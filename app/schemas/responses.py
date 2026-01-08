from pydantic import BaseModel, Field
from typing import List, Optional


class SourceDocument(BaseModel):
    """A source document retrieved for answering a query."""
    
    content: str = Field(..., description="The document content")
    source: str = Field(..., description="Source identifier")
    relevance_score: float = Field(..., description="Relevance score to the query")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata")


class QueryResponse(BaseModel):
    """Response model for research queries."""
    
    answer: str = Field(..., description="The generated answer")
    reasoning_steps: List[str] = Field(default_factory=list, description="Steps taken during reasoning")
    sources: List[SourceDocument] = Field(default_factory=list, description="Source documents used")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score")


class IngestResponse(BaseModel):
    """Response model for document ingestion."""
    
    success: bool = Field(..., description="Whether ingestion was successful")
    document_id: str = Field(..., description="Unique identifier for the ingested document")
    chunks_created: int = Field(..., description="Number of chunks created")
    message: str = Field(default="", description="Additional information")

