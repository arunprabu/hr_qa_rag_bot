# HR Q&A Bot - RAG System with Azure Cosmos DB

An intelligent HR assistant that uses Retrieval-Augmented Generation (RAG) to answer employee questions about HR policies, benefits, and procedures.

## 🎯 Features

- **RAG Architecture**: Combines vector search with LLM generation for accurate answers
- **Azure Cosmos DB**: Vector storage with similarity search capabilities
- **Azure OpenAI**: Embeddings and chat completion
- **AutoGen Framework**: Multi-agent orchestration for complex interactions
- **Command-Line Interface**: Easy-to-use interactive bot

## 📋 Tech Stack

- **Python**: 3.10+
- **Agent Framework**: AutoGen 0.7.5 (modern multi-agent API)
- **LLM**: Azure OpenAI (GPT-4)
- **Vector DB**: Azure Cosmos DB for MongoDB vCore
- **Embedding Model**: text-embedding-ada-002 (1536 dimensions)
- **Text Extraction**: PyPDF2
- **Chunk Size**: 1000 characters
- **Overlap Size**: 200 characters

## 🏗️ Project Structure

```
hr-qa-bot/
├── config/
│   └── settings.py          # Configuration management
├── src/
│   ├── agents/
│   │   └── hr_agents.py     # AutoGen HR assistant agent
│   ├── processors/
│   │   └── pdf_processor.py # PDF processing & embeddings
│   └── vector_db/
│       └── vector_db/
│           └── cosmos_vector_db.py  # Cosmos DB vector store
├── data/
│   └── *.pdf                # HR documents to embed
├── embed_documents.py       # Document embedding script
├── interactive.py           # Interactive chat interface
├── main.py                  # Single-question CLI
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not in git)
└── .env.example            # Example environment config
```

## 🚀 Setup Instructions

### 1. Prerequisites

- Python 3.10 or higher
- Azure account with:
  - Azure Cosmos DB for MongoDB vCore cluster
  - Azure OpenAI resource with deployed models

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

Required environment variables:
- `COSMOS_CONNECTION_STRING`: Your MongoDB vCore connection string
- `COSMOS_DATABASE_NAME`: Database name (default: hr_knowledge_base)
- `COSMOS_COLLECTION_NAME`: Collection name (default: hr_policies)
- `VECTOR_INDEX_TYPE`: Vector index type (vector-hnsw, vector-ivf, or vector-diskann)
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
- `AZURE_OPENAI_KEY`: Your Azure OpenAI API key
- `EMBEDDING_MODEL_DEPLOYMENT`: Name of your embedding model deployment
- `CHAT_MODEL_DEPLOYMENT`: Name of your chat model deployment

### 4. Prepare Your Data

Place your HR policy PDF documents in the `data/` directory:

```bash
cp your-hr-document.pdf data/
```

## 📝 Usage

### Step 1: Embed Documents

First, process and embed your HR documents:

```bash
python embed_documents.py
```

This will:
- Extract text from PDFs in the `data/` folder
- Split text into chunks (1000 chars, 200 overlap)
- Generate embeddings using Azure OpenAI
- Store vectors in Cosmos DB

### Step 2: Ask Questions

**Interactive Mode** (Recommended):

```bash
python interactive.py
```

Then type your questions:
```
❓ Your question: What is the leave policy?
❓ Your question: How do I apply for medical benefits?
❓ Your question: quit
```

**Single Question Mode**:

```bash
python main.py "What is the leave policy?"
```

## 🏛️ Architecture

### RAG Pipeline

1. **Document Ingestion** (`embed_documents.py`)
   - Load PDFs from `data/` folder
   - Extract text using PyPDF2
   - Chunk text with overlap
   - Generate embeddings via Azure OpenAI
   - Store in Cosmos DB MongoDB vCore with vector index

2. **Query Processing** (`interactive.py`, `main.py`)
   - User asks a question
   - Generate question embedding
   - Vector similarity search using MongoDB aggregation pipeline
   - Retrieve top-k relevant chunks
   - Pass context to AutoGen agent
   - Generate natural language answer

### Components

- **PDFProcessor**: Handles PDF text extraction, chunking, and embedding generation
- **CosmosVectorDB**: Vector database operations (insert, search)
- **HRAssistantTeam**: AutoGen agent that generates answers from context

## 🔧 Configuration

Edit `config/settings.py` or `.env` to customize:

- `CHUNK_SIZE`: Size of text chunks (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)
- `EMBEDDING_DIMENSIONS`: Vector dimensions (default: 1536 for Ada-002)
- `COSMOS_DATABASE_NAME`: Database name (default: hr_knowledge_base)
- `COSMOS_COLLECTION_NAME`: Collection name (default: hr_policies)
- `VECTOR_INDEX_TYPE`: Vector index type (default: vector-hnsw)

## 📊 Data Requirements

### Gen AI-Ready Data
- PDF files with selectable text
- Non-password protected documents
- Clear, well-structured content

### Non Gen AI-Ready Data (Requires OCR)
- Scanned documents
- Image-based PDFs
- Handwritten content

## 🐛 Troubleshooting

**Import Errors**:
```bash
# Make sure you're in the project root and venv is activated
cd /path/to/hr_qa_bot
source .venv/bin/activate
```

**Missing Environment Variables**:
```bash
# Check your .env file has all required variables
cat .env
```

**No Documents Found**:
```bash
# Ensure PDFs are in the data/ folder
ls data/*.pdf
```

**Cosmos DB Connection Issues**:
- Verify your COSMOS_CONNECTION_STRING
- Check firewall rules in Azure Portal
- Ensure your IP is allowed in the MongoDB vCore cluster
- Make sure vector index is created (see Azure Portal)

## 📄 License

MIT

## 🤝 Contributing

This is a training project for Cognizant Corporate Training.

---

**Last Updated**: 15 October 2025





