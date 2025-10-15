#!/usr/bin/env python3
"""
HR Q&A Bot - Main Entry Point
Provides both single-question and interactive modes.
"""
import os
import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from src.processors.pdf_processor import PDFProcessor
from src.vector_db.vector_db.cosmos_vector_db import CosmosVectorDB
from src.agents.hr_agents import HRAssistantTeam


async def ask_single_question(question: str):
    """Ask a single question and exit."""
    print("\n🤖 HR Assistant Bot - Single Question Mode\n")
    
    # Initialize components
    pdf_processor = PDFProcessor(
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        azure_api_key=settings.AZURE_OPENAI_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        embedding_model=settings.EMBEDDING_MODEL_DEPLOYMENT
    )
    
    cosmos_db = CosmosVectorDB(
        connection_string=settings.COSMOS_CONNECTION_STRING,
        database_name=settings.COSMOS_DATABASE_NAME,
        collection_name=settings.COSMOS_COLLECTION_NAME,
        embedding_dimensions=settings.EMBEDDING_DIMENSIONS,
        vector_index_type=settings.VECTOR_INDEX_TYPE
    )
    
    hr_team = HRAssistantTeam(
        cosmos_db=cosmos_db,
        pdf_processor=pdf_processor,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        azure_deployment=settings.CHAT_MODEL_DEPLOYMENT,
        api_key=settings.AZURE_OPENAI_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION
    )
    
    try:
        answer = await hr_team.ask_question(question, top_k=5)
        return answer
    finally:
        await hr_team.close()


def print_usage():
    """Print usage information."""
    print("""
HR Q&A Bot - Usage:

1. Single Question Mode:
   python main.py "What is the leave policy?"

2. Interactive Mode:
   python interactive.py

3. Embed Documents:
   python embed_documents.py

Environment:
   Make sure your .env file is configured with:
   - COSMOS_ENDPOINT
   - COSMOS_KEY
   - AZURE_OPENAI_ENDPOINT
   - AZURE_OPENAI_KEY
   - Other settings (see .env.example)
""")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("\n⚠️  No question provided!")
        print_usage()
        sys.exit(1)
    
    # Get question from command line
    question = " ".join(sys.argv[1:])
    
    try:
        asyncio.run(ask_single_question(question))
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
