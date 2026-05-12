# Módulo para configurar los embeddings de Google Generative AI
# Utiliza el modelo embedding-001 para convertir texto en vectores

import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Retorna una instancia configurada de GoogleGenerativeAIEmbeddings."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY no encontrada. "
            "Asegúrate de configurarla en el archivo .env"
        )

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=api_key,
    )
    return embeddings
