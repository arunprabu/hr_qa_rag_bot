#!/usr/bin/env python3
"""
Interactive HR Q&A Bot
Command-line interface for querying the HR knowledge base.
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


async def main():
    """Interactive Q&A session."""
    print("\n" + "="*70)
    print("🤖 HR ASSISTANT BOT - Interactive Mode")
    print("="*70)
    print("\nInitializing system...")
    
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
    
    print("\n✅ System ready! You can now ask questions about HR policies.\n")
    print("Commands:")
    print("  • Type your question to get an answer")
    print("  • Type 'quit' or 'exit' to end the session")
    print("  • Press Ctrl+C to interrupt\n")
    print("="*70 + "\n")
    
    # Interactive loop
    try:
        while True:
            # Get user question
            question = input("❓ Your question: ").strip()
            
            if not question:
                continue
            
            # Check for exit commands
            if question.lower() in ['quit', 'exit', 'bye', 'q']:
                print("\n👋 Thank you for using HR Assistant Bot. Goodbye!\n")
                break
            
            # Process question
            try:
                answer = await hr_team.ask_question(question, top_k=5)
                print()  # Extra newline for spacing
                
            except Exception as e:
                print(f"\n❌ Error processing question: {e}\n")
                continue
    
    except KeyboardInterrupt:
        print("\n\n👋 Session interrupted. Goodbye!\n")
    
    finally:
        # Cleanup
        await hr_team.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
