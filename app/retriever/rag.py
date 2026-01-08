from typing import List, Optional, Tuple
import uuid
import logging
import numpy as np
from dataclasses import dataclass

from app.config import get_settings
from app.llm import HFInferenceClient

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """A document chunk with metadata."""
    id: str
    content: str
    source: str
    embedding: Optional[List[float]] = None
    metadata: Optional[dict] = None


class RAGRetriever:
    """Retrieval-Augmented Generation retriever with vector store."""
    
    def __init__(self):
        self.settings = get_settings()
        self.llm_client = HFInferenceClient()
        self.documents: List[Document] = []
        self._embeddings_matrix: Optional[np.ndarray] = None
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        chunk_size = self.settings.chunk_size
        overlap = self.settings.chunk_overlap
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk)
            start = end - overlap
        
        return chunks
    
    def _cosine_similarity(self, query_embedding: List[float], doc_embeddings: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between query and documents."""
        query_norm = np.linalg.norm(query_embedding)
        doc_norms = np.linalg.norm(doc_embeddings, axis=1)
        
        # Avoid division by zero
        query_norm = query_norm if query_norm > 0 else 1e-10
        doc_norms = np.where(doc_norms > 0, doc_norms, 1e-10)
        
        similarities = np.dot(doc_embeddings, query_embedding) / (doc_norms * query_norm)
        return similarities
    
    async def ingest(self, content: str, source: str, metadata: Optional[dict] = None) -> Tuple[str, int]:
        """Ingest a document into the vector store."""
        chunks = self._chunk_text(content)
        
        if not chunks:
            return "", 0
        
        # Get embeddings for all chunks
        embeddings = self.llm_client.get_embeddings(chunks)
        
        doc_id = str(uuid.uuid4())
        
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            doc = Document(
                id=f"{doc_id}_{i}",
                content=chunk,
                source=source,
                embedding=embedding,
                metadata={**(metadata or {}), "chunk_index": i, "parent_doc": doc_id}
            )
            self.documents.append(doc)
        
        # Update embeddings matrix for efficient search
        self._update_embeddings_matrix()
        
        logger.info(f"Ingested document {doc_id} with {len(chunks)} chunks")
        return doc_id, len(chunks)
    
    def _update_embeddings_matrix(self):
        """Update the cached embeddings matrix."""
        if self.documents:
            self._embeddings_matrix = np.array([
                doc.embedding for doc in self.documents if doc.embedding
            ])
        else:
            self._embeddings_matrix = None
    
    async def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        """Retrieve most relevant documents for a query."""
        if not self.documents or self._embeddings_matrix is None:
            return []
        
        # Get query embedding
        query_embedding = self.llm_client.get_embeddings([query])[0]
        
        # Compute similarities
        similarities = self._cosine_similarity(query_embedding, self._embeddings_matrix)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = [
            (self.documents[i], float(similarities[i]))
            for i in top_indices
            if similarities[i] > 0
        ]
        
        return results
    
    async def query_with_context(self, query: str, top_k: int = 5) -> Tuple[str, List[Tuple[Document, float]]]:
        """Retrieve documents and format context for LLM."""
        results = await self.retrieve(query, top_k)
        
        if not results:
            return "", []
        
        context_parts = []
        for i, (doc, score) in enumerate(results, 1):
            context_parts.append(f"[Source {i}: {doc.source}]\n{doc.content}\n")
        
        context = "\n".join(context_parts)
        return context, results

