"""
Configuration settings for the AI Booking Assistant.
"""
import os
from typing import Optional

# Try to import streamlit for secrets
try:
    import streamlit as st
    USE_STREAMLIT_SECRETS = True
except ImportError:
    USE_STREAMLIT_SECRETS = False

def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get secret from environment variable or Streamlit secrets."""
    if USE_STREAMLIT_SECRETS:
        try:
            # Try accessing secrets directly
            if hasattr(st, 'secrets') and st.secrets is not None:
                # Try dict-style access first
                if key in st.secrets:
                    return st.secrets[key]
                # Fall back to get method
                value = st.secrets.get(key, default)
                if value is not None:
                    return value
        except Exception as e:
            # If secrets access fails, fall through to environment variable
            pass
    # Fall back to environment variable
    return os.getenv(key, default)

# Google Gemini API Configuration
GEMINI_API_KEY: Optional[str] = get_secret("GEMINI_API_KEY")

# Database Configuration
DB_PATH: str = get_secret("DB_PATH", "bookings.db")

# Email Configuration (SMTP)
SMTP_SERVER: str = get_secret("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT: int = int(get_secret("SMTP_PORT", "587"))
SMTP_USERNAME: Optional[str] = get_secret("SMTP_USERNAME")
SMTP_PASSWORD: Optional[str] = get_secret("SMTP_PASSWORD")
EMAIL_FROM: Optional[str] = get_secret("EMAIL_FROM", SMTP_USERNAME)

# Web Search API (using DuckDuckGo or similar)
WEB_SEARCH_ENABLED: bool = get_secret("WEB_SEARCH_ENABLED", "true").lower() == "true"

# RAG Configuration
CHUNK_SIZE: int = 1000
CHUNK_OVERLAP: int = 200
EMBEDDING_MODEL: str = "models/gemini-embedding-001"  # Gemini embedding model
LLM_MODEL: str = "gemini-1.5-flash"  # Gemini LLM model

# Memory Configuration
MAX_MEMORY_MESSAGES: int = 25

# Vector Store
VECTOR_STORE_PATH: str = get_secret("VECTOR_STORE_PATH", "vector_store")

