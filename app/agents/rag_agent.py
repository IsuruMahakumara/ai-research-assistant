from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.llm import chat_model
from app.retriever import PineconeRetriever
from app.core.logger import get_logger

logger = get_logger(__name__)

# System prompt template for RAG
SYSTEM_TEMPLATE = """You are an AI  assistant specialized in answering questions based on retrieved documents.
Use the following context to answer the user's question. If you cannot find the answer in the context, say so clearly.
Always cite the relevant article numbers when available.

Context:
{context}
"""

# Default configuration
DEFAULT_INDEX_NAME = "llama-text-embed-v2-index-gdpr"
DEFAULT_NAMESPACE = "gdpr"


class RAGAgent:
    """Simple RAG agent that retrieves documents and generates responses."""
    
    def __init__(self, index_name: str = DEFAULT_INDEX_NAME, namespace: str = DEFAULT_NAMESPACE):
        self.retriever = PineconeRetriever(index_name, namespace)
        self.llm = chat_model
        self.output_parser = StrOutputParser()
        
        # Build the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(SYSTEM_TEMPLATE),
            HumanMessagePromptTemplate.from_template("{query}")
        ])
        
        logger.info(f"RAGAgent initialized with index={index_name}, namespace={namespace}")
    
    def _format_context(self, documents: list[dict]) -> str:
        """Format retrieved documents into a context string."""
        if not documents:
            return "No relevant documents found."
        
        context_parts = []
        for doc in documents:
            fields = doc.get("fields", {})
            text = fields.get("text", "")
            article_num = fields.get("article_num", "Unknown")
            context_parts.append(f"[Article {article_num}]: {text}")
        
        return "\n\n".join(context_parts)
    
    def _extract_sources(self, documents: list[dict]) -> list[dict]:
        """Extract source information from retrieved documents."""
        sources = []
        for doc in documents:
            fields = doc.get("fields", {})
            sources.append({
                "id": doc.get("_id", "unknown"),
                "article_num": fields.get("article_num", "Unknown"),
                "text": fields.get("text", ""),
                "score": doc.get("_score", 0.0)
            })
        return sources
    
    async def run(self, query: str, top_k: int = 3) -> dict:
        """
        Execute the RAG pipeline:
        1. Retrieve relevant documents from Pinecone
        2. Format context from documents
        3. Generate response using LLM
        4. Return answer with sources
        """
        logger.info(f"RAGAgent processing query: {query!r} with top_k={top_k}")
        
        # Step 1: Retrieve documents from Pinecone
        retrieval_results = self.retriever.search(
            query=query,
            top_k=top_k,
            fields=["text", "article_num"]
        )
        
        # Extract hits from results
        hits = retrieval_results.get("result", {}).get("hits", [])
        logger.info(f"Retrieved {len(hits)} documents from Pinecone")
        
        # Step 2: Format context
        context = self._format_context(hits)
        
        # Step 3: Create the prompt and invoke LLM
        chain = self.prompt | self.llm | self.output_parser
        
        answer = chain.invoke({
            "context": context,
            "query": query
        })
        
        # Step 4: Extract sources
        sources = self._extract_sources(hits)
        
        logger.info(f"RAGAgent generated response for query: {query!r}")
        
        return {
            "query": query,
            "answer": answer,
            "sources": sources
        }


# Create a default agent instance
def create_rag_agent(index_name: str = DEFAULT_INDEX_NAME, namespace: str = DEFAULT_NAMESPACE) -> RAGAgent:
    """Factory function to create a RAG agent."""
    return RAGAgent(index_name=index_name, namespace=namespace)

