"""Gemini API bağlantı testi."""

from dotenv import load_dotenv
load_dotenv()

import config

print(f"Provider: {config.LLM_PROVIDER}")
print(f"Google Key: {config.GOOGLE_API_KEY[:10]}..." if config.GOOGLE_API_KEY else "Google Key: BOŞ!")
print(f"Tavily Key: {config.TAVILY_API_KEY[:10]}..." if config.TAVILY_API_KEY else "Tavily Key: BOŞ!")
print()

try:
    from llm_factory import create_llm
    from langchain_core.messages import HumanMessage

    print("LLM oluşturuluyor...")
    llm = create_llm()

    print("Gemini'ye test mesajı gönderiliyor...")
    response = llm.invoke([HumanMessage(content="Merhaba, sadece 'Çalışıyorum' yaz.")])
    print(f"Yanıt: {response.content}")
    print("\nBAŞARILI! Gemini API çalışıyor.")
except Exception as e:
    print(f"\nHATA: {type(e).__name__}: {e}")
