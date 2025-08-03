"""
Smart Document Chat - A modular RAG chatbot for PDF Q&A using Ollama and ChromaDB
Built for speed, clarity, and intelligence 🚀
"""

__version__ = "1.0.0"
__author__ = "Developer"

from .chatbot import RAGChatbot
from .document_processor import DocumentProcessor
from .vector_store import VectorStoreManager
from .llm_handler import LLMHandler

__all__ = [
    "RAGChatbot",
    "DocumentProcessor",
    "VectorStoreManager",
    "LLMHandler"
]