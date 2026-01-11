import os
import uvicorn
from fastapi import FastAPI, HTTPException

from app.core.logger import setup_logging, get_logger, LOG_FILE
from app.schemas.chat import ChatRequest, ChatResponse
from app.retriever import PineconeRetriever
from app.agents.rag_agent import create_rag_agent

setup_logging()
logger = get_logger(__name__)

app = FastAPI(title="AI Research Assistant")

logger.info(f"Log file location: {LOG_FILE.resolve()}")

# Initialize the RAG agent at startup
rag_agent = create_rag_agent()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    RAG-powered chat endpoint.
    
    1. Retrieves relevant documents from Pinecone based on user query
    2. Creates a system prompt with the retrieved context
    3. Gets an LLM response from HuggingFace
    4. Returns the answer with source documents
    """
    logger.info(f"Request: query={request.query!r}, top_k={request.top_k}")

    try:
        # Run the RAG agent
        result = await rag_agent.run(query=request.query, top_k=request.top_k)
        
        logger.info(f"Response generated for query: {request.query}")
        return ChatResponse(**result)
    
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
