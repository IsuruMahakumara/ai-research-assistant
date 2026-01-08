from pydantic import BaseModel, Field
from typing import Optional


class QueryRequest(BaseModel):
    """Request model for research queries."""
    
    query: str = Field(..., description="The research question to answer")
    max_sources: int = Field(default=5, ge=1, le=20, description="Maximum number of sources to retrieve")
    use_reasoning: bool = Field(default=True, description="Whether to use multi-step reasoning")


class IngestRequest(BaseModel):
    """Request model for document ingestion."""
    
    content: str = Field(..., description="The document content to ingest")
    source: str = Field(..., description="Source identifier (URL, filename, etc.)")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata")

