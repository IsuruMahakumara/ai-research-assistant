from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    query: str = Field(..., description="User's question or query", min_length=1)
    top_k: int = Field(default=3, description="Number of relevant documents to retrieve", ge=1, le=10)


class RetrievedDocument(BaseModel):
    """Document retrieved from Pinecone vector store."""
    id: str = Field(..., description="Document ID from Pinecone")
    article_num: str = Field(..., description="Article number from the source document")
    text: str = Field(..., description="Text content of the document")
    score: float = Field(..., description="Relevance score from vector search")


class ChatResponse(BaseModel):
    """Response from the RAG agent."""
    query: str = Field(..., description="Original user query")
    answer: str = Field(..., description="Generated answer from LLM")
    sources: list[RetrievedDocument] = Field(default_factory=list, description="Retrieved source documents")

