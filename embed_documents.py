#!/usr/bin/env python3
"""
Document Embedding Script
Processes PDF files from the data directory and stores them in Cosmos DB.
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from src.processors.pdf_processor import PDFProcessor
from src.vector_db.vector_db.cosmos_vector_db import CosmosVectorDB


def main():
    """Main embedding pipeline."""
    print("\n" + "="*70)
    print("HR DOCUMENT EMBEDDING PIPELINE")
    print("="*70 + "\n")
    
    # Initialize PDF Processor
    print("📋 Initializing PDF Processor...")
    pdf_processor = PDFProcessor(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        azure_api_key=settings.AZURE_OPENAI_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        embedding_model=settings.EMBEDDING_MODEL_DEPLOYMENT
    )
    
    # Initialize Cosmos DB for MongoDB vCore
    print("🗄️  Initializing Cosmos DB MongoDB vCore Vector Store...")
    cosmos_db = CosmosVectorDB(
        connection_string=settings.COSMOS_CONNECTION_STRING,
        database_name=settings.COSMOS_DATABASE_NAME,
        collection_name=settings.COSMOS_COLLECTION_NAME,
        embedding_dimensions=settings.EMBEDDING_DIMENSIONS,
        vector_index_type=settings.VECTOR_INDEX_TYPE
    )
    
    # Find all PDF files in data directory
    data_dir = settings.DATA_DIR
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"⚠️  No PDF files found in {data_dir}")
        return
    
    print(f"\n📁 Found {len(pdf_files)} PDF file(s) to process:\n")
    for pdf_file in pdf_files:
        print(f"   • {pdf_file.name}")
    print()
    
    # Process each PDF
    total_documents = 0
    
    for pdf_file in pdf_files:
        # Process PDF into chunks with embeddings
        documents = pdf_processor.process_pdf(
            pdf_path=str(pdf_file),
            chunk_size=settings.CHUNK_SIZE,
            overlap=settings.CHUNK_OVERLAP
        )
        
        if documents:
            # Insert into Cosmos DB
            print(f"💾 Storing {len(documents)} documents in Cosmos DB...")
            inserted = cosmos_db.insert_documents(documents)
            total_documents += inserted
            print(f"✓ Successfully stored {inserted} documents\n")
        else:
            print(f"⚠️  No documents created from {pdf_file.name}\n")
    
    # Summary
    print("\n" + "="*70)
    print(f"✅ EMBEDDING COMPLETE")
    print(f"   Total documents embedded: {total_documents}")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
