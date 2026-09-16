# Mini-RAG: Production-Grade Asynchronous Retrieval-Augmented Generation Architecture

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Celery](https://img.shields.io/badge/Celery-Distributed_Task_Queue-37814A.svg?logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose_Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An asynchronous, provider-agnostic **Retrieval-Augmented Generation (RAG)** platform designed for document ingestion, tenant-isolated vector indexing, high-performance semantic retrieval, and factual, hallucination-resistant LLM answer synthesis.

Built with a modular backend architecture decoupling compute-heavy ingestion workflows (chunking, vectorization, transcription) from latency-sensitive API operations via distributed task queues.

---

## 🏛️ System Architecture

```
                                 [Client Application / REST API Consumer]
                                                    │
                                                    ▼
                     ┌─────────────────────────────────────────────────────────────┐
                     │                     FastAPI Gateway                         │
                     │  - Ingestion Endpoints (/data/upload/file, /upload/audio)   │
                     │  - Segmentation & Indexing (/data/process, /process-push)   │
                     │  - Dense Semantic Retrieval (/nlp/index/search/{project_id})│
                     │  - Grounded RAG Synthesis (/nlp/index/answer/{project_id})  │
                     └──────────────┬───────────────────────────────┬──────────────┘
                                    │                               │
                      Async Dispatch│                 Sync Retrieval│ Cosine Ranking
                                    ▼                               ▼
                     ┌──────────────────────────────┐ ┌────────────────────────────┐
                     │   Message Broker (RabbitMQ)  │ │ Vector Store Abstraction   │
                     └──────────────┬───────────────┘ │  ├── PGVector (PostgreSQL) │
                                    │ Task Queue      │  └── Qdrant (HNSW / REST)  │
                                    ▼                 └─────────────▲──────────────┘
                     ┌──────────────────────────────┐               │
                     │     Celery Distributed Fleet │               │
                     │  - Document Parsing/Cleaning ├───────────────┘ Batch Vector Insertion
                     │  - Overlapping Sliding Chunk │
                     │  - Embedding Vectorization   │
                     └──────────────┬───────────────┘
                                    │ State / Task Tracking
                                    ▼
                     ┌──────────────────────────────┐
                     │     Result Backend (Redis)   │
                     └──────────────────────────────┘

Relational & Telemetry Layer:
├── PostgreSQL + Alembic: Multi-tenant schemas (Projects, Asset Metadata, Document Chunks, Task Records)
├── Flower: Celery worker monitoring and real-time execution inspect
├── Prometheus & Grafana: Infrastructure metrics, request latency, and queue depths
└── Nginx: Secure reverse proxy and edge routing
```

---

## ⚡ Key Architectural Features

### 1. Multi-Provider Abstraction Layer (Factory Pattern)
Decouples core business logic from concrete third-party providers, preventing vendor lock-in and allowing zero-downtime provider switching via configuration:
- **Vector Stores (`VectordbFactory`)**: Interchangable support for **PostgreSQL (`pgvector`)** and **Qdrant** with unified interfaces for collection initialization, payload upsert, and metric-based search.
- **Embedding Models (`LLMFactory`)**: Supports local inference using **SentenceTransformers (`all-MiniLM-L6-v2`)** for zero-API-cost setups alongside cloud embeddings via **Cohere**.
- **LLM Generators**: Abstracted synthesis supporting **Grok (xAI)**, **Cohere**, and local model runtimes.
- **Audio & Translation**: Modular interfaces for **Whisper** audio transcription and **DeepL** cross-language document processing.

### 2. Multi-Tenant Project Isolation
All collections, document chunks, and embeddings are isolated dynamically at the storage and vector index layers:
- Dynamic collection naming: `collection_{dimension}_{project_id}`.
- Prevents cross-tenant context bleeding during vector similarity queries and context window synthesis.

### 3. Distributed Asynchronous Ingestion Pipeline
Heavy preprocessing and tensor transformations are offloaded to **Celery** workers backed by **RabbitMQ** and **Redis**:
- **Sliding-Window Chunking**: Configurable `chunk_size` and `chunk_overlap` segmentation with text normalization.
- **Batch Embedding**: Asynchronous batching to maximize hardware utilization and avoid API rate limits.
- **Idempotent Tasks**: Execution safety using persistent task state tracking to prevent duplicate embeddings.

### 4. Grounded Context-Injection & Anti-Hallucination Prompting
- High-precision cosine similarity thresholding to discard low-relevance passages.
- Multilingual prompt templates enforcing strict negative constraints: requires explicit grounding in retrieved context and prevents ungrounded model extrapolations.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **API Framework** | FastAPI, Pydantic, Uvicorn, Python 3.10+ |
| **Distributed Tasks** | Celery, RabbitMQ (Broker), Redis (Result Backend), Flower |
| **Vector Storage** | Qdrant, PostgreSQL (`pgvector`) |
| **Relational Database** | PostgreSQL, SQLAlchemy, Alembic (Migrations) |
| **Embeddings & NLP** | SentenceTransformers (`all-MiniLM-L6-v2`), Cohere Embeddings |
| **LLM Generation** | Cohere API, Grok / xAI |
| **Observability** | Prometheus, Grafana, Custom Metrics Middleware |
| **Containerization** | Docker, Docker Compose, Nginx |

---

## 📁 Repository Structure

```
.
├── src/
│   ├── controllers/         # Request handling, validation & business logic
│   │   ├── BaseControllers.py
│   │   ├── DataControllers.py
│   │   ├── NlpControllers.py
│   │   └── ProcessControllers.py
│   ├── models/              # SQLAlchemy models & schema definitions
│   │   ├── ProjectModel.py
│   │   ├── AssetModel.py
│   │   ├── ChunkModel.py
│   │   └── db_schemes/      # Alembic migration revisions
│   ├── routes/              # FastAPI APIRouter endpoints
│   │   ├── base.py          # Service health & version info
│   │   ├── data.py          # Asset ingestion & processing routes
│   │   └── nlp.py           # Vector search & RAG synthesis routes
│   ├── stores/              # Provider implementations & Factory contracts
│   │   ├── llm/             # LLM & Embedding provider implementations
│   │   │   ├── LLMFactory.py
│   │   │   ├── providers/   # MiniLM, Cohere, Grok
│   │   │   └── templates/   # Multi-language grounded RAG prompts
│   │   └── vectordb/        # Vector store providers (Qdrant, PGVector)
│   │       ├── VectordbFactory.py
│   │       └── providers/
│   ├── tasks/               # Celery task definitions & pipeline chains
│   │   ├── file_processing.py
│   │   └── data_indexing.py
│   ├── celery_app.py        # Celery instance configuration
│   ├── flowerconfig.py      # Flower dashboard configuration
│   └── main.py              # Application entrypoint & lifespan events
├── docker/                  # Multi-container orchestration & configs
│   ├── docker-compose.yaml  # API, Celery, Postgres, RabbitMQ, Redis, Qdrant
│   ├── Dockerfile
│   ├── prometheus.yml
│   └── nginx/
└── requirements.txt         # Production dependencies
```

---

## 🚀 Quick Start Guide

### Prerequisites
- [Docker Engine](https://docs.docker.com/engine/install/) & [Docker Compose](https://docs.docker.com/compose/)
- Python 3.10+ (if running locally outside Docker)

---

### Option A: Complete Docker Compose Deployment (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kerlosmelad12/Mini-RAG-Application.git
   cd Mini-RAG-Application
   ```

2. **Configure Environment Variables:**
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` to supply your API credentials (e.g., `COHERE_API_KEY`, `POSTGRES_PASSWORD`, etc.).*

3. **Start all services:**
   ```bash
   docker compose -f docker/docker-compose.yaml up -d --build
   ```

4. **Verify Service Health:**
   - **FastAPI Core Service:** `http://localhost:5000/MiniRAG-V1/`
   - **Interactive API Docs (Swagger):** `http://localhost:5000/docs`
   - **Flower Task Dashboard:** `http://localhost:5555`
   - **Qdrant Dashboard:** `http://localhost:6333/dashboard`

---

### Option B: Local Development Setup

1. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install core dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

4. **Start the Celery worker fleet:**
   ```bash
   celery -A src.celery_app worker --loglevel=info --concurrency=4
   ```

5. **Start the FastAPI server:**
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 5000 --reload
   ```

---

## 📡 REST API Reference

### 1. Document Ingestion
Upload files (`.pdf`, `.txt`, `.json`, `.csv`, `.docx`) or audio assets associated with a target `project_id`.

```http
POST /MiniRAG-V1/data/upload/file/{project_id}
Content-Type: multipart/form-data

file: <binary>
```

### 2. Document Chunking & Preprocessing
Triggers asynchronous sliding-window segmentation and normalizes text units.

```http
POST /MiniRAG-V1/data/process/{project_id}
Content-Type: application/json

{
  "file_id": "8f3b2d1c-...",
  "chunk_size": 600,
  "chunk_overlap": 50,
  "do_reset": false
}
```

### 3. Asynchronous Vector Indexing
Pushes pending processed chunks into the designated vector store collection.

```http
POST /MiniRAG-V1/nlp/index/push/{project_id}
Content-Type: application/json

{
  "do_reset": false
}
```

### 4. Semantic Similarity Search
Executes dense vector search using cosine distance over project-isolated collections.

```http
POST /MiniRAG-V1/nlp/index/search/{project_id}
Content-Type: application/json

{
  "text": "How does vector indexing prevent LLM hallucination?",
  "limit": 5
}
```

### 5. Grounded RAG Question-Answering
Retrieves top-$k$ contextual chunks, injects them into defensive prompt scaffolds, and synthesizes answers.

```http
POST /MiniRAG-V1/nlp/index/answer/{project_id}
Content-Type: application/json

{
  "text": "What is the token overlap configuration used in this project?",
  "limit": 5
}
```

---

## ⚙️ Configuration (.env)

| Variable | Description | Default |
| :--- | :--- | :--- |
| `APP_NAME` | Service identifier | `MiniRAG-V1` |
| `APP_PORT` | Port for the Uvicorn/FastAPI server | `5000` |
| `POSTGRES_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/minirag` |
| `VECTOR_DB_BACKEND` | Active vector store (`QDRANT` or `PGVECTOR`) | `QDRANT` |
| `QDRANT_HOST` | Host address for Qdrant instance | `http://localhost:6333` |
| `EMBEDDING_PROVIDER` | Embedding engine (`MINILM` or `COHERE`) | `MINILM` |
| `GENERATION_PROVIDER`| Primary text generation engine | `COHERE` |
| `CELERY_BROKER_URL` | Message broker URL | `amqp://guest:guest@localhost:5672//` |
| `CELERY_RESULT_BACKEND`| Task state storage URL | `redis://localhost:6379/0` |
| `COHERE_API_KEY` | API Key for Cohere embeddings/synthesis | `optional` |
| `GROK_API_KEY` | API Key for xAI Grok provider | `optional` |

---

## 🛡️ Reliability, Observability & Scaling

- **Resilience**: Task failures during parsing or embedding are trapped with detailed tracebacks stored in the relational database without terminating the worker daemon.
- **Resource Protection**: Embedding and file processing are bound by concurrency limits configured in Celery, preventing memory exhaustion when handling large documents.
- **Telemetry**: Prometheus scraping target exposes queue latencies, active tasks, and API throughput metrics.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
