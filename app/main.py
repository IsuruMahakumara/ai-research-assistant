import os  # Added missing import
import uvicorn
from fastapi import FastAPI

from app.core.logger import setup_logging, get_logger, LOG_FILE
from app.schemas.chat import ChatRequest, ChatResponse
from app.llm import chat_model
from app.retriever import PineconeRetriever

setup_logging()
logger = get_logger(__name__)

app = FastAPI(title="AI Research Assistant")

logger.info(f"Log file location: {LOG_FILE.resolve()}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    logger.info(f"Request: query={request.query!r}, top_k={request.top_k}")

    # Invoke the LLM
    response = chat_model.invoke(request.query)

    final_response = {
        "query": request.query,
        "answer": response.content,
        "sources": [] 
    }

    logger.info(f"Response generated for query: {request.query}")
    return final_response

# Root endpoint for Cloud Run Health Checks
@app.get("/")
async def root():
    return {"status": "alive"}


# Test endpoint for Pinecone retriever
@app.get("/test-retriever")
async def test_retriever(query: str = "What is the subject matter and objective of this regulation?"):
    retriever = PineconeRetriever("llama-text-embed-v2-index-gdpr", "gdpr")
    results = retriever.search(query, top_k=2, fields=["text", "article_num"])
    return results




if __name__ == "__main__":
    # Get port from environment, default to 8080
    port = int(os.environ.get("PORT", 8080))
    # Removed reload=True and fixed the module path
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
