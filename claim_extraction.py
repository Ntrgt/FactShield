"""Claim extraction module using LLM to identify verifiable claims from news text."""

import json
import re

from langchain_core.messages import HumanMessage, SystemMessage

from llm_factory import create_llm

SYSTEM_PROMPT = """\
Sen bir haber analiz uzmanısın. Görevin, verilen haber metninden kontrol edilebilir, \
somut iddiaları çıkarmaktır.

Kurallar:
1. Yalnızca doğrulanabilir olgusal iddiaları çıkar (sayılar, tarihler, isimler, olaylar, \
istatistikler).
2. Öznel yorumları, tahminleri veya görüş ifadelerini ÇIKARMA.
3. Her iddiayı bağımsız, tek bir cümle olarak yaz.
4. En fazla 7 iddia çıkar; en önemli ve doğrulanabilir olanları seç.
5. Yanıtını YALNIZCA aşağıdaki JSON formatında ver, başka hiçbir şey ekleme:

[
  {"id": 1, "claim": "İddia metni burada"},
  {"id": 2, "claim": "İddia metni burada"}
]
"""


def extract_claims(text: str) -> list[dict]:
    """Extract verifiable claims from the given news text using an LLM.

    Returns a list of dicts, each with 'id' and 'claim' keys.
    Raises ValueError if no claims could be extracted.
    """
    llm = create_llm()

    truncated = text[:6000] if len(text) > 6000 else text

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=f"Aşağıdaki haber metninden doğrulanabilir iddiaları çıkar:\n\n{truncated}"
        ),
    ]

    response = llm.invoke(messages)
    raw = response.content
    # Some models return a list of content blocks instead of a plain string
    if isinstance(raw, list):
        raw = " ".join(
            block.get("text", str(block)) if isinstance(block, dict) else str(block)
            for block in raw
        )
    return _parse_claims(raw)


def _parse_claims(raw: str) -> list[dict]:
    """Parse the LLM response into a list of claim dicts."""
    # Try direct JSON parse first
    try:
        claims = json.loads(raw)
        if isinstance(claims, list) and claims:
            return claims
    except json.JSONDecodeError:
        pass

    # Fallback: extract JSON array from within the response text
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        try:
            claims = json.loads(match.group())
            if isinstance(claims, list) and claims:
                return claims
        except json.JSONDecodeError:
            pass

    raise ValueError("LLM yanıtından iddialar ayrıştırılamadı.")
