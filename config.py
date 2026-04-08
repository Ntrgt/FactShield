"""FactShield configuration and environment setup."""

import os
from dotenv import load_dotenv

load_dotenv()

# LLM Provider: "groq" (free), "gemini" (free) or "anthropic" (paid)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

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
