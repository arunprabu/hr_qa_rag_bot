#!/usr/bin/env python3
"""
Configuration Test Script
Verifies that all environment variables are set correctly.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*70)
print("🔍 HR Q&A Bot - Configuration Test")
print("="*70 + "\n")

try:
    from config import settings
    
    print("✅ Configuration loaded successfully!\n")
    
    # Check Cosmos DB settings
    print("Azure Cosmos DB for MongoDB vCore:")
    conn_str = settings.COSMOS_CONNECTION_STRING
    if conn_str:
        # Mask password in connection string
        if '@' in conn_str:
            parts = conn_str.split('@')
            prefix = parts[0].split('://')[0] + '://***:***'
            masked = prefix + '@' + parts[1]
            print(f"   Connection: {masked[:60]}...")
        else:
            print(f"   Connection: {conn_str[:60]}...")
    else:
        print("   ❌ Connection string not configured")
    print(f"   Database: {settings.COSMOS_DATABASE_NAME}")
    print(f"   Collection: {settings.COSMOS_COLLECTION_NAME}")
    print(f"   Vector Index Type: {settings.VECTOR_INDEX_TYPE}\n")
    
    # Check Azure OpenAI settings
    print("Azure OpenAI:")
    print(f"   Endpoint: {settings.AZURE_OPENAI_ENDPOINT[:50]}..." if settings.AZURE_OPENAI_ENDPOINT else "   ❌ Not configured")
    print(f"   Key: {'*' * 20}...{settings.AZURE_OPENAI_KEY[-4:] if settings.AZURE_OPENAI_KEY and len(settings.AZURE_OPENAI_KEY) > 4 else '❌ Not configured'}")
    print(f"   API Version: {settings.AZURE_OPENAI_API_VERSION}")
    print(f"   Embedding Model: {settings.EMBEDDING_MODEL_DEPLOYMENT}")
    print(f"   Chat Model: {settings.CHAT_MODEL_DEPLOYMENT}\n")
    
    # Check processing settings
    print("Document Processing:")
    print(f"   Chunk Size: {settings.CHUNK_SIZE}")
    print(f"   Chunk Overlap: {settings.CHUNK_OVERLAP}")
    print(f"   Embedding Dimensions: {settings.EMBEDDING_DIMENSIONS}\n")
    
    # Check data directory
    print("Data Directory:")
    pdf_files = list(settings.DATA_DIR.glob("*.pdf"))
    if pdf_files:
        print(f"   ✅ Found {len(pdf_files)} PDF file(s):")
        for pdf in pdf_files:
            print(f"      • {pdf.name}")
    else:
        print(f"   ⚠️  No PDF files found in {settings.DATA_DIR}")
    
    print("\n" + "="*70)
    print("✅ Configuration test complete!")
    print("="*70 + "\n")
    
    print("Next steps:")
    print("   1. If credentials show ❌, update your .env file")
    print("   2. Add PDF files to the data/ directory if none found")
    print("   3. Run: python embed_documents.py")
    print("   4. Run: python interactive.py\n")

except ValueError as e:
    print(f"❌ Configuration Error:\n   {e}\n")
    print("Please check your .env file and ensure all required variables are set.")
    print("See .env.example for reference.\n")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected Error:\n   {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)
