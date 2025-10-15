"""
PDF processing module for extracting text, chunking, and generating embeddings.

This module handles the document preparation phase of RAG:
1. Extract text from PDF files
2. Split text into manageable chunks with overlap
3. Generate embedding vectors for each chunk using Azure OpenAI
"""
import os
from typing import List, Dict, Any
from pathlib import Path
import PyPDF2
from openai import AzureOpenAI


class PDFProcessor:
    """
    Processes PDF documents into embedded chunks for vector search.
    
    Workflow:
    1. Extract all text from PDF pages
    2. Split into overlapping chunks (for context continuity)
    3. Generate 1536-dimensional embeddings for each chunk
    4. Package as documents ready for Cosmos DB storage
    """
    
    def __init__(
        self,
        azure_endpoint: str,
        azure_api_key: str,
        api_version: str,
        embedding_model: str
    ):
        """
        Initialize PDF processor with Azure OpenAI client.
        
        Args:
            azure_endpoint: Azure OpenAI endpoint URL
            azure_api_key: Azure OpenAI API key
            api_version: API version
            embedding_model: Embedding model deployment name
        """
        self.client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=azure_api_key,
            api_version=api_version
        )
        self.embedding_model = embedding_model
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract all text from a PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text as string
        """
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                print(f"📄 Extracting text from {Path(pdf_path).name} ({total_pages} pages)...")
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                print(f"✓ Extracted {len(text)} characters")
                
        except Exception as e:
            print(f"✗ Error extracting text: {e}")
            
        return text
    
    def chunk_text(
        self, 
        text: str, 
        chunk_size: int = 1000, 
        overlap: int = 200
    ) -> List[str]:
        """
        Split text into overlapping chunks for better context preservation.
        
        Overlap ensures that information split across chunk boundaries
        is still captured in at least one complete chunk.
        
        Example with chunk_size=10, overlap=3:
        "Hello world test" -> ["Hello worl", "orl test"]
                                    ^^^(overlap)
        
        Args:
            text: Full text to split into chunks
            chunk_size: Maximum characters per chunk (default: 1000)
            overlap: Characters to repeat between chunks (default: 200)
            
        Returns:
            List of overlapping text chunks
        """
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end].strip()
            
            if chunk:
                chunks.append(chunk)
            
            # Move forward by (chunk_size - overlap) to create overlap
            start += (chunk_size - overlap)
        
        print(f"✓ Created {len(chunks)} chunks")
        return chunks
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate 1536-dimensional embedding vector using Azure OpenAI.
        
        Embeddings convert text into numerical vectors that capture semantic meaning.
        Similar texts will have similar embedding vectors (measured by cosine similarity).
        
        Args:
            text: Text to convert to embedding (question or document chunk)
            
        Returns:
            1536-dimensional float vector representing the text's semantic meaning
        """
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.embedding_model  # text-embedding-ada-002
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"✗ Error generating embedding: {e}")
            return []
    
    def process_pdf(
        self,
        pdf_path: str,
        chunk_size: int,
        overlap: int,
        metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Complete pipeline: extract, chunk, and embed PDF.
        
        Args:
            pdf_path: Path to PDF file
            chunk_size: Size of text chunks
            overlap: Overlap between chunks
            metadata: Additional metadata
            
        Returns:
            List of documents with embeddings
        """
        print(f"\n{'='*60}")
        print(f"Processing: {Path(pdf_path).name}")
        print(f"{'='*60}")
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        if not text.strip():
            return []
        
        # Chunk text
        chunks = self.chunk_text(text, chunk_size, overlap)
        
        # Create documents with embeddings
        documents = []
        for i, chunk in enumerate(chunks):
            print(f"Generating embedding {i+1}/{len(chunks)}...", end='\r')
            
            embedding = self.generate_embedding(chunk)
            
            doc = {
                "content": chunk,
                "contentVector": embedding,
                "metadata": {
                    "source": os.path.basename(pdf_path),
                    "full_path": pdf_path,
                    "chunk_id": i,
                    "total_chunks": len(chunks),
                    **(metadata or {})
                }
            }
            documents.append(doc)
        
        print(f"\n✓ Created {len(documents)} documents with embeddings\n")
        return documents
