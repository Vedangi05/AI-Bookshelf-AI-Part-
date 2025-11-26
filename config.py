# API Configuration
API_KEY = "sk-XMvWZn0YZOjYa8v0BHBH1Q"  # Replace with your actual API key
API_BASE_URL = "https://api.ai.it.ufl.edu"  # LiteLLM Proxy is OpenAI compatible
API_MODEL = "gpt-3.5-turbo"  # Model to use (can also use "gpt-4", etc.)

# Embedding Model Configuration
EMBEDDING_MODEL = "all-mpnet-base-v2"  # Sentence transformer model - converts text → embeddings (vectors of numbers)
EMBEDDING_DIMENSION = 768  # Dimension of embeddings from all-mpnet-base-v2

# Milvus Vector Database Configuration
MILVUS_USERNAME = "db_2a2221794b41642"
MILVUS_PASSWORD = "Mb0/k%sBL/a)!BVJ"
MILVUS_ENDPOINT = "https://in03-2a2221794b41642.serverless.aws-eu-central-1.cloud.zilliz.com"
MILVUS_COLLECTION_NAME = "documents"  # Collection name for storing document embeddings
MILVUS_DB_NAME = "bookshelf"  # Database name in Milvus

# PDF Management Configuration
PDF_REFERENCE_FOLDER = "pdf_references"  # Folder containing PDFs to process
CHUNK_SIZE = 500  # Size of text chunks
CHUNK_OVERLAP = 50  # Overlap between chunks

