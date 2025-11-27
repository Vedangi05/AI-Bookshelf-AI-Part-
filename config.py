import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
API_KEY = os.getenv("API_KEY", "sk-XMvWZn0YZOjYa8v0BHBH1Q")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.ai.it.ufl.edu")
API_MODEL = os.getenv("API_MODEL", "gpt-oss-120b")

# Embedding Model Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-mpnet-base-v2")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "768"))

# Milvus Vector Database Configuration
MILVUS_USERNAME = os.getenv("MILVUS_USERNAME", "db_2a2221794b41642")
MILVUS_PASSWORD = os.getenv("MILVUS_PASSWORD", "Mb0/k%sBL/a)!BVJ")
MILVUS_ENDPOINT = os.getenv("MILVUS_ENDPOINT", "https://in03-2a2221794b41642.serverless.aws-eu-central-1.cloud.zilliz.com")
MILVUS_COLLECTION_NAME = os.getenv("MILVUS_COLLECTION_NAME", "documents")
MILVUS_DB_NAME = os.getenv("MILVUS_DB_NAME", "bookshelf")

# PDF Management Configuration
PDF_REFERENCE_FOLDER = os.getenv("PDF_REFERENCE_FOLDER", "pdf_references")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

