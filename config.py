"""
Smart Document Chat - Configuration Central 🎛️
All the settings and tweaks to make this RAG chatbot absolutely perfect
"""
import os
from pathlib import Path
from typing import Union, Type, Any

# Base directory configuration
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"

# Create logs directory if it doesn't exist
LOGS_DIR.mkdir(exist_ok=True)

def get_config_value(env_key: str, default_value: Any, config_type: Type = str) -> Any:
    """Get configuration value from environment variable or use default"""
    env_value = os.getenv(env_key)
    if env_value is not None:
        if config_type == bool:
            return env_value.lower() in ('true', '1', 'yes', 'on')
        elif config_type == int:
            return int(env_value)
        elif config_type == float:
            return float(env_value)
        return env_value
    return default_value

# Directory configuration
PDF_DIR = BASE_DIR / "pdfFiles"
VECTOR_DB_DIR = BASE_DIR / "vectorDB"

# Create directories if they don't exist
PDF_DIR.mkdir(exist_ok=True)
VECTOR_DB_DIR.mkdir(exist_ok=True)

# LLM Configuration
LLM_MODEL = get_config_value("LLM_MODEL", "gemma3:4b")
LLM_BASE_URL = get_config_value("LLM_BASE_URL", "http://localhost:11434")
LLM_TEMPERATURE = get_config_value("LLM_TEMPERATURE", 0.6, float)

# Embedding model
EMBEDDING_MODEL = get_config_value("EMBEDDING_MODEL", "nomic-embed-text")

# Document processing settings
CHUNK_SIZE = get_config_value("CHUNK_SIZE", 1500, int)
CHUNK_OVERLAP = get_config_value("CHUNK_OVERLAP", 200, int)
MAX_FILE_SIZE_MB = get_config_value("MAX_FILE_SIZE_MB", 50, int)

# Vector DB settings
CHROMA_PERSIST_DIR = str(VECTOR_DB_DIR)
COLLECTION_NAME = get_config_value("COLLECTION_NAME", "pdf_documents")

# Performance settings
EMBEDDING_BATCH_SIZE = get_config_value("EMBEDDING_BATCH_SIZE", 10, int)
RETRIEVAL_K = get_config_value("RETRIEVAL_K", 4, int)
SIMILARITY_THRESHOLD = get_config_value("SIMILARITY_THRESHOLD", 0.7, float)

# Streamlit App Configuration
PAGE_TITLE = get_config_value("PAGE_TITLE", "🤖 Smart Document Assistant")
PAGE_ICON = get_config_value("PAGE_ICON", "🚀")
PAGE_LAYOUT = get_config_value("PAGE_LAYOUT", "wide")

# Server settings
SERVER_PORT = get_config_value("SERVER_PORT", 8501, int)
SERVER_ADDRESS = get_config_value("SERVER_ADDRESS", "localhost")
ALLOW_REMOTE_ACCESS = get_config_value("ALLOW_REMOTE_ACCESS", False, bool)

# Session State Keys
SESSION_MESSAGES = "messages"
SESSION_VECTOR_STORE = "vector_store"
SESSION_CONVERSATION_CHAIN = "conversation_chain"

# UI Messages
WELCOME_MESSAGE = get_config_value("WELCOME_MESSAGE", 
                                 "🎯 Hey there! Drop your PDFs and let's get some answers! 📄⚡")
UPLOAD_PROMPT = get_config_value("UPLOAD_PROMPT",
                               "Ready when you are - just upload a PDF to start our conversation.")
PROCESSING_MESSAGE = "🔥 Working my magic on your document... hang tight!"
SUCCESS_MESSAGE = "✨ All set! Your PDF is locked and loaded. Fire away with questions!"
ERROR_MESSAGE = "Oops! Something went sideways: {}"
PERSISTENT_DATA_MESSAGE = "Welcome back! Your docs are ready to chat. Add more or dive right in!"

# Advanced settings
DEBUG_MODE = get_config_value("DEBUG_MODE", False, bool)
SHOW_SOURCE_DOCUMENTS = get_config_value("SHOW_SOURCE_DOCUMENTS", True, bool)
LOG_LEVEL = get_config_value("LOG_LEVEL", "INFO")

# Disable Streamlit telemetry for privacy
os.environ["STREAMLIT_TELEMETRY_DISABLED"] = "true"
