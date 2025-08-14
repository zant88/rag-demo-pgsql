import cohere
from typing import List, Optional
from app.core.config import settings

class EmbeddingService:
    def __init__(self):
        self.client = cohere.Client(settings.COHERE_API_KEY)
        self.model = "embed-english-v3.0"  # Cohere's latest embedding model

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        try:
            if not text or not text.strip():
                print(f"[EMBEDDING DEBUG] Empty or whitespace-only text provided")
                return None
            
            print(f"[EMBEDDING DEBUG] Generating embedding for text length: {len(text)}")
            
            # Use Cohere's embed API
            response = self.client.embed(
                texts=[text],
                model=self.model,
                input_type="search_document"  # For document embeddings
            )
            
            print(f"[EMBEDDING DEBUG] Cohere API response received")
            
            # Get the original embedding
            embedding = response.embeddings[0]
            original_length = len(embedding)
            print(f"[EMBEDDING DEBUG] Original embedding length: {original_length}")
            
            # Cohere embeddings are 1024 dimensions, pad to 1536 for compatibility
            # Pad with zeros to reach 1536 dimensions
            while len(embedding) < 1536:
                embedding.append(0.0)
            
            final_embedding = embedding[:1536]  # Ensure exactly 1536 dimensions
            print(f"[EMBEDDING DEBUG] Final embedding length: {len(final_embedding)}")
            
            return final_embedding
        except Exception as e:
            print(f"[EMBEDDING ERROR] Error generating embedding: {str(e)}")
            print(f"[EMBEDDING ERROR] Text length: {len(text) if text else 'None'}")
            print(f"[EMBEDDING ERROR] Text preview: {text[:100] if text else 'None'}...")
            return None

    async def generate_embeddings_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        # Optionally implement batching if needed, or just loop over generate_embedding
        return [await self.generate_embedding(text) for text in texts]

    async def generate_query_embedding(self, query: str) -> Optional[List[float]]:
        try:
            if not query or not query.strip():
                return None
            
            # Use Cohere's embed API with search_query input type
            response = self.client.embed(
                texts=[query],
                model=self.model,
                input_type="search_query"  # For search queries
            )
            
            # Cohere embeddings are 1024 dimensions, pad to 1536 for compatibility
            embedding = response.embeddings[0]
            # Pad with zeros to reach 1536 dimensions
            while len(embedding) < 1536:
                embedding.append(0.0)
            
            return embedding[:1536]  # Ensure exactly 1536 dimensions
        except Exception as e:
            print(f"Error generating query embedding: {str(e)}")
            return None