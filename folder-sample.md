ai-chatbot/
│
├── backend/                     # FastAPI-based backend
│   ├── app/
│   │   ├── api/                 # API route definitions (chat, ingest, search, etc.)
│   │   ├── core/                # Core configuration & dependency injection
│   │   ├── services/            # Business logic (embedding, retrieval, RAG, etc.)
│   │   ├── models/              # Pydantic models (request/response schemas)
│   │   ├── utils/               # Helper utilities (text splitter, cleaner, etc.)
│   │   ├── main.py              # FastAPI entry point
│   │   └── __init__.py
│   │
│   ├── tests/                   # Unit & integration tests for backend
│   └── requirements.txt         # Backend dependencies
│
├── frontend/                    # ReactJS (Vite/NextJS) for UI
│   ├── src/
│   │   ├── components/          # UI components (ChatBox, Sidebar, Loader, etc.)
│   │   ├── pages/               # Page-level components (Home, Admin, Docs)
│   │   ├── hooks/               # Custom React hooks (useChat, useSearch, etc.)
│   │   ├── services/            # API call definitions (Axios/Fetch to backend)
│   │   ├── store/               # State management (Zustand/Recoil)
│   │   ├── utils/               # UI helper (formatting, markdown render)
│   │   └── index.tsx
│   └── package.json
│
├── data/                        # Knowledge base data & processing
│   ├── docs/                    # Markdown docs or raw text files to ingest
│   │   ├── 01_ONBOARDING_GUIDE.md
│   │   ├── 02_BUSINESS_OVERVIEW.md
│   │   └── ...
│   ├── processed/               # Chunked + cleaned text after preprocessing
│   ├── embeddings/              # Local cache for embeddings before pushing to Pinecone
│   └── metadata/                # Metadata JSON (doc_id, chunk_id, source, etc.)
│
├── pipelines/                   # Data ingestion & chunking pipelines
│   ├── chunking/
│   │   ├── hybrid_recursive_splitter.py  # “Hybrid Recursive + Sentence Window” logic
│   │   └── __init__.py
│   ├── embedding/
│   │   ├── embedder_pinecone.py          # Convert text chunks -> vector embeddings
│   │   └── __init__.py
│   ├── ingestion_pipeline.py             # Full pipeline: clean → chunk → embed → upload
│   ├── retriever_pipeline.py             # Retrieve + rerank chunks from Pinecone
│   └── utils/                            # Shared helpers (token counter, text cleaner)
│
├── configs/
│   ├── settings.yaml            # Global config (API keys, Pinecone index, model IDs)
│   ├── logging.yaml             # Logging configuration
│   └── env.example              # Environment variable template (.env)
│
├── scripts/                     # Automation & ops scripts
│   ├── ingest_docs.sh           # CLI to ingest new docs
│   ├── run_dev.sh               # Run backend + frontend locally
│   └── sync_pinecone.py         # Re-sync embeddings to Pinecone
│
├── notebooks/                   # Jupyter notebooks for data analysis / embedding testing
│   ├── test_chunking.ipynb
│   ├── test_semantic_search.ipynb
│   └── rag_experiments.ipynb
│
├── docker-compose.yml           # Containerize backend, frontend, and services
├── Dockerfile                   # Backend Dockerfile
├── README.md                    # Project overview
└── .env                         # Environment variables (API keys, Pinecone config)
