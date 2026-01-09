from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class ChatRequest(BaseModel):
    query: str = Field(..., description="User's question or query", min_length=1)
    top_k: int = Field(default=3, description="Number of relevant documents to retrieve", ge=1, le=10)


class RetrievedDocument(BaseModel):
    id: str
    title: str
    content: str
    relevance_score: float


class ChatResponse(BaseModel):
    query: str
    answer: str
    sources: list[RetrievedDocument]

