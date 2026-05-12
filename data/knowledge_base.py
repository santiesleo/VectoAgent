"""Carga la base de conocimiento desde archivos Markdown y la fragmenta para RAG."""

import os
from pathlib import Path
from typing import List

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

DEFAULT_KB_DIR = "data/markdown"
DEFAULT_GLOB = "**/*.md"
DEFAULT_CHUNK_SIZE = 700
DEFAULT_CHUNK_OVERLAP = 120


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def load_markdown_documents() -> List[Document]:
    """Carga documentos markdown y los parte en chunks configurables por entorno."""
    kb_dir = os.getenv("KNOWLEDGE_BASE_DIR", DEFAULT_KB_DIR)
    kb_glob = os.getenv("KNOWLEDGE_BASE_GLOB", DEFAULT_GLOB)
    chunk_size = _env_int("CHUNK_SIZE", DEFAULT_CHUNK_SIZE)
    chunk_overlap = _env_int("CHUNK_OVERLAP", DEFAULT_CHUNK_OVERLAP)

    base_path = Path(kb_dir)
    if not base_path.exists():
        raise FileNotFoundError(
            f"No se encontro el directorio de conocimiento: '{kb_dir}'. "
            "Configuralo en KNOWLEDGE_BASE_DIR."
        )

    loader = DirectoryLoader(
        str(base_path),
        glob=kb_glob,
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True,
        use_multithreading=True,
    )
    raw_docs = loader.load()
    if not raw_docs:
        raise ValueError(
            f"No se encontraron archivos markdown en '{kb_dir}' con glob '{kb_glob}'."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n# ", "\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(raw_docs)

    print(
        "[KnowledgeBase] "
        f"{len(raw_docs)} archivos markdown cargados y {len(chunks)} chunks generados "
        f"(chunk_size={chunk_size}, chunk_overlap={chunk_overlap})."
    )
    return chunks


DOCUMENTS = load_markdown_documents()
