# AI-Bookshelf with Milvus

A RAG (Retrieval-Augmented Generation) application using Milvus vector database and OpenAI API.

## ⚡ Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create PDF Folder
```bash
mkdir pdf_references
```

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
