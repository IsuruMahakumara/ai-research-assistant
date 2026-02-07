# AI Research Assistant

A full-stack AI research assistant powered by HuggingFace models and Pinecone vector database. This is a monolith application with a FastAPI backend serving a React frontend.

## Project Structure

```
├── app/                   # Python backend
│   ├── agents/            # AI agents (RAG agent)
│   ├── core/              # Core utilities (logging, config)
│   ├── llm/               # LLM integrations (HuggingFace)
│   ├── retriever/         # Document retrieval (Pinecone)
│   ├── schemas/           # Pydantic models
│   └── main.py            # FastAPI application
├── frontend/              # React frontend
│   ├── src/               # Source files
│   ├── public/            # Static assets
│   ├── package.json       # Node dependencies
│   └── vite.config.ts     # Vite configuration
├── static/                # Built frontend (generated)
├── cloudbuild.yaml        # GCP Cloud Build config
├── Dockerfile             # Multi-stage container build
└── requirements.txt       # Python dependencies
```

## Local Development

### Prerequisites

- Python 3.12+
- Node.js 20+
- HuggingFace API token
- Pinecone API key

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export HUGGINGFACE_TOKEN=your_token_here
export PINECONE_API_KEY=your_pinecone_key_here

# Run the backend server
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run the dev server (proxies API requests to backend)
npm run dev
```

The frontend dev server runs on http://localhost:5173 and proxies `/api/*` requests to the backend at http://localhost:8080.

### Production Build

```bash
cd frontend
npm run build
```

This builds the frontend and outputs to the `static/` directory, which FastAPI serves automatically.

## API Endpoints

- `POST /chat` - Send a query and receive an AI-generated response with source documents
- `GET /health` - Health check endpoint
- `GET /test-retriever` - Test the Pinecone retriever

## GCP Cloud Build Deployment

This project includes a `cloudbuild.yaml` for automated deployment to Google Cloud Run.

### Prerequisites

1. **GCP Project** with the following APIs enabled:
   - Cloud Build API
   - Cloud Run API
   - Artifact Registry API
   - Secret Manager API

2. **Artifact Registry Repository** (create if not exists):
   ```bash
   gcloud artifacts repositories create cloud-run-images \
     --repository-format=docker \
     --location=us-central1 \
     --description="Docker images for Cloud Run"
   ```

3. **Secrets in Secret Manager**:
   ```bash
   # HuggingFace token
   echo -n "your_huggingface_token" | gcloud secrets create HUGGINGFACE_TOKEN --data-file=-
   
   # Pinecone API key
   echo -n "your_pinecone_api_key" | gcloud secrets create PINECONE_API_KEY --data-file=-
   ```

4. **IAM Permissions** for Cloud Build service account:
   ```bash
   PROJECT_ID=$(gcloud config get-value project)
   PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
   
   # Grant Cloud Run Admin role
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
     --role="roles/run.admin"
   
   # Grant Service Account User role
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
     --role="roles/iam.serviceAccountUser"
   
   # Grant Secret Manager Accessor role
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
     --role="roles/secretmanager.secretAccessor"
   ```

### Manual Trigger

```bash
gcloud builds submit --config cloudbuild.yaml
```

### With Custom Substitutions

```bash
gcloud builds submit --config cloudbuild.yaml \
  --substitutions=_REGION=us-west1,_SERVICE_NAME=my-ai-assistant
```

### Set Up Continuous Deployment

Connect your repository to Cloud Build for automatic deployments on push:

```bash
gcloud builds triggers create github \
  --repo-name=ai-research-assistant \
  --repo-owner=YOUR_GITHUB_USERNAME \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

## Configuration

The Cloud Build configuration uses the following substitution variables (can be overridden):

| Variable | Default | Description |
|----------|---------|-------------|
| `_REGION` | `us-central1` | GCP region for deployment |
| `_SERVICE_NAME` | `ai-research-assistant` | Cloud Run service name |
| `_REPOSITORY` | `cloud-run-images` | Artifact Registry repository |
