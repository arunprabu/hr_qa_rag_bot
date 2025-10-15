# HR Q&A Bot - Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Configure Your Credentials

Edit the `.env` file with your Azure credentials:

```bash
# Open .env file
nano .env  # or use any text editor

# Update these values:
COSMOS_CONNECTION_STRING=mongodb+srv://username:password@your-cluster.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com/
AZURE_OPENAI_KEY=YOUR-AZURE-OPENAI-KEY
```

### Step 2: Embed Your Documents

Process the HR documents in the `data/` folder:

```bash
# Activate virtual environment (if not already active)
source .venv/bin/activate

# Run embedding script
python embed_documents.py
```

**Expected Output:**
```
======================================================================
HR DOCUMENT EMBEDDING PIPELINE
======================================================================

📋 Initializing PDF Processor...
🗄️  Initializing Cosmos DB Vector Store...
✓ Cosmos DB container 'hr_policies' ready with vector search

📁 Found 1 PDF file(s) to process:
   • HR_Support_Desk_KnowledgeBase.pdf

============================================================
Processing: HR_Support_Desk_KnowledgeBase.pdf
============================================================
📄 Extracting text from HR_Support_Desk_KnowledgeBase.pdf (X pages)...
✓ Extracted XXXX characters
✓ Created XX chunks
Generating embedding XX/XX...
✓ Created XX documents with embeddings

💾 Storing XX documents in Cosmos DB...
✓ Successfully stored XX documents

======================================================================
✅ EMBEDDING COMPLETE
   Total documents embedded: XX
======================================================================
```

### Step 3: Start Asking Questions!

**Interactive Mode (Best for multiple questions):**

```bash
python interactive.py
```

Then type your questions:
```
❓ Your question: What is the leave policy?
❓ Your question: How do I request time off?
❓ Your question: What are the medical benefits?
❓ Your question: quit
```

**Single Question Mode:**

```bash
python main.py "What is the leave policy?"
```

## 📋 Example Questions You Can Ask

- "What is the company leave policy?"
- "How do I apply for medical benefits?"
- "What are the working hours?"
- "How do I request time off?"
- "What is the dress code?"
- "What holidays does the company observe?"
- "How do performance reviews work?"
- "What is the remote work policy?"

## 🔧 Troubleshooting

### Error: Missing environment variables

**Solution:** Make sure your `.env` file has all required values filled in (not placeholders).

### Error: No PDF files found

**Solution:** Ensure your PDF files are in the `data/` directory:
```bash
ls data/*.pdf
```

### Error: Connection to Cosmos DB failed

**Solution:** 
1. Verify your `COSMOS_CONNECTION_STRING` in `.env`
2. Check your Azure Cosmos DB MongoDB vCore firewall settings
3. Ensure your IP address is allowed in Azure Portal
4. Make sure the vector index is created

### Error: Azure OpenAI authentication failed

**Solution:**
1. Verify your `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_KEY`
2. Ensure your models are deployed in Azure OpenAI Studio
3. Check that deployment names match your `.env` settings

## 📊 Project Files Overview

| File | Purpose |
|------|---------|
| `embed_documents.py` | Processes PDFs and stores embeddings |
| `interactive.py` | Interactive Q&A chat interface |
| `main.py` | Single-question command-line tool |
| `config/settings.py` | Configuration management |
| `src/processors/pdf_processor.py` | PDF text extraction & chunking |
| `src/vector_db/vector_db/cosmos_vector_db.py` | Cosmos DB vector operations |
| `src/agents/hr_agents.py` | AutoGen RAG agent |

## 🎯 Next Steps

1. ✅ Configure credentials in `.env`
2. ✅ Run `python embed_documents.py`
3. ✅ Start chatting with `python interactive.py`
4. 🚀 Add more HR documents to `data/` folder and re-run embedding

## 💡 Tips

- **Re-embedding**: If you add new PDFs, just run `embed_documents.py` again
- **Context**: The bot retrieves the top 5 most relevant document chunks for each question
- **Accuracy**: Answers are based only on your HR documents - the bot won't make up information
- **Chunking**: Documents are split into 1000-character chunks with 200-character overlap for better context

---

Need help? Check the full README.md for detailed documentation.
