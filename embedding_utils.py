from sentence_transformers import SentenceTransformer
import config
import numpy as np
from numpy.linalg import norm

class EmbeddingManager:
    def __init__(self, embedding_model_name=config.EMBEDDING_MODEL):
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.collections = {}  # In-memory storage for collections

    def create_collection(self, collection_name):
        """Creates a collection in memory."""
        if collection_name not in self.collections:
            print(f"Creating new collection: '{collection_name}'")
            self.collections[collection_name] = {'documents': [], 'embeddings': [], 'ids': []}
        else:
            print(f"Collection '{collection_name}' already exists.")
        return collection_name

    def embed_text(self, text):
        """Embeds a single piece of text."""
        return self.embedding_model.encode(text)

    def add_to_collection(self, collection_name, documents, ids):
        """Adds documents and their embeddings to the in-memory collection."""
        embeddings = [self.embed_text(doc) for doc in documents]
        self.collections[collection_name]['documents'].extend(documents)
        self.collections[collection_name]['embeddings'].extend(embeddings)
        self.collections[collection_name]['ids'].extend(ids)

    def query_collection(self, collection_name, query_text, n_results=5):
        """Queries the in-memory collection using cosine similarity."""
        query_embedding = self.embed_text(query_text)
        embeddings = np.array(self.collections[collection_name]['embeddings'])
        documents = self.collections[collection_name]['documents']
        ids = self.collections[collection_name]['ids']

        if len(embeddings) == 0:
            return []

        # Compute cosine similarities
        sims = np.dot(embeddings, query_embedding) / (norm(embeddings, axis=1) * norm(query_embedding) + 1e-10)
        top_idx = np.argsort(sims)[-n_results:][::-1]

        results = [{'id': ids[i], 'document': documents[i], 'score': sims[i]} for i in top_idx]
        return results
