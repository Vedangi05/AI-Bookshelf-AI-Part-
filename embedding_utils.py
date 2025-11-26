from sentence_transformers import SentenceTransformer
import config


class EmbeddingManager:
    """Manages text embeddings using SentenceTransformer model."""
    
    def __init__(self, embedding_model_name=config.EMBEDDING_MODEL):
        """Initialize the embedding model."""
        self.embedding_model = SentenceTransformer(embedding_model_name)
        print(f"✓ Loaded embedding model: {embedding_model_name}")

    def embed_text(self, text):
        """
        Embed a single piece of text into a vector.
        
        Args:
            text: Text to embed
            
        Returns:
            Numpy array representing the embedding
        """
        try:
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            print(f"✗ Error embedding text: {e}")
            return None

    def embed_multiple(self, texts):
        """
        Embed multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of numpy arrays representing embeddings
        """
        try:
            embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
            return embeddings
        except Exception as e:
            print(f"✗ Error embedding multiple texts: {e}")
            return None
