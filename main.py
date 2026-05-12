# Punto de entrada principal del agente ReAct con RAG
# Ejecuta el pipeline completo: embeddings → vector store → agente → evaluación RAGAS

import os

from dotenv import load_dotenv

# Cargar variables de entorno ANTES de importar cualquier módulo que las necesite
load_dotenv()

from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.agent import invoke_agent
from src.evaluation import evaluate_rag
from src.pipeline import build_runtime


def generate_ground_truth(question: str, contexts: list[str]) -> str:
    """Genera un ground truth de referencia usando el LLM a partir de los contextos recuperados."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )
    contexto_unido = "\n\n".join(contexts)
    prompt = (
        f"Basándote únicamente en los siguientes fragmentos de texto, "
        f"escribe una respuesta de referencia concisa y completa para la pregunta: '{question}'\n\n"
        f"Fragmentos:\n{contexto_unido}\n\n"
        f"Respuesta de referencia:"
    )
    result = llm.invoke([HumanMessage(content=prompt)])
    content = result.content
    if isinstance(content, list):
        return " ".join(
            b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"
        ).strip()
    return str(content).strip()


def main():
    print("\n" + "=" * 60)
    print("       VectoAgent — Agente ReAct con RAG")
    print("=" * 60 + "\n")

    # ── 1-3. Inicializar pipeline ──────────────────────────────────────────
    print("[1/4] Inicializando pipeline (embeddings + vector store + agente)...")
    try:
        agent_executor, retriever = build_runtime()
    except Exception as e:
        print(f"ERROR al inicializar pipeline: {e}")
        return

    # ── Pregunta libre del usuario ─────────────────────────────────────────
    print(f"\n{'─' * 60}")
    print("Puedes preguntar sobre cualquier tema disponible en la base de conocimiento.")
    print(f"{'─' * 60}")
    question = input("Tu pregunta: ").strip()
    if not question:
        print("No ingresaste ninguna pregunta. Saliendo.")
        return
    print(f"{'─' * 60}\n")

    try:
        respuesta = invoke_agent(agent_executor, question)
    except Exception as e:
        print(f"ERROR durante la invocación del agente: {e}")
        return

    print(f"\n{'─' * 60}")
    print("Respuesta final del agente:")
    print(f"{'─' * 60}")
    print(respuesta)

    # ── 4. Evaluar con RAGAS ───────────────────────────────────────────────
    print(f"\n[4/4] Evaluando con RAGAS...")

    try:
        retrieved_docs = retriever.invoke(question)
        contexts = [doc.page_content for doc in retrieved_docs]
    except Exception as e:
        print(f"ERROR al recuperar documentos para evaluación: {e}")
        return

    # Generar ground truth dinámico a partir de los contextos recuperados
    try:
        print("[RAGAS] Generando ground truth automático...")
        ground_truth = generate_ground_truth(question, contexts)
    except Exception as e:
        print(f"ERROR al generar ground truth: {e}")
        return

    try:
        evaluate_rag(
            question=question,
            answer=respuesta,
            contexts=contexts,
            ground_truth=ground_truth,
        )
    except Exception as e:
        print(f"ERROR durante la evaluación RAGAS: {e}")

    print("\n✓ Pipeline completado. Revisa las trazas en https://smith.langchain.com\n")


if __name__ == "__main__":
    main()
