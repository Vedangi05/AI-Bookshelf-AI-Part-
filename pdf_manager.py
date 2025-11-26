import os
import config
from pdf_loader import get_pdf_text, split_text_into_chunks
from embedding_utils import EmbeddingManager
from milvus_manager import MilvusManager


class PDFManager:
    """Manages PDF processing and checks for existing embeddings."""
    
    def __init__(self):
        """Initialize PDF manager with embedding and Milvus managers."""
        self.pdf_folder = config.PDF_REFERENCE_FOLDER
        self.embedding_manager = EmbeddingManager()
        self.milvus_manager = MilvusManager()
        
        # Create reference folder if it doesn't exist
        if not os.path.exists(self.pdf_folder):
            os.makedirs(self.pdf_folder)
            print(f"✓ Created PDF reference folder: {self.pdf_folder}")
    
    def get_pdf_files(self):
        """Get list of all PDF files in the reference folder."""
        if not os.path.exists(self.pdf_folder):
            print(f"✗ PDF reference folder does not exist: {self.pdf_folder}")
            return []
        
        pdf_files = [
            f for f in os.listdir(self.pdf_folder)
            if f.lower().endswith('.pdf')
        ]
        return pdf_files
    
    def process_new_pdfs(self):
        """
        Process PDF files that haven't been embedded yet.
        Skips files that already have embeddings in Milvus.
        """
        pdf_files = self.get_pdf_files()
        embedded_files = self.milvus_manager.get_all_embedded_files()
        
        processed_count = 0
        skipped_count = 0
        
        print(f"\n📚 Found {len(pdf_files)} PDF files in {self.pdf_folder}")
        print(f"📦 Already embedded files: {len(embedded_files)}\n")
        
        for pdf_file in pdf_files:
            if pdf_file in embedded_files:
                print(f"⏭️  Skipping {pdf_file} (already embedded)")
                skipped_count += 1
                continue
            
            print(f"🔄 Processing {pdf_file}...")
            
            pdf_path = os.path.join(self.pdf_folder, pdf_file)
            
            # Extract text from PDF
            pdf_text = get_pdf_text(pdf_path)
            if pdf_text is None:
                print(f"✗ Failed to load {pdf_file}")
                continue
            
            # Split into chunks
            chunks = split_text_into_chunks(
                pdf_text,
                chunk_size=config.CHUNK_SIZE,
                overlap=config.CHUNK_OVERLAP
            )
            
            if not chunks:
                print(f"✗ No text chunks extracted from {pdf_file}")
                continue
            
            # Generate embeddings
            print(f"  Generating embeddings for {len(chunks)} chunks...")
            embeddings = [self.embedding_manager.embed_text(chunk) for chunk in chunks]
            
            # Store in Milvus
            success = self.milvus_manager.add_embeddings(pdf_file, chunks, embeddings)
            
            if success:
                print(f"✓ Successfully processed {pdf_file}")
                processed_count += 1
            else:
                print(f"✗ Failed to store embeddings for {pdf_file}")
        
        print(f"\n📊 Processing Summary:")
        print(f"  ✓ Newly processed: {processed_count}")
        print(f"  ⏭️  Skipped (already embedded): {skipped_count}")
        print(f"  📚 Total PDF files: {len(pdf_files)}\n")
        
        return processed_count, skipped_count
    
    def add_pdf_manually(self, pdf_path):
        """
        Manually add a specific PDF file.
        
        Args:
            pdf_path: Path to the PDF file
        """
        if not os.path.exists(pdf_path):
            print(f"✗ PDF file not found: {pdf_path}")
            return False
        
        pdf_file = os.path.basename(pdf_path)
        
        # Check if already embedded
        if self.milvus_manager.check_file_exists(pdf_file):
            print(f"✓ {pdf_file} is already embedded in the database")
            return True
        
        print(f"🔄 Processing {pdf_file}...")
        
        # Extract text
        pdf_text = get_pdf_text(pdf_path)
        if pdf_text is None:
            print(f"✗ Failed to load {pdf_file}")
            return False
        
        # Split into chunks
        chunks = split_text_into_chunks(
            pdf_text,
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        
        if not chunks:
            print(f"✗ No text chunks extracted from {pdf_file}")
            return False
        
        # Generate embeddings
        print(f"  Generating embeddings for {len(chunks)} chunks...")
        embeddings = [self.embedding_manager.embed_text(chunk) for chunk in chunks]
        
        # Store in Milvus
        success = self.milvus_manager.add_embeddings(pdf_file, chunks, embeddings)
        
        if success:
            print(f"✓ Successfully processed {pdf_file}")
        else:
            print(f"✗ Failed to store embeddings for {pdf_file}")
        
        return success
    
    def get_embedded_files_count(self):
        """Get count of unique files with embeddings."""
        return len(self.milvus_manager.get_all_embedded_files())
