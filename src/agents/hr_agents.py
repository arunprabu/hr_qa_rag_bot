"""
AutoGen v0.7.5 HR agents and team setup.
Uses the modern AutoGen 0.7.5 API for multi-agent orchestration.
"""
import asyncio
from typing import List
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_core import CancellationToken
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient

from ..vector_db.vector_db.cosmos_vector_db import CosmosVectorDB
from ..processors.pdf_processor import PDFProcessor


class HRAssistantTeam:
    """
    HR Q&A Assistant using AutoGen v0.7.5 multi-agent architecture.
    
    This class implements the RAG (Retrieval-Augmented Generation) pattern:
    1. Embeds user questions using Azure OpenAI
    2. Retrieves relevant context from Cosmos DB vector store
    3. Generates accurate answers using AutoGen agent with context
    """
    
    def __init__(
        self,
        cosmos_db: CosmosVectorDB,
        pdf_processor: PDFProcessor,
        azure_endpoint: str,
        azure_deployment: str,
        api_key: str,
        api_version: str
    ):
        """
        Initialize HR Assistant Team with AutoGen 0.7.5 components.
        
        Args:
            cosmos_db: Cosmos DB vector database instance for document retrieval
            pdf_processor: PDF processor instance for embedding generation
            azure_endpoint: Azure OpenAI endpoint URL (e.g., https://your-resource.openai.azure.com/)
            azure_deployment: Chat model deployment name (e.g., 'gpt-4o')
            api_key: Azure OpenAI API key for authentication
            api_version: Azure OpenAI API version (e.g., '2024-02-01')
        """
        self.cosmos_db = cosmos_db
        self.pdf_processor = pdf_processor
        
        # Initialize Azure OpenAI chat client using AutoGen 0.7.5 API
        self.model_client = AzureOpenAIChatCompletionClient(
            azure_endpoint=azure_endpoint,
            model=azure_deployment,
            api_version=api_version,
            azure_deployment=azure_deployment,
            api_key=api_key,
            temperature=0.0  # Deterministic responses for consistent answers
        )
        
        # Create HR Assistant Agent using AutoGen 0.7.5 AssistantAgent
        self.hr_assistant = AssistantAgent(
            name="hr_assistant",
            model_client=self.model_client,
            system_message="""You are a helpful and professional HR assistant for employees.
            
Your responsibilities:
- Answer employee questions about company policies, benefits, leave, and HR topics
- Base all answers strictly on the provided context from official HR documents
- If the information is not in the context, clearly state: "I don't have that information in the HR documents"
- Be concise, accurate, and professional in your responses
- Always cite the source document when providing information

CRITICAL RULE: Never make up or infer information. Only use facts explicitly stated in the provided context."""
        )
    
    async def ask_question(self, question: str, top_k: int = 5) -> str:
        """
        Ask the HR assistant a question using RAG (Retrieval-Augmented Generation).
        
        This method implements the complete RAG pipeline:
        1. Convert question to embedding vector
        2. Search vector database for relevant document chunks
        3. Build context from retrieved chunks
        4. Send context + question to AutoGen agent
        5. Return generated answer
        
        Args:
            question: Employee's question about HR policies
            top_k: Number of most relevant documents to retrieve (default: 5)
            
        Returns:
            Assistant's answer based on retrieved context
        """
        print(f"\n{'='*60}")
        print(f"QUESTION: {question}")
        print(f"{'='*60}\n")
        
        # Step 1: Convert question to embedding vector (1536 dimensions)
        question_embedding = self.pdf_processor.generate_embedding(question)
        
        # Step 2: Search Cosmos DB vector store for semantically similar documents
        print(f"🔍 Searching for relevant documents in vector database...")
        results = self.cosmos_db.search(
            query_embedding=question_embedding,
            top_k=top_k
        )
        
        # Step 3: Build context from retrieved documents with relevance scores
        context_parts = []
        for i, result in enumerate(results, 1):
            source = result.get("metadata", {}).get("source", "Unknown")
            content = result.get("content", "")
            # Convert distance to similarity percentage
            similarity_score = 1 - result.get("similarity", 1.0)
            
            context_parts.append(
                f"[Document {i} - Source: {source} (Relevance: {similarity_score:.2%})]\n{content}\n"
            )
        
        context = "\n".join(context_parts)
        
        # Step 4: Create augmented prompt combining context + question
        # This is the core of RAG - injecting retrieved context into the LLM prompt
        augmented_message = f"""Based on the following HR document excerpts, please answer the question.

CONTEXT FROM HR DOCUMENTS:
{context}

EMPLOYEE QUESTION: {question}

INSTRUCTIONS:
- Provide a clear, concise answer based ONLY on the information in the context above
- If the context doesn't contain enough information to answer, explicitly state that
- Cite the source document when providing information"""
        
        # Step 5: Send to AutoGen agent and get response (using 0.7.5 async API)
        print(f"💬 Generating answer using AutoGen agent...\n")
        
        cancellation_token = CancellationToken()
        response = await self.hr_assistant.on_messages(
            [TextMessage(content=augmented_message, source="user")],
            cancellation_token
        )
        
        # Extract the text answer from the agent's response
        answer = response.chat_message.content
        
        print(f"{'='*60}")
        print(f"ANSWER:\n{answer}")
        print(f"{'='*60}\n")
        
        return answer
    
    async def close(self):
        """Close model client connection."""
        await self.model_client.close()
