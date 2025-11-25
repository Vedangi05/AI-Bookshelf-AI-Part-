import ethical_layer
from flask import Flask, request, jsonify
import pdf_loader
import embedding_utils

app = Flask(__name__)

# Initialize in-memory collection
pdf_path = "DBMS.pdf"
collection_name = "my_knowledge_base"

embedding_manager = embedding_utils.EmbeddingManager()

# Load PDF and add embeddings to the collection
try:
    pdf_text = pdf_loader.get_pdf_text(pdf_path)
    if pdf_text is None:
        raise Exception("Failed to load the PDF.")
    text_chunks = pdf_loader.split_text_into_chunks(pdf_text)
# A new vector embedding collection is created.
# Every chunk of the PDF is converted into an embedding.
# Embeddings are stored in RAM (in-memory) — nothing is saved permanently.
# This is your knowledge base.
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
    #This finds the most similar chunks from the PDF using embeddings
    results = embedding_manager.query_collection(collection_name, query)
    
    # This joins the retrieved chunks into a single context block.
    context = "\n".join([res['document'] for res in results])
    
    # Prepare prompt for your ethical_layer bot
#     This constructs a prompt containing:

# The retrieved context

# The user's question

# The instruction to generate an answer
    prompt = f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
#     The ethical_layer ensures:

# No harmful content

# No unsafe advice

# No hallucinated dangerous info
    answer = ethical_layer.generate_safe_response(prompt)
        
    return jsonify({"context": context, "answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
