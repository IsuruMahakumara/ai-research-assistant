from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.schemas import (
    QueryRequest,
    QueryResponse,
    IngestRequest,
    IngestResponse,
    SourceDocument,
)
from app.retriever import RAGRetriever
from app.agents import ReasoningAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global instances
retriever: RAGRetriever = None
reasoning_agent: ReasoningAgent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup application resources."""
    global retriever, reasoning_agent
    
    logger.info("Initializing AI Research Assistant...")
    settings = get_settings()
    
    # Initialize retriever and reasoning agent
    retriever = RAGRetriever()
    reasoning_agent = ReasoningAgent(retriever)
    
    logger.info(f"Using LLM model: {settings.hf_model_id}")
    logger.info(f"Using embedding model: {settings.embedding_model}")
    
    yield
    
    logger.info("Shutting down AI Research Assistant...")


app = FastAPI(
    title="AI Research Assistant",
    description="An AI-powered research assistant with RAG capabilities",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ai-research-assistant"}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "AI Research Assistant",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Process a research query using RAG and multi-step reasoning.
    
    The system will:
    1. Decompose complex queries into sub-questions (if use_reasoning=True)
    2. Retrieve relevant documents for each question
    3. Generate answers grounded in the retrieved context
    4. Synthesize a final comprehensive answer
    """
    try:
        result = await reasoning_agent.reason_and_answer(
            query=request.query,
            max_sources=request.max_sources,
            use_decomposition=request.use_reasoning,
        )
        
        return QueryResponse(
            answer=result["answer"],
            reasoning_steps=result["reasoning_steps"],
            sources=[
                SourceDocument(
                    content=s["content"],
                    source=s["source"],
                    relevance_score=s["relevance_score"],
                    metadata=s.get("metadata"),
                )
                for s in result["sources"]
            ],
            confidence=result["confidence"],
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestRequest):
    """
    Ingest a document into the knowledge base.
    
    The document will be:
    1. Split into chunks
    2. Embedded using the configured embedding model
    3. Stored in the vector store for retrieval
    """
    try:
        doc_id, chunks_created = await retriever.ingest(
            content=request.content,
            source=request.source,
            metadata=request.metadata,
        )
        
        if not doc_id:
            return IngestResponse(
                success=False,
                document_id="",
                chunks_created=0,
                message="No content to ingest",
            )
        
        return IngestResponse(
            success=True,
            document_id=doc_id,
            chunks_created=chunks_created,
            message=f"Successfully ingested document with {chunks_created} chunks",
        )
        
    except Exception as e:
        logger.error(f"Error ingesting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get statistics about the knowledge base."""
    return {
        "total_documents": len(retriever.documents) if retriever else 0,
        "status": "ready" if retriever else "initializing",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

