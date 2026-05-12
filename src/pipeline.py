"""Utilidades para inicializar el pipeline RAG con configuracion por entorno."""

import os
from typing import Tuple

from src.agent import build_agent
from src.embeddings import get_embeddings
from src.vector_store import get_retriever, init_vectorstore
from data.knowledge_base import DOCUMENTS


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def get_retriever_k() -> int:
    return _env_int("RETRIEVER_K", 3)


def build_runtime() -> Tuple[object, object]:
    """Inicializa embeddings, vector store, retriever y agente."""
    embeddings = get_embeddings()
    vectorstore = init_vectorstore(DOCUMENTS, embeddings)
    retriever = get_retriever(vectorstore, k=get_retriever_k())
    agent_executor = build_agent(retriever)
    return agent_executor, retriever
