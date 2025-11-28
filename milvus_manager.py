from pymilvus import connections, utility, Collection, FieldSchema, CollectionSchema, DataType
import config
import uuid
import time

class MilvusManager:
    """Manages Milvus connection and vector operations."""

    def __init__(self):
        self.collection_name = config.MILVUS_COLLECTION_NAME
        self.db_name = config.MILVUS_DB_NAME
        self.collection = None

        self._connect_with_retry()
        self._setup_collection()

    def _connect_with_retry(self, retries=15, delay=2):
        """Retry Milvus connection for stability (HF Spaces cold starts)."""
        for attempt in range(1, retries + 1):
            try:
                connections.connect(
                    alias="default",
                    uri=config.MILVUS_ENDPOINT,
                    user=config.MILVUS_USERNAME,
                    password=config.MILVUS_PASSWORD
                )
                print("✓ Connected to Milvus")
                return
            except Exception as e:
                print(f"⚠️ Milvus connection failed (attempt {attempt}): {e}")
                time.sleep(delay)
        raise RuntimeError("❌ Could not connect to Milvus after retries")

    def _setup_collection(self):
        """Create or load Milvus collection."""
        try:
            if self.collection_name not in utility.list_collections():
                fields = [
                    FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=256, is_primary=True),
                    FieldSchema(name="file_name", dtype=DataType.VARCHAR, max_length=512),
                    FieldSchema(name="chunk_index", dtype=DataType.INT64),
                    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
                    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=config.EMBEDDING_DIMENSION),
                ]

                schema = CollectionSchema(fields=fields, description="Document embedding store")
                self.collection = Collection(name=self.collection_name, schema=schema)
                print("✓ Created new collection:", self.collection_name)

            else:
                self.collection = Collection(name=self.collection_name)
                print(f"✓ Loaded existing collection: {self.collection_name}")

            self._create_index()

        except Exception as e:
            print(f"✗ Error setting up collection: {e}")
            raise

    def _create_index(self):
        """Ensure index exists and load the collection."""
        try:
            index_params = {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024},
            }

            try:
                self.collection.create_index("embedding", index_params)
                print("✓ Created index")
            except Exception:
                print("ℹ️ Index exists, skipping")

            try:
                self.collection.load()
            except Exception as e:
                print("⚠️ Could not load collection into memory:", e)

        except Exception as e:
            print("✗ Error creating index:", e)
            raise

    def add_embeddings(self, file_name, chunks, embeddings):
        """Insert chunk + embedding rows."""
        try:
            ids = [str(uuid.uuid4()) for _ in chunks]
            file_names = [file_name] * len(chunks)
            indices = list(range(len(chunks)))
            embeds = [e.tolist() for e in embeddings]

            data = [ids, file_names, indices, chunks, embeds]
            self.collection.insert(data)
            self.collection.flush()

            print(f"✓ Inserted {len(chunks)} chunks for {file_name}")
            return True

        except Exception as e:
            print(f"✗ Error inserting embeddings: {e}")
            return False

    def search_embeddings(self, vec, n=5):
        try:
            query_vec = vec.tolist()
            params = {"metric_type": "L2", "params": {"nprobe": 10}}

            results = self.collection.search(
                data=[query_vec],
                anns_field="embedding",
                param=params,
                limit=n,
                output_fields=["file_name", "chunk_index", "text"]
            )

            formatted = []
            for hit in results[0]:
                formatted.append({
                    "id": hit.id,
                    "document": hit.entity.get("text"),
                    "file_name": hit.entity.get("file_name"),
                    "chunk_index": hit.entity.get("chunk_index"),
                    "score": hit.distance
                })

            return formatted

        except Exception as e:
            print(f"✗ Search error: {e}")
            return []

    def get_all_embedded_files(self):
        try:
            results = self.collection.query(expr="file_name != ''", output_fields=["file_name"])
            return {r["file_name"] for r in results}
        except:
            return set()

    def close_connection(self):
        connections.disconnect("default")
        print("✓ Disconnected Milvus")
