# VectoAgent

Agente ReAct con RAG (Retrieval-Augmented Generation) para la Copa Mundial FIFA 2026. Responde preguntas en lenguaje natural buscando en una base de conocimiento vectorial y, opcionalmente, crea eventos en Google Calendar a través de integración MCP.

---

## Arquitectura

```
                         ┌─────────────────────────────────────────────────────┐
                         │                  VectoAgent                         │
                         │                                                     │
  Pregunta del  ──────►  │  Embedding (gemini-embedding-001)                   │
  usuario               │       │                                              │
                         │       ▼                                              │
                         │  ChromaDB ──► Recupera k fragmentos relevantes      │
                         │       │                                              │
                         │       ▼                                              │
                         │  Agente ReAct (Gemini 2.5 Flash / LangGraph)        │
                         │       │                                              │
                         │       ├─► buscar_en_base_de_conocimiento (RAG)      │
                         │       │                                              │
                         │       └─► MCP Google Calendar (opcional)            │
                         │              ├─► crear_evento_calendario            │
                         │              ├─► listar_eventos_calendario          │
                         │              └─► eliminar_evento_calendario         │
                         │                                                     │
  Respuesta     ◄──────  │  Respuesta final + evaluación RAGAS (modo CLI)      │
                         └─────────────────────────────────────────────────────┘
```

---

## Stack tecnológico

| Componente     | Tecnología                                      |
|----------------|-------------------------------------------------|
| LLM            | Gemini 2.5 Flash (`gemini-2.5-flash`)           |
| Embeddings     | Google `models/gemini-embedding-001` (3072 dim) |
| Vector store   | ChromaDB con persistencia local                 |
| Framework      | LangChain 1.x + LangGraph (`create_agent`)      |
| UI chat        | Streamlit                                       |
| Evaluación RAG | RAGAS (faithfulness, relevancy, precision/recall)|
| Trazabilidad   | LangSmith                                       |
| Calendario     | Google Calendar API vía MCP (stdio)             |

---

## Pipeline paso a paso

```
1. Carga de documentos
   data/markdown/*.md
        │
        ▼
2. Chunking
   RecursiveCharacterTextSplitter
   (CHUNK_SIZE=700, CHUNK_OVERLAP=120)
        │
        ▼
3. Embeddings + indexado
   gemini-embedding-001 → ChromaDB (persistente en ./chroma_db)
   (idempotente: si la colección ya existe, no re-inserta)
        │
        ▼
4. Retriever
   Búsqueda por similitud, devuelve RETRIEVER_K fragmentos
        │
        ▼
5. Agente ReAct (LangGraph)
   Gemini 2.5 Flash recibe la pregunta + decide qué herramienta usar:
     - buscar_en_base_de_conocimiento  → siempre primero
     - crear/listar/eliminar_evento    → si MCP_GCAL_ENABLED=true
        │
        ▼
6. Evaluación RAGAS (solo modo CLI, main.py)
   Ground truth generado automáticamente con el LLM
   Métricas: faithfulness, answer_relevancy,
             context_precision, context_recall
```

---

## Estructura del proyecto

```
VectoAgent/
├── app.py                       # Chat UI con Streamlit
├── main.py                      # Modo CLI con evaluación RAGAS
├── mcp_google_calendar_server.py# Servidor MCP (FastMCP) para Google Calendar
├── setup_oauth.py               # Script único para autorizar Google Calendar
├── requirements.txt
├── .env.example                 # Plantilla de configuración
├── data/
│   ├── knowledge_base.py        # Loader de Markdown + chunking
│   └── markdown/
│       └── info_mundial.md      # Base de conocimiento: Copa Mundial 2026
├── src/
│   ├── pipeline.py              # build_runtime(): inicializa todo el stack
│   ├── agent.py                 # build_agent() + invoke_agent()
│   ├── embeddings.py            # get_embeddings() con gemini-embedding-001
│   ├── vector_store.py          # init_vectorstore() idempotente + get_retriever()
│   ├── evaluation.py            # evaluate_rag() con RAGAS
│   └── mcp_client.py            # MCPClientManager + LangChain tools wrapper
└── .secrets/
    └── google_token.json        # Token OAuth (generado por setup_oauth.py, NO commitear)
```

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/santiesleo/VectoAgent.git
cd VectoAgent

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## Configuración de credenciales

### 1. Google API Key (Gemini — LLM y embeddings)

1. Entra a [https://aistudio.google.com](https://aistudio.google.com)
2. Ve a **Get API key → Create API key**
3. Copia la clave y pégala en `.env` como `GOOGLE_API_KEY`

> El plan gratuito de Gemini 2.5 Flash tiene un límite de 20 solicitudes/día.
> Para uso intensivo, activa facturación en Google Cloud y usa `gemini-2.0-flash`.

---

### 2. LangSmith (trazabilidad — opcional pero recomendado)

1. Crea cuenta en [https://smith.langchain.com](https://smith.langchain.com)
2. Ve a **Settings → API Keys → Create API Key**
3. Copia la clave y completa en `.env`:

```env
LANGCHAIN_API_KEY=tu_langchain_api_key
LANGCHAIN_PROJECT=VectoAgent
LANGCHAIN_TRACING_V2=true
```

Si no quieres trazabilidad, deja `LANGCHAIN_TRACING_V2=false`.

---

### 3. Google Calendar vía MCP (opcional)

La integración con Google Calendar requiere tres pasos: habilitar la API, crear credenciales OAuth y ejecutar el flujo de autorización una única vez.

#### 3.1 Habilitar Google Calendar API

1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. Selecciona o crea un proyecto
3. Navega a **APIs y servicios → Biblioteca**
4. Busca **Google Calendar API** y haz clic en **Habilitar**

#### 3.2 Crear credenciales OAuth 2.0

1. Ve a **APIs y servicios → Credenciales → Crear credenciales → ID de cliente OAuth**
2. Tipo de aplicación: **Aplicación de escritorio**
3. Nombre: cualquiera (ej: `VectoAgent`)
4. Clic en **Crear**
5. Copia el **Client ID** y **Client Secret** que aparecen

> **Importante:** usa tipo "Aplicación de escritorio" (`installed`), no "Aplicación web".
> Los redirect URIs `http://localhost` y `http://localhost:8080` deben estar registrados.

6. Agrega en `.env`:

```env
GOOGLE_OAUTH_CLIENT_ID=tu_client_id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=tu_client_secret
GOOGLE_OAUTH_TOKEN_PATH=./.secrets/google_token.json
```

#### 3.3 Autorizar la aplicación (una sola vez)

```bash
python setup_oauth.py
```

Esto abrirá el navegador, pedirá que autorices el acceso a Google Calendar y guardará el token en `.secrets/google_token.json`. Solo hay que hacerlo una vez; el token se refresca automáticamente.

#### 3.4 Habilitar el MCP en `.env`

```env
MCP_GCAL_ENABLED=true
MCP_GCAL_COMMAND=python
MCP_GCAL_ARGS=
MCP_GCAL_SCRIPT=mcp_google_calendar_server.py
```

---

## Variables de entorno

Copia `.env.example` a `.env` y completa los valores. **Nunca subas `.env` al repositorio.**

```bash
cp .env.example .env
```

| Variable               | Descripción                                          | Requerida |
|------------------------|------------------------------------------------------|-----------|
| `GOOGLE_API_KEY`       | Clave de Google AI Studio para Gemini                | Sí        |
| `GOOGLE_OAUTH_CLIENT_ID` | Client ID OAuth para Google Calendar              | Solo MCP  |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Client Secret OAuth                          | Solo MCP  |
| `GOOGLE_OAUTH_TOKEN_PATH` | Ruta donde guardar el token OAuth               | Solo MCP  |
| `LANGCHAIN_API_KEY`    | Clave de LangSmith para trazabilidad                 | No        |
| `LANGCHAIN_PROJECT`    | Nombre del proyecto en LangSmith                     | No        |
| `LANGCHAIN_TRACING_V2` | Activar trazas (`true` / `false`)                    | No        |
| `KNOWLEDGE_BASE_DIR`   | Directorio de archivos Markdown (`data/markdown`)    | No        |
| `KNOWLEDGE_BASE_GLOB`  | Patrón de archivos (`**/*.md`)                       | No        |
| `CHUNK_SIZE`           | Tamaño de fragmento en caracteres (default: 700)     | No        |
| `CHUNK_OVERLAP`        | Solapamiento entre fragmentos (default: 120)         | No        |
| `RETRIEVER_K`          | Fragmentos recuperados por consulta (default: 3)     | No        |
| `CHROMA_PERSIST_DIR`   | Directorio de persistencia de ChromaDB               | No        |
| `CHROMA_COLLECTION`    | Nombre de la colección en ChromaDB                   | No        |
| `CHROMA_RESET_ON_START`| Reconstruir la colección al iniciar (`true`/`false`) | No        |
| `MCP_GCAL_ENABLED`     | Activar integración Google Calendar (`true`/`false`) | No        |
| `MCP_GCAL_COMMAND`     | Comando para ejecutar el server MCP (`python`)       | No        |
| `MCP_GCAL_ARGS`        | Argumentos extra al comando (separados por coma)     | No        |
| `MCP_GCAL_SCRIPT`      | Ruta al script del servidor MCP                      | No        |

---

## Ejecución

### Modo CLI (con evaluación RAGAS)

```bash
python main.py
```

Inicia el pipeline completo, permite escribir una pregunta libre y al final evalúa la respuesta con RAGAS mostrando las métricas en consola y en LangSmith.

### Modo UI (Streamlit)

```bash
streamlit run app.py
```

Abre un chat en el navegador en `http://localhost:8501`. El panel lateral muestra la configuración activa y permite limpiar el historial. Cada respuesta incluye un desplegable con los fragmentos recuperados de ChromaDB.

---

## Extender la base de conocimiento

Agrega archivos `.md` en `data/markdown/`. Al reiniciar la app, los nuevos documentos se indexan automáticamente.

Para reconstruir la colección desde cero (útil si cambias la estructura de los docs):

```env
CHROMA_RESET_ON_START=true
```

Vuelve a `false` después del primer arranque para no re-indexar en cada inicio.

---

## Cómo funciona el MCP de Google Calendar

El agente se comunica con el servidor MCP a través de **stdio** usando el Model Context Protocol. El flujo es:

```
app.py / main.py
    │
    └─► MCPClientManager (src/mcp_client.py)
            │  (event loop dedicado en hilo de fondo)
            │
            └─► mcp_google_calendar_server.py  (FastMCP)
                    │
                    └─► Google Calendar API  (OAuth2)
```

Cuando el usuario pide agregar un partido al calendario, el agente:
1. Usa `buscar_en_base_de_conocimiento` para obtener fecha, hora y sede del partido.
2. Llama a `crear_evento_calendario` con los datos recuperados — sin pedirle nada al usuario.

Las herramientas disponibles son:

| Herramienta LangChain        | Tool MCP          | Descripción                          |
|------------------------------|-------------------|--------------------------------------|
| `crear_evento_calendario`    | `crear_evento`    | Crea un evento en Google Calendar    |
| `listar_eventos_calendario`  | `listar_eventos`  | Lista los próximos eventos           |
| `eliminar_evento_calendario` | `eliminar_evento` | Elimina un evento por su ID          |

---

## Evaluación RAGAS

El modo CLI evalúa cada respuesta con cuatro métricas:

| Métrica              | Qué mide                                                    |
|----------------------|-------------------------------------------------------------|
| `faithfulness`       | Si la respuesta está sustentada en los fragmentos recuperados|
| `answer_relevancy`   | Qué tan relevante es la respuesta para la pregunta          |
| `context_precision`  | Precisión de los fragmentos recuperados                     |
| `context_recall`     | Cobertura de los fragmentos respecto al ground truth        |

El ground truth se genera automáticamente con el LLM a partir de los contextos recuperados, por lo que no se necesita un dataset curado de antemano.

Los resultados también quedan guardados en LangSmith si `LANGCHAIN_TRACING_V2=true`.
