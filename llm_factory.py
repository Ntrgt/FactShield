"""Factory for creating the LLM instance based on the configured provider."""

from langchain_core.language_models import BaseChatModel

import config


def create_llm() -> BaseChatModel:
    """Return a LangChain chat model based on the LLM_PROVIDER setting."""
    provider = config.LLM_PROVIDER.lower()

    if provider == "groq":
        if not config.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY ayarlanmamış. "
                "https://console.groq.com/keys adresinden ücretsiz alabilirsiniz."
            )
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=config.LLM_MODELS["groq"],
            api_key=config.GROQ_API_KEY,
            max_tokens=config.LLM_MAX_TOKENS,
            temperature=config.LLM_TEMPERATURE,
        )

    if provider == "gemini":
        if not config.GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY ayarlanmamış. "
                "https://aistudio.google.com/apikey adresinden ücretsiz alabilirsiniz."
            )
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=config.LLM_MODELS["gemini"],
            google_api_key=config.GOOGLE_API_KEY,
            max_output_tokens=config.LLM_MAX_TOKENS,
            temperature=config.LLM_TEMPERATURE,
        )

    if provider == "anthropic":
        if not config.ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY ayarlanmamış. Lütfen .env dosyasını kontrol edin."
            )
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=config.LLM_MODELS["anthropic"],
            api_key=config.ANTHROPIC_API_KEY,
            max_tokens=config.LLM_MAX_TOKENS,
            temperature=config.LLM_TEMPERATURE,
        )

    raise ValueError(f"Desteklenmeyen LLM provider: {provider}")
