# AI Research Assistant Backend

A FastAPI-based backend service for an AI research assistant powered by HuggingFace models.

## Local Development

### Prerequisites

- Python 3.12+
- HuggingFace API token

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export HUGGINGFACE_TOKEN=your_token_here

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

- `POST /chat` - Send a chat query and receive an AI-generated response

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

3. **Secret in Secret Manager** for HuggingFace token:
   ```bash
   echo -n "your_huggingface_token" | gcloud secrets create HUGGINGFACE_TOKEN --data-file=-
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
  --repo-name=ai-research-assistant-backend \
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

## Project Structure

```
├── app/
│   ├── agents/        # AI agents (future)
│   ├── core/          # Core utilities (logging, config)
│   ├── llm/           # LLM integrations (HuggingFace)
│   ├── retriever/     # Document retrieval (future RAG)
│   ├── schemas/       # Pydantic models
│   └── main.py        # FastAPI application
├── data/              # Data files
├── logs/              # Application logs
├── notebooks/         # Jupyter notebooks
├── cloudbuild.yaml    # GCP Cloud Build config
├── Dockerfile         # Container definition
└── requirements.txt   # Python dependencies
```

