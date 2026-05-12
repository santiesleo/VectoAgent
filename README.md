# VectoAgent — Agente ReAct con RAG

Implementación de un agente ReAct (Reasoning + Acting) con RAG (Retrieval-Augmented Generation)
usando LangChain, Gemini 2.5 Flash y ChromaDB como vector store.

---

## Arquitectura

```
Usuario → Pregunta → [Embedding] → ChromaDB → Contexto
                                                   ↓
                                          Agente ReAct (Gemini)
                                                   ↓
                                             Respuesta Final
                                                   ↓
                                     LangSmith (trazas) + RAGAS (scores)
```

**Flujo detallado:**

1. La pregunta del usuario se convierte en un vector con `embedding-001`
2. ChromaDB busca los `k=3` fragmentos más similares semánticamente
3. El agente ReAct recibe la pregunta, razona y decide usar la herramienta de búsqueda
4. Gemini 2.5 Flash genera la respuesta final usando el contexto recuperado
5. LangSmith registra las trazas automáticamente
6. RAGAS evalúa la calidad del pipeline con 4 métricas

---

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| LLM | Gemini 2.5 Flash (`gemini-2.5-flash`) |
| Embeddings | Google `embedding-001` |
| Vector Store | ChromaDB (persistido en `./chroma_db`) |
| Framework | LangChain 0.3+ |
| Trazabilidad | LangSmith |
| Evaluación | RAGAS |

---

## Obtener las API Keys (ambas son gratuitas)

### GOOGLE_API_KEY

1. Ve a [https://aistudio.google.com](https://aistudio.google.com)
2. Inicia sesión con tu cuenta de Google
3. Haz clic en **"Get API Key"** → **"Create API key"**
4. Copia la clave generada

### LANGCHAIN_API_KEY

1. Ve a [https://smith.langchain.com](https://smith.langchain.com)
2. Crea una cuenta gratuita (puedes usar GitHub o Google)
3. Ve a **Settings → API Keys → Create API Key**
4. Copia la clave generada

---

## Instalación

```bash
# 1. Clonar o descargar el proyecto
cd VectoAgent

# 2. (Recomendado) Crear entorno virtual
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## Configuración

```bash
# Copiar el archivo de variables de entorno
cp .env.example .env

# Editar .env y completar las API keys
nano .env   # o usa tu editor preferido
```

El archivo `.env` debe quedar así:

```env
GOOGLE_API_KEY=AIza...tu_clave_aquí
LANGCHAIN_API_KEY=lsv2_...tu_clave_aquí
LANGCHAIN_PROJECT=VectoAgent
LANGCHAIN_TRACING_V2=true
```

---

## Ejecución

```bash
python main.py
```

---

## Qué esperar al ejecutar

### 1. Inicialización
```
[1/4] Inicializando embeddings de Google Generative AI...
[2/4] Inicializando vector store (ChromaDB)...
[VectorStore] Creando nueva base de datos en './chroma_db'...
[VectorStore] 11 documentos insertados correctamente.
[3/4] Construyendo agente ReAct con Gemini 2.5 Flash...
```

### 2. Verbose del agente ReAct
El agente imprime su proceso de razonamiento (Thought → Action → Observation):
```
> Entering new AgentExecutor chain...
Thought: Necesito buscar información sobre Simón Bolívar en la base de conocimiento.
Action: buscar_en_base_de_conocimiento
Action Input: Simón Bolívar
Observation: [fragmentos recuperados de ChromaDB]
Thought: Con esta información puedo responder...
Final Answer: Simón Bolívar fue...
```

### 3. Scores de RAGAS
```
==================================================
         SCORES DE EVALUACIÓN RAGAS
==================================================
  faithfulness          : 0.9500
  answer_relevancy      : 0.9200
  context_precision     : 0.8800
  context_recall        : 0.9100
==================================================
```

### 4. Trazas en LangSmith
Ve a [https://smith.langchain.com](https://smith.langchain.com) → proyecto **VectoAgent**
para ver el detalle completo de cada ejecución: tokens usados, latencia por paso, inputs/outputs.

---

## Estructura del proyecto

```
VectoAgent/
├── .env.example            # Plantilla de variables de entorno
├── requirements.txt        # Dependencias Python
├── README.md               # Este archivo
├── main.py                 # Punto de entrada
├── data/
│   └── knowledge_base.py   # Documentos LangChain hardcodeados
├── src/
│   ├── embeddings.py       # GoogleGenerativeAIEmbeddings
│   ├── vector_store.py     # ChromaDB via LangChain
│   ├── agent.py            # Agente ReAct con LangChain
│   └── evaluation.py       # Evaluación con RAGAS
└── chroma_db/              # Base de datos vectorial (generada automáticamente)
```

---

## Métricas RAGAS explicadas

| Métrica | Qué mide |
|---|---|
| **faithfulness** | ¿La respuesta está soportada por el contexto recuperado? |
| **answer_relevancy** | ¿La respuesta es relevante para la pregunta? |
| **context_precision** | ¿Los fragmentos recuperados son precisos para la pregunta? |
| **context_recall** | ¿El contexto recuperado cubre lo necesario para responder? |

Todas las métricas tienen rango `[0, 1]`, donde `1` es el mejor valor posible.
