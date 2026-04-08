"""RAG engine: searches for evidence and verifies claims."""

import json
import re

from langchain_core.messages import HumanMessage, SystemMessage
from tavily import TavilyClient

import config
from llm_factory import create_llm

VERIFICATION_SYSTEM_PROMPT = """\
Sen bir doğrulama uzmanısın. Sana bir iddia ve bu iddiayla ilgili kaynaklardan toplanan \
kanıtlar verilecek.

KRİTİK KURALLAR:
1. YALNIZCA sağlanan kaynaklara dayanarak cevap ver.
2. Kaynaklarda yeterli bilgi yoksa verdict olarak "Belirsiz" de.
3. Kendi bilgini veya varsayımlarını KULLANMA.
4. Kaynakların tarihine dikkat et — eski bilgiler güncel iddiaları yanlış doğrulayabilir.

Yanıtını YALNIZCA şu JSON formatında ver:
{
  "verdict": "Doğru" | "Yanlış" | "Belirsiz",
  "confidence": 0.0-1.0,
  "explanation": "Kısa açıklama"
}
"""


class RAGEngine:
    """Retrieval-Augmented Generation engine for claim verification."""

    def __init__(self):
        if not config.TAVILY_API_KEY:
            raise ValueError(
                "TAVILY_API_KEY ayarlanmamış. Lütfen .env dosyasını kontrol edin."
            )

        self.search_client = TavilyClient(api_key=config.TAVILY_API_KEY)
        self.llm = create_llm()
        self._evidence_store: dict[int, list[dict]] = {}

    def search_evidence(self, claim: str) -> list[dict]:
        """Search the web for evidence related to the given claim."""
        try:
            results = self.search_client.search(
                query=claim,
                max_results=config.MAX_SEARCH_RESULTS,
                search_depth="advanced",
                include_raw_content=False,
            )
            return results.get("results", [])
        except Exception as e:
            raise RuntimeError(f"Arama sırasında hata oluştu: {e}") from e

    def store_evidence(self, claim_id: int, evidence_list: list[dict]) -> None:
        """Store evidence documents in memory."""
        stored = []
        for ev in evidence_list:
            content = ev.get("content", "")
            if not content:
                continue
            stored.append({
                "content": content[:2000],
                "url": ev.get("url", ""),
                "title": ev.get("title", ""),
                "score": ev.get("score", 0.0),
            })
        self._evidence_store[claim_id] = stored

    def retrieve_evidence(self, claim: str, claim_id: int) -> list[dict]:
        """Retrieve stored evidence for the claim, sorted by relevance score."""
        evidence = self._evidence_store.get(claim_id, [])
        return sorted(evidence, key=lambda x: x.get("score", 0), reverse=True)[
            : config.TOP_K_RESULTS
        ]

    def verify_claim(self, claim: str, evidence: list[dict]) -> dict:
        """Use LLM to verify a claim against the retrieved evidence."""
        if not evidence:
            return {
                "verdict": "Belirsiz",
                "confidence": 0.0,
                "explanation": "Bu iddia için kaynak bulunamadı.",
                "sources": [],
            }

        evidence_text = ""
        sources = []
        for i, ev in enumerate(evidence, 1):
            evidence_text += (
                f"\n--- Kaynak {i} ---\n"
                f"Başlık: {ev.get('title', 'N/A')}\n"
                f"URL: {ev.get('url', 'N/A')}\n"
                f"İçerik: {ev['content'][:800]}\n"
            )
            sources.append({"title": ev.get("title", ""), "url": ev.get("url", "")})

        messages = [
            SystemMessage(content=VERIFICATION_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"İDDİA: {claim}\n\n"
                    f"KAYNAKLAR:{evidence_text}\n\n"
                    "Bu kaynakları kullanarak iddiayı doğrula."
                )
            ),
        ]

        response = self.llm.invoke(messages)
        raw = response.content
        if isinstance(raw, list):
            raw = " ".join(
                block.get("text", str(block)) if isinstance(block, dict) else str(block)
                for block in raw
            )
        result = self._parse_verdict(raw)
        result["sources"] = sources
        return result

    def analyze_claim(self, claim_id: int, claim: str) -> dict:
        """Full pipeline: search, store, retrieve, and verify a single claim."""
        evidence_list = self.search_evidence(claim)
        self.store_evidence(claim_id, evidence_list)
        evidence = self.retrieve_evidence(claim, claim_id)
        return self.verify_claim(claim, evidence)

    @staticmethod
    def _parse_verdict(raw: str) -> dict:
        """Parse the LLM verdict response."""
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        return {
            "verdict": "Belirsiz",
            "confidence": 0.0,
            "explanation": "Doğrulama yanıtı ayrıştırılamadı.",
        }
