
"""
Azure Cosmos DB for MongoDB vCore Vector Database implementation.

This module provides vector search capabilities using MongoDB vCore API with vector indexes.
Vector search enables semantic similarity search for RAG (Retrieval-Augmented Generation).
"""
import hashlib
from typing import List, Dict, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure


class CosmosVectorDB:
    """
    Vector database for storing and retrieving document embeddings.
    
    Uses Azure Cosmos DB for MongoDB vCore with vector search capabilities:
    - Stores document chunks with 1536-dimensional embedding vectors
    - Performs cosine similarity search for semantic matching
    - Supports HNSW, IVF, and DiskANN vector index types
    
    Compatible with AutoGen v0.7.5 architecture.
    """
    
    def __init__(
        self,
        connection_string: str,
        database_name: str,
        collection_name: str,
        embedding_dimensions: int = 1536,
        vector_index_type: str = "vector-hnsw"
    ):
        """
        Initialize Cosmos DB for MongoDB vCore vector database connection.
        
        Args:
            connection_string: MongoDB vCore connection string from Azure Portal
            database_name: Name of database (will be created if doesn't exist)
            collection_name: Name of collection for storing embedded documents
            embedding_dimensions: Vector dimensions (1536 for text-embedding-ada-002)
            vector_index_type: Index type for vector search:
                - 'vector-hnsw': Hierarchical Navigable Small World (recommended)
                - 'vector-ivf': Inverted File Index (fast but less accurate)
                - 'vector-diskann': DiskANN (for very large datasets)
        """
        try:
            # Connect to MongoDB vCore
            self.client = MongoClient(connection_string)
            
            # Test connection
            self.client.admin.command('ping')
            
            # Get database and collection
            self.database = self.client[database_name]
            self.collection = self.database[collection_name]
            self.embedding_dimensions = embedding_dimensions
            self.vector_index_type = vector_index_type
            
            # Create vector index if it doesn't exist
            self._create_vector_index()
            
            print(f"✓ Cosmos DB MongoDB vCore collection '{collection_name}' ready with vector search")
            
        except ConnectionFailure as e:
            print(f"✗ Failed to connect to Cosmos DB MongoDB vCore: {e}")
            raise
        except Exception as e:
            print(f"✗ Error initializing Cosmos DB: {e}")
            raise
    
    def _create_vector_index(self):
        """
        Create vector search index on contentVector field for similarity search.
        
        The vector index enables fast approximate nearest neighbor (ANN) search
        using cosine similarity. This is essential for RAG document retrieval.
        """
        try:
            # Check if vector index already exists
            existing_indexes = list(self.collection.list_indexes())
            index_names = [idx['name'] for idx in existing_indexes]
            
            if 'vectorSearchIndex' in index_names:
                print(f"✓ Vector index already exists")
                return
            
            # Create vector index using MongoDB cosmosSearch
            vector_index = {
                "name": "vectorSearchIndex",
                "key": {
                    "contentVector": "cosmosSearch"  # Field containing embedding vectors
                },
                "cosmosSearchOptions": {
                    "kind": self.vector_index_type,  # HNSW/IVF/DiskANN
                    "numLists": 100,  # Number of clusters for IVF index
                    "similarity": "COS",  # Cosine similarity metric
                    "dimensions": self.embedding_dimensions  # Vector dimensions (1536)
                }
            }
            
            self.collection.create_index(
                [("contentVector", "cosmosSearch")],
                name="vectorSearchIndex",
                cosmosSearchOptions={
                    "kind": self.vector_index_type,
                    "numLists": 100,
                    "similarity": "COS",
                    "dimensions": self.embedding_dimensions
                }
            )
            
            print(f"✓ Created vector index: {self.vector_index_type}")
            
        except OperationFailure as e:
            # Index might already exist or creation in progress
            print(f"ℹ️  Vector index note: {e}")
        except Exception as e:
            print(f"⚠️  Could not create vector index: {e}")
            print(f"   You may need to create it manually in Azure Portal")
    
    def insert_documents(self, documents: List[Dict[str, Any]]) -> int:
        """
        Insert document chunks with embeddings into MongoDB collection.
        
        Each document should have structure:
        {
            "content": "Text chunk",
            "contentVector": [0.123, -0.456, ...],  # 1536-dim embedding
            "metadata": {"source": "filename.pdf", "chunk_id": 0, ...}
        }
        
        Args:
            documents: List of document dictionaries with content and embeddings
            
        Returns:
            Number of documents successfully inserted/updated
        """
        inserted_count = 0
        
        for doc in documents:
            try:
                # Generate unique ID based on content hash if not present
                if "_id" not in doc:
                    content_hash = hashlib.md5(
                        doc.get("content", "").encode()
                    ).hexdigest()
                    doc["_id"] = f"doc_{content_hash}"
                
                # Upsert: replace if ID exists, insert if new
                # This prevents duplicate documents with same content
                self.collection.replace_one(
                    {"_id": doc["_id"]},
                    doc,
                    upsert=True
                )
                inserted_count += 1
                
            except Exception as e:
                print(f"✗ Error inserting document: {e}")
                continue
        
        print(f"✓ Inserted/Updated {inserted_count} documents")
        return inserted_count
    
    def search(
        self, 
        query_embedding: List[float], 
        top_k: int = 5,
        similarity_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic similarity search using vector embeddings.
        
        This is the core retrieval step in RAG:
        1. Takes question embedding (1536-dim vector)
        2. Finds most similar document embeddings using cosine similarity
        3. Returns top-k matching documents with relevance scores
        
        Args:
            query_embedding: Question embedding vector (1536 dimensions)
            top_k: Number of most relevant results to return (default: 5)
            similarity_threshold: Minimum similarity score 0-1 (0=filter off)
            
        Returns:
            List of documents sorted by relevance, each containing:
            - content: Text chunk
            - metadata: Source info (filename, chunk_id, etc.)
            - similarity: Relevance score (higher = more relevant)
        """
        try:
            # MongoDB aggregation pipeline for vector search
            pipeline = [
                {
                    "$search": {
                        "cosmosSearch": {
                            "vector": query_embedding,  # Query vector (1536-dim)
                            "path": "contentVector",     # Field to search
                            "k": top_k                   # Number of results
                        },
                        "returnStoredSource": True      # Include document content
                    }
                },
                {
                    "$project": {
                        "_id": 1,
                        "content": 1,                    # Text chunk
                        "metadata": 1,                   # Source information
                        "similarity": {"$meta": "searchScore"}  # Relevance score
                    }
                }
            ]
            
            # Execute vector search
            results = list(self.collection.aggregate(pipeline))
            
            # Optional: Filter by minimum similarity score
            if similarity_threshold > 0.0:
                results = [
                    doc for doc in results 
                    if doc.get("similarity", 0.0) >= similarity_threshold
                ]
            
            return results
            
        except Exception as e:
            print(f"✗ Error during vector search: {e}")
            print(f"   Make sure vector index 'vectorSearchIndex' exists in Azure Portal")
            return []
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document by ID.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            result = self.collection.delete_one({"_id": doc_id})
            if result.deleted_count > 0:
                return True
            else:
                print(f"Document {doc_id} not found")
                return False
        except Exception as e:
            print(f"✗ Error deleting document: {e}")
            return False
    
    def close(self):
        """Close MongoDB connection."""
        try:
            self.client.close()
        except Exception:
            pass
