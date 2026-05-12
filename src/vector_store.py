# Módulo para gestionar el vector store con ChromaDB a través de LangChain
# Persiste los embeddings en disco para evitar re-insertar documentos duplicados

import os
import shutil
from typing import List

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "vectoagent_docs")


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def init_vectorstore(
    documents: List[Document],
    embeddings: Embeddings,
) -> Chroma:
    """
    Inicializa o carga el vector store de Chroma.

    Si ya existe la base de datos persistida, la carga sin re-insertar documentos.
    Si no existe, crea la colección e inserta los documentos proporcionados.
    """
    try:
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", PERSIST_DIR)
        collection_name = os.getenv("CHROMA_COLLECTION", COLLECTION_NAME)
        reset_on_start = _env_bool("CHROMA_RESET_ON_START", default=False)

        if reset_on_start and os.path.exists(persist_dir):
            print(f"[VectorStore] Eliminando base persistida en '{persist_dir}' (CHROMA_RESET_ON_START=true)...")
            shutil.rmtree(persist_dir, ignore_errors=True)

        # Verificar si ya existe la base de datos persistida con datos
        if os.path.exists(persist_dir) and os.listdir(persist_dir):
            print(f"[VectorStore] Cargando base de datos existente desde '{persist_dir}'...")
            vectorstore = Chroma(
                collection_name=collection_name,
                persist_directory=persist_dir,
                embedding_function=embeddings,
            )
            # Confirmar que realmente tiene documentos
            docs = vectorstore.get()
            count = len(docs.get("ids", []))
            if count > 0:
                print(f"[VectorStore] Base de datos cargada con {count} documentos.")
                return vectorstore
            print("[VectorStore] La base de datos existe pero está vacía. Insertando documentos...")

        # Crear nueva colección e insertar documentos
        print(
            f"[VectorStore] Creando nueva base de datos en '{persist_dir}' "
            f"(collection='{collection_name}')..."
        )
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            collection_name=collection_name,
            persist_directory=persist_dir,
        )
        print(f"[VectorStore] {len(documents)} documentos insertados correctamente.")
        return vectorstore

    except Exception as e:
        raise RuntimeError(f"Error al inicializar ChromaDB: {e}") from e


def get_retriever(vectorstore: Chroma, k: int = 3):
    """
    Retorna un retriever configurado para recuperar los k documentos más relevantes.
    """
    return vectorstore.as_retriever(search_kwargs={"k": k})
