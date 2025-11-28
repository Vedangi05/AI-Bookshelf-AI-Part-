---
title: AI-Bookshelf RAG
emoji: 📚
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# AI-Bookshelf RAG

A Retrieval-Augmented Generation (RAG) system for managing and searching your personal book collection using vector embeddings and Milvus vector database.

## Features

- 📚 **Browse Books** — View all embedded documents in your knowledge base
- 🔍 **Semantic Search** — Ask questions and get AI-powered answers with source attribution
- ⬆️ **Upload PDFs** — Add new books to the knowledge base (automatically chunked and embedded)
- 🤖 **AI-Powered Responses** — Uses OpenAI-compatible LLM with retrieval-augmented generation
- 🔐 **Vector Storage** — Milvus serverless vector database for fast similarity search

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Flask API
- **Vector DB**: Milvus (serverless)
- **Embeddings**: Sentence Transformers (all-mpnet-base-v2)
- **LLM**: OpenAI-compatible API (LiteLLM Proxy)
- **Container**: Docker

## Quick Start

### Local Development

1. Clone and setup:
```bash
cd AI-Bookshelf-RAG
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
```

2. Run both services locally:

**Option A: Start script (Windows)**
```powershell
start.bat
```

**Option B: Manual (all platforms)**
```bash
# Terminal 1 - Flask backend
python main.py

# Terminal 2 - Streamlit frontend
streamlit run ui.py  # http://localhost:8501
```

### Docker

```bash
docker build -t ai-bookshelf-rag .
docker run -p 8501:8501 -p 5000:5000 \
  -e API_KEY="your_key" \
  -e MILVUS_USERNAME="user" \
  -e MILVUS_PASSWORD="pass" \
  -e MILVUS_ENDPOINT="endpoint" \
  ai-bookshelf-rag
```

## Configuration

Set these environment variables in `.env`:

- `API_KEY` — OpenAI/LiteLLM API key
- `API_BASE_URL` — API endpoint
- `API_MODEL` — Model name
- `MILVUS_USERNAME`, `MILVUS_PASSWORD`, `MILVUS_ENDPOINT` — Database credentials
- `EMBEDDING_MODEL` — Sentence transformer (default: all-mpnet-base-v2)

See `.env.example` for all options.

## API Endpoints

**POST** `/query` — Search knowledge base
```json
{"query": "What are the main topics?"}
```

**GET** `/status` — Check system status

**POST** `/add-pdf` — Upload new PDF
```json
{"pdf_path": "pdf_references/book.pdf"}
```

## Deployment

### Hugging Face Spaces

1. Create a new Docker Space: https://huggingface.co/spaces
2. Add secrets in Space Settings (Repository secrets):
   - `API_KEY`
   - `MILVUS_USERNAME`
   - `MILVUS_PASSWORD`
   - `MILVUS_ENDPOINT`
3. Push code:
```bash
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
git push hf main
```

## Project Structure

```
├── ui.py                      # Streamlit frontend
├── main.py                    # Flask API backend
├── config.py                  # Configuration
├── embedding_utils.py         # Text embeddings
├── milvus_manager.py          # Vector DB
├── pdf_manager.py             # PDF processing
├── ethical_layer.py           # LLM + safety
├── Dockerfile                 # Container config
├── start.sh / start.bat       # Launch scripts
├── requirements.txt           # Dependencies
└── .env.example              # Environment template
```

## License

MIT License

---

**Built with ❤️ | RAG + AI + Vector Search**

### 3. Add Your PDFs
```bash
cp your_documents/*.pdf pdf_references/
```

### 4. Run Application
```bash
python main.py
```

The app will:
- Load embedding model
- Connect to Milvus
- Check for new PDFs
- Skip already-processed PDFs
- Start Flask API on http://localhost:5000

### 5. Query the API
```bash
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Your question here"}'
```

## 📁 Project Structure-AI-Part-
AI-Bookshelf(AI Part)
