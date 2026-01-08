from huggingface_hub import InferenceClient
from typing import Optional, List, Dict, Any
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)


class HFInferenceClient:
    """HuggingFace Inference API client for LLM interactions."""
    
    def __init__(self, model_id: Optional[str] = None, api_token: Optional[str] = None):
        settings = get_settings()
        self.model_id = model_id or settings.hf_model_id
        self.api_token = api_token or settings.hf_api_token
        
        self.client = InferenceClient(
            model=self.model_id,
            token=self.api_token if self.api_token else None
        )
    
    async def generate(
        self,
        prompt: str,
        max_new_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 0.95,
        stop_sequences: Optional[List[str]] = None,
    ) -> str:
        """Generate text completion from the LLM."""
        try:
            response = self.client.text_generation(
                prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                stop_sequences=stop_sequences,
            )
            return response
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        max_new_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """Generate chat completion from the LLM."""
        try:
            response = self.client.chat_completion(
                messages=messages,
                max_tokens=max_new_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            raise
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for a list of texts (uses embedding model)."""
        settings = get_settings()
        embedding_client = InferenceClient(
            model=settings.embedding_model,
            token=self.api_token if self.api_token else None
        )
        
        try:
            embeddings = embedding_client.feature_extraction(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error getting embeddings: {e}")
            raise

