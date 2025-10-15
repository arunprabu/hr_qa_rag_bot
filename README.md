## Project Structure

hr-qa-bot/
├── config/ # Configuration and settings
├── src/
│ ├── vector_db/ # Cosmos DB vector database
│ ├── processors/ # PDF processing and embeddings
│ ├── agents/ # AutoGen agents
│ └── utils/ # Helper functions
├── data/ # HR documents
├── main.py # Main execution script
└── interactive.py # Interactive chat mode


## Architecture

1. **PDF Processing**: Documents are chunked and embedded using Azure OpenAI
2. **Vector Storage**: Embeddings stored in Cosmos DB with vector indexing
3. **RAG Retrieval**: User questions trigger vector similarity search
4. **Agent Response**: AutoGen assistant generates answers from retrieved context

## Environment Variables

See `.env.example` for all required configuration.

## License

MIT


Gen AI-Ready data (as of 15th Oct 2025)
======
  * files that are with selectable texts 
  * non-password protected 

Non gen-ai ready data (as of 15th Oct 2025)
====
  * PDF files with images. (with OCR )



Embedding
====
  1. Preprocessing 
    1.1. Load the document
    1.2. Opening the file 
    1.3. Extracting the text by chunks (tools like pdf extractor)
    1.4. Set the chunking overlap 
    1.5. Choose the embedding model and start embedding 
  
