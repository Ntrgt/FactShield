"""FactShield configuration and environment setup."""

import os
from dotenv import load_dotenv

load_dotenv()


def _get_secret(key: str, default: str = "") -> str:
    """Read from Streamlit secrets (cloud) or environment variables (local)."""
    try:
        import streamlit as st
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)


# LLM Provider: "groq" (free), "gemini" (free) or "anthropic" (paid)
LLM_PROVIDER = _get_secret("LLM_PROVIDER", "groq")

GROQ_API_KEY = _get_secret("GROQ_API_KEY")
GOOGLE_API_KEY = _get_secret("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = _get_secret("ANTHROPIC_API_KEY")
TAVILY_API_KEY = _get_secret("TAVILY_API_KEY")

# LLM settings per provider
LLM_MODELS = {
    "groq": "llama-3.3-70b-versatile",
    "gemini": "gemini-2.0-flash",
    "anthropic": "claude-sonnet-4-20250514",
}
LLM_MAX_TOKENS = 4096
LLM_TEMPERATURE = 0.1

# RAG settings
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 5
MAX_SEARCH_RESULTS = 5

# Confidence thresholds
CONFIDENCE_HIGH = 0.7
CONFIDENCE_LOW = 0.4
