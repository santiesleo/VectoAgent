# Punto de entrada principal del agente ReAct con RAG
# Ejecuta el pipeline completo: embeddings → vector store → agente → evaluación RAGAS

from dotenv import load_dotenv

# Cargar variables de entorno ANTES de importar cualquier módulo que las necesite
load_dotenv()

from data.knowledge_base import DOCUMENTS
from src.agent import build_agent, invoke_agent
from src.embeddings import get_embeddings
from src.evaluation import evaluate_rag
from src.vector_store import get_retriever, init_vectorstore


def main():
    print("\n" + "=" * 60)
    print("       VectoAgent — Agente ReAct con RAG")
    print("=" * 60 + "\n")

    # ── 1. Inicializar embeddings ──────────────────────────────────────────
    print("[1/4] Inicializando embeddings de Google Generative AI...")
    try:
        embeddings = get_embeddings()
    except Exception as e:
        print(f"ERROR al inicializar embeddings: {e}")
        return

    # ── 2. Inicializar vector store ────────────────────────────────────────
    print("[2/4] Inicializando vector store (ChromaDB)...")
    try:
        vectorstore = init_vectorstore(DOCUMENTS, embeddings)
        retriever = get_retriever(vectorstore, k=3)
    except Exception as e:
        print(f"ERROR al inicializar ChromaDB: {e}")
        return

    # ── 3. Construir y ejecutar el agente ──────────────────────────────────
    print("[3/4] Construyendo agente ReAct con Gemini 2.5 Flash...")
    try:
        agent_executor = build_agent(retriever)
    except Exception as e:
        print(f"ERROR al construir el agente: {e}")
        return

    question = "¿Quién es Simón Bolívar?"

    print(f"\n{'─' * 60}")
    print(f"Pregunta: {question}")
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

    # Recuperar los documentos que usó el retriever para esta pregunta
    try:
        retrieved_docs = retriever.invoke(question)
        contexts = [doc.page_content for doc in retrieved_docs]
    except Exception as e:
        print(f"ERROR al recuperar documentos para evaluación: {e}")
        return

    # Respuesta de referencia (ground truth) para las métricas de RAGAS
    ground_truth = (
        "Simón Bolívar fue un militar y político venezolano nacido en Caracas en 1783. "
        "Es conocido como 'El Libertador' por liderar la independencia de Venezuela, "
        "Colombia, Ecuador, Perú y Bolivia del dominio español. Fundó la República de "
        "Gran Colombia en 1819 y murió en Santa Marta, Colombia, el 17 de diciembre de 1830."
    )

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
