import os
import config
from pdf_loader import get_pdf_text, split_text_into_chunks

class PDFManager:
    """Lightweight PDF handler — uses shared embedder & Milvus."""

    def __init__(self, embedding_manager, milvus_manager):
        self.embedding = embedding_manager
        self.milvus = milvus_manager
        self.pdf_folder = config.PDF_REFERENCE_FOLDER

        os.makedirs(self.pdf_folder, exist_ok=True)

    def get_pdf_files(self):
        return [
            f for f in os.listdir(self.pdf_folder)
            if f.lower().endswith(".pdf")
        ]

    def process_new_pdfs(self):
        pdfs = self.get_pdf_files()
        embedded = self.milvus.get_all_embedded_files()

        processed = 0
        skipped = 0

        print(f"\n📚 PDFs found: {len(pdfs)}")
        print(f"📦 Already embedded: {len(embedded)}")

        for pdf_file in pdfs:
            if pdf_file in embedded:
                print(f"⏭️  Skipped {pdf_file}")
                skipped += 1
                continue

            print(f"🔄 Processing {pdf_file}")
            full_path = os.path.join(self.pdf_folder, pdf_file)

            text = get_pdf_text(full_path)
            if not text:
                print(f"✗ Could not read {pdf_file}")
                continue

            chunks = split_text_into_chunks(
                text,
                chunk_size=config.CHUNK_SIZE,
                overlap=config.CHUNK_OVERLAP
            )

            embeddings = [self.embedding.embed_text(c) for c in chunks]
            success = self.milvus.add_embeddings(pdf_file, chunks, embeddings)

            if success:
                processed += 1
                print(f"✓ Done: {pdf_file}")
            else:
                print(f"✗ Failed: {pdf_file}")

        print(f"\n📊 Summary: processed={processed}, skipped={skipped}")
        return processed, skipped

    def add_pdf_manually(self, path):
        if not os.path.exists(path):
            print("✗ File not found:", path)
            return False

        name = os.path.basename(path)

        if name in self.milvus.get_all_embedded_files():
            print("✓ Already embedded:", name)
            return True

        print("🔄 Manually processing:", name)

        text = get_pdf_text(path)
        if not text:
            print("✗ Failed loading:", name)
            return False

        chunks = split_text_into_chunks(
            text,
            chunk_size=config.CHUNK_SIZE,
            overlap=config.CHUNK_OVERLAP
        )

        embeddings = [self.embedding.embed_text(c) for c in chunks]
        return self.milvus.add_embeddings(name, chunks, embeddings)
