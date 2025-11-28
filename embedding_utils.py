from sentence_transformers import SentenceTransformer
import config
import threading

# -------------------------------------------------------------
# GLOBAL SHARED SENTENCE TRANSFORMER MODEL
# -------------------------------------------------------------
# Load ONCE at import (guaranteed to be safe with HF Spaces)
# -------------------------------------------------------------
_MODEL = None
_MODEL_LOCK = threading.Lock()

def _load_global_model():
    global _MODEL
    with _MODEL_LOCK:
        if _MODEL is None:
            print(f"🔥 Loading embedding model: {config.EMBEDDING_MODEL}")
            _MODEL = SentenceTransformer(config.EMBEDDING_MODEL)
            print("✓ Embedding model loaded")
    return _MODEL


class EmbeddingManager:
    """Thin wrapper around global SentenceTransformer model"""
    
    def __init__(self):
        self.embedding_model = _load_global_model()

    def embed_text(self, text):
        try:
            return self.embedding_model.encode(text, convert_to_numpy=True)
        except Exception as e:
            print(f"✗ Error embedding text: {e}")
            return None

    def embed_multiple(self, texts):
        try:
            return self.embedding_model.encode(texts, convert_to_numpy=True)
        except Exception as e:
            print(f"✗ Error embedding multiple texts: {e}")
            return None
