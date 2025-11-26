import ethical_layer
from flask import Flask, request, jsonify
from pdf_manager import PDFManager
from embedding_utils import EmbeddingManager
from milvus_manager import MilvusManager

app = Flask(__name__)

# Initialize managers
print("\n🚀 Initializing AI-Bookshelf Application...\n")

try:
    embedding_manager = EmbeddingManager()
    milvus_manager = MilvusManager()
    pdf_manager = PDFManager()
    
    # Process PDFs on startup
    print("📂 Checking for new PDFs to embed...")
    processed, skipped = pdf_manager.process_new_pdfs()
    
except Exception as e:
    print(f"✗ Error during initialization: {e}")
    raise


# API Endpoint for querying the bot
@app.route("/query", methods=["POST"])
def query_bot():
    """Query the knowledge base and generate a response."""
    try:
        data = request.get_json()
        query = data.get("query", "")
        
        if not query:
            return jsonify({"error": "Query is required"}), 400

        # Generate embedding for the query
        query_embedding = embedding_manager.embed_text(query)
        
        if query_embedding is None:
            return jsonify({"error": "Failed to embed query"}), 500
        
        # Search Milvus for similar documents
        results = milvus_manager.search_embeddings(query_embedding, n_results=5)
        
        if not results:
            return jsonify({
                "context": "",
                "answer": "I couldn't find relevant information in the knowledge base.",
                "file_names": []
            }), 200
        
        # Prepare context from search results
        context = "\n".join([res['document'] for res in results])
        file_names = list(set([res['file_name'] for res in results]))
        
        # Generate prompt for ethical layer
        prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
        
        # Generate safe response
        answer = ethical_layer.generate_safe_response(prompt)
        
        return jsonify({
            "context": context,
            "answer": answer,
            "file_names": file_names,
            "num_results": len(results)
        }), 200
        
    except Exception as e:
        print(f"✗ Error processing query: {e}")
        return jsonify({"error": f"Error processing query: {str(e)}"}), 500


@app.route("/status", methods=["GET"])
def get_status():
    """Get the status of the knowledge base."""
    try:
        embedded_files = milvus_manager.get_all_embedded_files()
        return jsonify({
            "status": "running",
            "embedded_files": list(embedded_files),
            "total_files": len(embedded_files)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/add-pdf", methods=["POST"])
def add_pdf():
    """Manually add a PDF file to the knowledge base."""
    try:
        data = request.get_json()
        pdf_path = data.get("pdf_path", "")
        
        if not pdf_path:
            return jsonify({"error": "pdf_path is required"}), 400
        
        success = pdf_manager.add_pdf_manually(pdf_path)
        
        return jsonify({
            "success": success,
            "message": f"PDF added successfully" if success else "Failed to add PDF"
        }), 200 if success else 400
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    try:
        print("🌐 Starting Flask server on http://localhost:5000\n")
        app.run(debug=True, port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        milvus_manager.close_connection()
        print("✓ Application closed")
    except Exception as e:
        print(f"✗ Error running application: {e}")
        milvus_manager.close_connection()
