from typing import List, Dict, Any
import openai
from config.settings import OPENAI_API_KEY, EMBEDDING_MODEL

class EmbeddingsService:
    """
    Service for generating and managing embeddings using OpenAI
    """
    
    def __init__(self):
        """Initialize the embedding service with API key"""
        openai.api_key = OPENAI_API_KEY
        self.model = EMBEDDING_MODEL
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            
        Returns:
            List[float]: Vector embedding
        """
        try:
            response = openai.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")
    
    def generate_batch_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for a list of text chunks
        
        Args:
            chunks: List of chunk dictionaries with text
            
        Returns:
            List[Dict]: Chunks with added embeddings
        """
        result = []
        
        for chunk in chunks:
            embedding = self.generate_embedding(chunk["text"])
            chunk["embedding"] = embedding
            result.append(chunk)
            
        return result
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a search query
        
        Args:
            query: Query text
            
        Returns:
            List[float]: Vector embedding for the query
        """
        return self.generate_embedding(query)