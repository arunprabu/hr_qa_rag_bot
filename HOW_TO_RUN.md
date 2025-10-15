# 🚀 How to Run the HR Q&A Bot

Quick guide to get the bot running in 5 minutes!

---

## Prerequisites Checklist

Before running, make sure you have:
- ✅ Python 3.10 or higher installed
- ✅ Azure Cosmos DB for MongoDB vCore cluster created
- ✅ Azure OpenAI resource with deployed models:
  - `text-embedding-ada-002` (for embeddings)
  - `gpt-4o` or `gpt-4` (for chat)

---

## Step-by-Step Instructions

### **Step 1: Set Up Python Environment**

```bash
# Navigate to project directory
cd "/Users/arun/Documents/RamSELabs/Corporate Training/Course Materials/cognizant/hr_qa_bot"

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

### **Step 2: Configure Credentials**

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your credentials
nano .env
```

**Required Variables to Update:**

```bash
# Azure Cosmos DB for MongoDB vCore
COSMOS_CONNECTION_STRING=mongodb+srv://username:password@your-cluster.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key-here

# Model deployment names (from Azure OpenAI Studio)
EMBEDDING_MODEL_DEPLOYMENT=text-embedding-ada-002
CHAT_MODEL_DEPLOYMENT=gpt-4o
```

**How to Get These Values:**

1. **Cosmos DB Connection String**: 
   - Azure Portal → Your Cosmos DB MongoDB vCore Account → Connection strings
   
2. **OpenAI Endpoint & Key**: 
   - Azure Portal → Your Azure OpenAI Resource → Keys and Endpoint

3. **Model Deployment Names**: 
   - Azure OpenAI Studio → Deployments → Copy your deployment names

---

### **Step 3: Verify Configuration**

```bash
# Test your configuration
python test_config.py
```

**Expected Output:**
```
✅ Configuration loaded successfully!

Azure Cosmos DB for MongoDB vCore:
   Connection: mongodb+srv://***:***@...
   Database: hr_knowledge_base
   Collection: hr_policies

Azure OpenAI:
   Endpoint: https://your-resource.openai.azure.com/...
   Key: ********************...xxxx
   
✅ Configuration test complete!
```

---

### **Step 4: Prepare Your Data**

Place your HR policy PDF files in the `data/` folder:

```bash
# The project already has a sample file
ls data/
# Should show: HR_Support_Desk_KnowledgeBase.pdf

# Add more PDFs if you have them
cp /path/to/your/hr-policy.pdf data/
```

---

### **Step 5: Embed Documents**

This processes your PDFs and stores them in the vector database:

```bash
python embed_documents.py
```

**What Happens:**
1. ✅ Extracts text from PDFs
2. ✅ Splits into 1000-character chunks with 200-char overlap
3. ✅ Generates 1536-dimensional embeddings
4. ✅ Stores in Cosmos DB with vector index

**Expected Output:**
```
======================================================================
HR DOCUMENT EMBEDDING PIPELINE
======================================================================

📋 Initializing PDF Processor...
🗄️  Initializing Cosmos DB MongoDB vCore Vector Store...
✓ Cosmos DB MongoDB vCore collection 'hr_policies' ready with vector search

📁 Found 1 PDF file(s) to process:
   • HR_Support_Desk_KnowledgeBase.pdf

============================================================
Processing: HR_Support_Desk_KnowledgeBase.pdf
============================================================
📄 Extracting text from HR_Support_Desk_KnowledgeBase.pdf (XX pages)...
✓ Extracted XXXXX characters
✓ Created XX chunks
Generating embedding XX/XX...
✓ Created XX documents with embeddings

💾 Storing XX documents in Cosmos DB...
✓ Inserted/Updated XX documents
✓ Successfully stored XX documents

======================================================================
✅ EMBEDDING COMPLETE
   Total documents embedded: XX
======================================================================
```

---

### **Step 6: Start Chatting!**

You have two options:

#### **Option A: Interactive Mode (Recommended)**

```bash
python interactive.py
```

**Usage:**
```
==================================================================
🤖 HR ASSISTANT BOT - Interactive Mode
==================================================================

Initializing system...
✅ System ready! You can now ask questions about HR policies.

Commands:
  • Type your question to get an answer
  • Type 'quit' or 'exit' to end the session
  • Press Ctrl+C to interrupt

==================================================================

❓ Your question: What is the leave policy?

============================================================
QUESTION: What is the leave policy?
============================================================

🔍 Searching for relevant documents in vector database...
💬 Generating answer using AutoGen agent...

============================================================
ANSWER:
According to the HR Support Desk Knowledge Base, the leave policy...
[Answer appears here with source citations]
============================================================

❓ Your question: quit

👋 Thank you for using HR Assistant Bot. Goodbye!
```

#### **Option B: Single Question Mode**

```bash
python main.py "What is the leave policy?"
```

**Perfect for:**
- Quick one-off questions
- Scripting/automation
- Testing specific queries

---

## Common Commands Summary

```bash
# Activate environment (always do this first!)
source .venv/bin/activate

# Test configuration
python test_config.py

# Embed new documents
python embed_documents.py

# Interactive chat
python interactive.py

# Single question
python main.py "Your question here"

# Deactivate environment when done
deactivate
```

---

## Troubleshooting

### **Problem: Import errors or module not found**

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### **Problem: Configuration errors**

```bash
# Check your .env file exists and has correct values
cat .env

# Verify configuration
python test_config.py
```

### **Problem: No documents found**

```bash
# Check PDFs are in data/ folder
ls data/*.pdf

# Re-run embedding
python embed_documents.py
```

### **Problem: Cosmos DB connection failed**

- ✅ Check your connection string in `.env`
- ✅ Verify firewall rules in Azure Portal allow your IP
- ✅ Ensure MongoDB vCore cluster is running
- ✅ Test connection string format

### **Problem: Azure OpenAI errors**

- ✅ Verify endpoint and key in `.env`
- ✅ Check model deployment names match Azure OpenAI Studio
- ✅ Ensure models are deployed and active
- ✅ Check API quotas and limits

---

## Quick Test Flow

Run these commands in order for a complete test:

```bash
# 1. Setup
source .venv/bin/activate

# 2. Verify config
python test_config.py

# 3. Embed documents (if not done)
python embed_documents.py

# 4. Test with a single question
python main.py "What is the company's leave policy?"

# 5. Try interactive mode
python interactive.py
```

---

## 🎉 That's It!

You should now have a working HR Q&A Bot that can:
- ✅ Answer questions about HR policies
- ✅ Use RAG to provide accurate, grounded responses
- ✅ Cite sources from your documents
- ✅ Run in interactive or single-question mode

---

## Need Help?

See these files for more details:
- `README.md` - Full documentation
- `QUICKSTART.md` - Quick start guide
- `PROJECT_REVIEW.md` - Technical review
- `.env.example` - Configuration template

**Happy chatting with your HR Bot! 🤖**
