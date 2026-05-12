# Módulo de evaluación del pipeline RAG con RAGAS
# Mide faithfulness, answer_relevancy, context_precision y context_recall

import os
from typing import Any, Dict, List

from datasets import Dataset
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from ragas import evaluate
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    answer_relevancy,
    context_precision,
    context_recall,
    faithfulness,
)


def evaluate_rag(
    question: str,
    answer: str,
    contexts: List[str],
    ground_truth: str,
) -> Dict[str, Any]:
    """
    Evalúa el pipeline RAG usando las métricas estándar de RAGAS.

    Parámetros:
        question    : La pregunta original del usuario.
        answer      : La respuesta generada por el agente.
        contexts    : Lista de fragmentos recuperados por el retriever.
        ground_truth: Respuesta de referencia para calcular recall y precision.

    Retorna:
        Diccionario con los scores de cada métrica.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY no encontrada para la evaluación RAGAS.")

    # Construir el dataset en el formato que RAGAS espera
    data = {
        "question": [question],
        "answer": [answer],
        "contexts": [contexts],
        "ground_truth": [ground_truth],
    }
    dataset = Dataset.from_dict(data)

    # Configurar LLM evaluador envuelto para RAGAS
    evaluator_llm = LangchainLLMWrapper(
        ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=api_key,
        )
    )

    # Configurar embeddings evaluador envuelto para RAGAS
    evaluator_embeddings = LangchainEmbeddingsWrapper(
        GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=api_key,
        )
    )

    metricas = [faithfulness, answer_relevancy, context_precision, context_recall]

    try:
        print("\n[RAGAS] Iniciando evaluación del pipeline RAG...")
        resultado = evaluate(
            dataset=dataset,
            metrics=metricas,
            llm=evaluator_llm,
            embeddings=evaluator_embeddings,
        )

        # Mostrar resultados como tabla en consola
        print("\n" + "=" * 50)
        print("         SCORES DE EVALUACIÓN RAGAS")
        print("=" * 50)
        scores = resultado.to_pandas().iloc[0]
        for metrica in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
            valor = scores.get(metrica, "N/A")
            if isinstance(valor, float):
                print(f"  {metrica:<22}: {valor:.4f}")
            else:
                print(f"  {metrica:<22}: {valor}")
        print("=" * 50 + "\n")

        return resultado

    except Exception as e:
        print(f"[RAGAS] Error durante la evaluación: {e}")
        raise
