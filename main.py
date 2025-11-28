import ethical_layer
import logging
import threading
from flask import Flask, request, jsonify, render_template

# Import updated managers
from embedding_utils import EmbeddingManager
from milvus_manager import MilvusManager
from pdf_manager import PDFManager


# -------------------------------------------------------------
# LOGGING CONFIG
# -------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[logging.StreamHandler()]
)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.logger = logging.getLogger("ai-bookshelf")

app.logger.info("\n🚀 AI-Bookshelf Application initializing...\n")


# -------------------------------------------------------------
# GLOBAL SINGLETON INSTANCES (loaded in background)
# -------------------------------------------------------------
embedding_manager = None
milvus_manager = None
pdf_manager = None


# -------------------------------------------------------------
# BACKGROUND INITIALIZATION (HF Spaces safe)
# -------------------------------------------------------------
def init_in_background():
    global embedding_manager, milvus_manager, pdf_manager

    try:
        app.logger.info("🔧 Initializing embedding + Milvus managers...")

        # Load embedding model only once
        embedding_manager = EmbeddingManager()

        # Connect Milvus only once
        milvus_manager = MilvusManager()

        # PDFManager now uses the same managers
        pdf_manager = PDFManager(embedding_manager, milvus_manager)

        app.logger.info("📂 Processing PDFs...")
        processed, skipped = pdf_manager.process_new_pdfs()

        app.logger.info(
            f"✓ Initialization complete! processed={processed}, skipped={skipped}"
        )

    except Exception:
        app.logger.exception("❌ Background initialization failed")


# Start initialization the moment the module loads
threading.Thread(target=init_in_background, daemon=True).start()


# -------------------------------------------------------------
# ROUTES
# -------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    response = None
    upload_message = None

    if request.method == "POST":
        user_query = request.form.get("user_query", "").strip()

        if user_query:
            if embedding_manager is None:
                response = "Service is initializing… please wait."
            else:
                try:
                    query_emb = embedding_manager.embed_text(user_query)

                    results = milvus_manager.search_embeddings(query_emb, n=5)

                    if not results:
                        response = "No relevant information found."
                    else:
                        context = "\n".join([r["document"] for r in results])
                        prompt = f"Context:\n{context}\n\nQuestion: {user_query}\n\nAnswer:"
                        response = ethical_layer.generate_safe_response(prompt)

                except Exception as e:
                    response = f"Error: {str(e)}"

    return render_template("index.html", response=response, upload_message=upload_message)


@app.route("/upload", methods=["POST"])
def upload_pdf():
    if "pdf_file" not in request.files:
        return render_template("index.html", upload_message="No file uploaded"), 400

    file = request.files["pdf_file"]

    if file.filename == "":
        return render_template("index.html", upload_message="Empty filename"), 400

    if not file.filename.lower().endswith(".pdf"):
        return render_template("index.html", upload_message="Invalid file type"), 400

    save_path = f"pdf_references/{file.filename}"
    file.save(save_path)

    success = (
        pdf_manager.add_pdf_manually(save_path)
        if pdf_manager is not None
        else False
    )

    msg = "PDF processed successfully" if success else "Error processing PDF"
    return render_template("index.html", upload_message=msg)


@app.route("/query", methods=["POST"])
def query_api():
    try:
        payload = request.get_json() or request.form
        query = payload.get("query") or payload.get("user_query")

        if not query:
            return jsonify({"error": "Missing query"}), 400

        if embedding_manager is None:
            return jsonify({"error": "Initializing, try again soon"}), 503

        emb = embedding_manager.embed_text(query)
        results = milvus_manager.search_embeddings(emb, n=5)

        if not results:
            return jsonify({
                "context": "",
                "answer": "No relevant information found.",
                "file_names": []
            }), 200

        context = "\n".join([r["document"] for r in results])
        file_names = list({r["file_name"] for r in results})

        answer = ethical_layer.generate_safe_response(
            f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
        )

        return jsonify({
            "context": context,
            "answer": answer,
            "file_names": file_names,
            "num_results": len(results)
        })

    except Exception as e:
        app.logger.exception("❌ Error in /query")
        return jsonify({"error": str(e)}), 500


@app.route("/status")
def status():
    if milvus_manager is None:
        return jsonify({"status": "initializing"}), 200

    files = milvus_manager.get_all_embedded_files()

    return jsonify({
        "status": "running",
        "embedded_files": list(files),
        "total_files": len(files)
    }), 200


@app.route("/add-pdf", methods=["POST"])
def add_pdf():
    try:
        data = request.get_json()
        pdf_path = data.get("pdf_path")

        if not pdf_path:
            return jsonify({"error": "pdf_path missing"}), 400

        success = (
            pdf_manager.add_pdf_manually(pdf_path)
            if pdf_manager
            else False
        )

        return jsonify({"success": success}), 200 if success else 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/healthz")
def health():
    return "ok", 200


# Local run only (gunicorn won't enter here)
if __name__ == "__main__":
    app.run(port=7860, debug=False)
