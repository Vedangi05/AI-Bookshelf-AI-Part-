from pymilvus import connections, utility, Collection, FieldSchema, CollectionSchema, DataType
import config
import uuid


class MilvusManager:
    """Manages connections and operations with Milvus vector database."""
    
    def __init__(self):
        """Initialize Milvus connection and setup collection."""
        self.collection_name = config.MILVUS_COLLECTION_NAME
        self.db_name = config.MILVUS_DB_NAME
        self._connect()
        self._setup_collection()
    
    def _connect(self):
        """Establish connection to Milvus."""
        try:
            connections.connect(
                alias="default",
                uri=config.MILVUS_ENDPOINT,
                user=config.MILVUS_USERNAME,
                password=config.MILVUS_PASSWORD
            )
            print("✓ Connected to Milvus successfully")
        except Exception as e:
            print(f"✗ Error connecting to Milvus: {e}")
            raise
    
    def _setup_collection(self):
        """Create collection if it doesn't exist."""
        try:
            # Check if collection exists (use utility.list_collections)
            existing_collections = utility.list_collections()

            if self.collection_name not in existing_collections:
                # Define schema for the collection
                fields = [
                    FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=256, is_primary=True),
                    FieldSchema(name="file_name", dtype=DataType.VARCHAR, max_length=512),
                    FieldSchema(name="chunk_index", dtype=DataType.INT64),
                    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=config.EMBEDDING_DIMENSION),
                ]
                
                schema = CollectionSchema(
                    fields=fields,
                    description="Document embeddings collection"
                )
                
                # Create collection
                self.collection = Collection(
                    name=self.collection_name,
                    schema=schema
                )
                print(f"✓ Created new collection: {self.collection_name}")
            else:
                self.collection = Collection(name=self.collection_name)
                print(f"✓ Collection '{self.collection_name}' already exists")
            # Create index if it doesn't exist (best-effort)
            self._create_index_if_needed()
            
        except Exception as e:
            print(f"✗ Error setting up collection: {e}")
            raise
    
    def _create_index_if_needed(self):
        """Create index for vector field if it doesn't exist."""
        try:
            # Attempt to create index; if it already exists, ignore the error
            index_params = {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }

            try:
                # create_index will raise if an identical index already exists
                self.collection.create_index(
                    field_name="embedding",
                    index_params=index_params
                )
                print("✓ Created index for embedding field")
            except Exception as ie:
                # If index exists or creation failed for a benign reason, log and continue
                print(f"ℹ️  Index creation skipped or failed (may already exist): {ie}")

            # Load collection into memory (best effort)
            try:
                self.collection.load()
            except Exception as le:
                print(f"ℹ️  Could not load collection into memory immediately: {le}")
        except Exception as e:
            print(f"✗ Error creating index: {e}")
            raise
    
    def check_file_exists(self, file_name):
        """Check if a PDF file has already been embedded."""
        try:
            # Search for documents with this file_name
            results = self.collection.query(
                expr=f'file_name == "{file_name}"',
                output_fields=["file_name"]
            )
            return len(results) > 0
        except Exception as e:
            print(f"✗ Error checking file existence: {e}")
            return False
    
    def add_embeddings(self, file_name, chunks, embeddings):
        """
        Add document chunks and their embeddings to Milvus.
        
        Args:
            file_name: Name of the PDF file
            chunks: List of text chunks
            embeddings: List of embedding vectors (numpy arrays)
        """
        try:
            if len(chunks) != len(embeddings):
                raise ValueError("Number of chunks must match number of embeddings")
            
            # Prepare data for insertion
            ids = [str(uuid.uuid4()) for _ in chunks]
            file_names = [file_name] * len(chunks)
            chunk_indices = list(range(len(chunks)))
            
            # Convert embeddings to list of lists if they are numpy arrays
            embeddings_list = [emb.tolist() if hasattr(emb, 'tolist') else emb for emb in embeddings]
            
            data = [
                ids,
                file_names,
                chunk_indices,
                chunks,
                embeddings_list
            ]
            
            # Insert data
            self.collection.insert(data)
            self.collection.flush()
            
            print(f"✓ Added {len(chunks)} chunks for file: {file_name}")
            return True
        except Exception as e:
            print(f"✗ Error adding embeddings: {e}")
            return False
    
    def search_embeddings(self, query_embedding, n_results=5):
        """
        Search for similar embeddings in Milvus.
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            
        Returns:
            List of search results with documents and scores
        """
        try:
            # Convert numpy array to list if needed
            query_vector = query_embedding.tolist() if hasattr(query_embedding, 'tolist') else query_embedding
            
            search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
            
            results = self.collection.search(
                data=[query_vector],
                anns_field="embedding",
                param=search_params,
                limit=n_results,
                output_fields=["file_name", "chunk_index", "text"]
            )
            
            # Format results
            formatted_results = []
            for hit in results[0]:
                formatted_results.append({
                    "id": hit.id,
                    "document": hit.entity.text,
                    "file_name": hit.entity.file_name,
                    "chunk_index": hit.entity.chunk_index,
                    "score": hit.distance
                })
            
            return formatted_results
        except Exception as e:
            print(f"✗ Error searching embeddings: {e}")
            return []
    
    def get_all_embedded_files(self):
        """Get a set of all file names that have embeddings in Milvus."""
        try:
            results = self.collection.query(
                expr="file_name != ''",
                output_fields=["file_name"]
            )
            
            file_names = set()
            for result in results:
                file_names.add(result['file_name'])
            
            return file_names
        except Exception as e:
            print(f"✗ Error getting embedded files: {e}")
            return set()
    
    def close_connection(self):
        """Close connection to Milvus."""
        try:
            connections.disconnect(alias="default")
            print("✓ Disconnected from Milvus")
        except Exception as e:
            print(f"✗ Error disconnecting from Milvus: {e}")
