# AI Research Assistant Backend

A FastAPI-based backend for an AI-powered research assistant with RAG (Retrieval-Augmented Generation) capabilities.

## Features

- **Multi-step Reasoning**: Decomposes complex queries into sub-questions for thorough research
- **RAG Pipeline**: Retrieves relevant documents to ground LLM responses in factual content
- **HuggingFace Integration**: Uses HF Inference API for LLM and embedding models
- **Document Ingestion**: Ingest documents with automatic chunking and embedding

## Project Structure

```
ai-research-assistant-backend/
├── app/
│   ├── main.py              # FastAPI entrypoint
│   ├── config.py            # Configuration settings
│   ├── agents/              # Planner and reasoning agents
│   ├── retriever/           # RAG logic
│   ├── llm/                 # HuggingFace inference client
│   └── schemas/             # Pydantic models
├── data/
│   └── ingestion/           # Document ingestion
├── requirements.txt
└── README.md
```

## Setup

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   Create a `.env` file in the project root:
   ```env
   HF_API_TOKEN=your_huggingface_token
   HF_MODEL_ID=mistralai/Mistral-7B-Instruct-v0.2
   DEBUG=false
   ```

4. **Run the server**:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Query
```http
POST /query
Content-Type: application/json

{
  "query": "What are the latest advances in transformer architectures?",
  "max_sources": 5,
  "use_reasoning": true
}
```

### Ingest Document
```http
POST /ingest
Content-Type: application/json

{
  "content": "Document text content...",
  "source": "research_paper.pdf",
  "metadata": {"author": "John Doe"}
}
```

### Health Check
```http
GET /health
```

## Configuration Options

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `HF_API_TOKEN` | HuggingFace API token | - |
| `HF_MODEL_ID` | LLM model ID | `mistralai/Mistral-7B-Instruct-v0.2` |
| `EMBEDDING_MODEL` | Embedding model ID | `sentence-transformers/all-MiniLM-L6-v2` |
| `CHUNK_SIZE` | Document chunk size | `512` |
| `CHUNK_OVERLAP` | Overlap between chunks | `50` |
| `DEBUG` | Enable debug mode | `false` |

## License

MIT

