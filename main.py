import ethical_layer
from flask import Flask, request, jsonify
import pdf_loader
import embedding_utils

app = Flask(__name__)

# Initialize in-memory collection
pdf_path = "Essentials of Hindutva.pdf"
collection_name = "my_knowledge_base"

embedding_manager = embedding_utils.EmbeddingManager()

# Load PDF and add embeddings to the collection
try:
    pdf_text = pdf_loader.get_pdf_text(pdf_path)
    if pdf_text is None:
        raise Exception("Failed to load the PDF.")
    text_chunks = pdf_loader.split_text_into_chunks(pdf_text)
    embedding_manager.create_collection(collection_name)
    embedding_manager.add_to_collection(
        collection_name,
        text_chunks,
        [f"doc_{i}" for i in range(len(text_chunks))]
    )
except Exception as e:
    print(f"Error loading PDF or creating collection: {e}")

# API Endpoint for querying the bot
@app.route("/query", methods=["POST"])
def query_bot():
    data = request.get_json()
    query = data.get("query", "")
    if not query:
        return jsonify({"error": "Query is required"}), 400

    # Query the in-memory collection
    results = embedding_manager.query_collection(collection_name, query)
    
    # Build context text from results
    context = "\n".join([res['document'] for res in results])
    
    # Prepare prompt for your ethical_layer bot
    prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
    answer = ethical_layer.generate_safe_response(prompt)
        
    return jsonify({"context": context, "answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
