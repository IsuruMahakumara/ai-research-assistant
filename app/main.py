import uvicorn
from fastapi import FastAPI

from app.core.logger import setup_logging, get_logger, LOG_FILE
from app.schemas.chat import ChatRequest, ChatResponse

setup_logging()
logger = get_logger(__name__)

app = FastAPI(title="AI Research Assistant")

logger.info(f"Log file location: {LOG_FILE.resolve()}")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint for user queries.

    Future: retrieval over static KB, LLM inference, response generation.
    """
    logger.info(f"Request: query={request.query!r}, top_k={request.top_k}")

    response = ChatResponse(
        query=request.query,
        answer="",
        sources=[],
    )

    logger.info(f"Response: query={response.query!r}, answer={response.answer!r}, sources_count={len(response.sources)}")

    return response


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
