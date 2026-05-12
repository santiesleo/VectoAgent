# Módulo para gestionar el vector store con ChromaDB a través de LangChain
# Persiste los embeddings en disco para evitar re-insertar documentos duplicados

import os
from typing import List

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

PERSIST_DIR = "./chroma_db"


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
        # Verificar si ya existe la base de datos persistida con datos
        if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
            print(f"[VectorStore] Cargando base de datos existente desde '{PERSIST_DIR}'...")
            vectorstore = Chroma(
                persist_directory=PERSIST_DIR,
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
        print(f"[VectorStore] Creando nueva base de datos en '{PERSIST_DIR}'...")
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=PERSIST_DIR,
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
