"""Report generation module for producing markdown fact-check reports."""

from datetime import datetime


def generate_report(article_info: dict, claims: list[dict], results: list[dict]) -> str:
    """Generate a markdown report summarizing the fact-check analysis.

    Args:
        article_info: Dict with title, source_url, publish_date keys.
        claims: List of claim dicts with id and claim keys.
        results: List of verification result dicts aligned with claims.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    verdicts = [r.get("verdict", "Belirsiz") for r in results]
    confidences = [r.get("confidence", 0.0) for r in results]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

    true_count = verdicts.count("Doğru")
    false_count = verdicts.count("Yanlış")
    uncertain_count = verdicts.count("Belirsiz")

    overall = _overall_verdict(avg_confidence, true_count, false_count, len(claims))

    lines = [
        f"# FactShield Doğruluk Raporu",
        f"",
        f"**Analiz Tarihi:** {now}",
        f"**Makale:** {article_info.get('title', 'N/A')}",
        f"**Kaynak:** {article_info.get('source_url', 'N/A')}",
        f"**Yayın Tarihi:** {article_info.get('publish_date', 'Bilinmiyor')}",
        f"",
        f"---",
        f"",
        f"## Genel Değerlendirme",
        f"",
        f"| Metrik | Değer |",
        f"|--------|-------|",
        f"| Toplam İddia | {len(claims)} |",
        f"| Doğru | {true_count} |",
        f"| Yanlış | {false_count} |",
        f"| Belirsiz | {uncertain_count} |",
        f"| Ortalama Güven Skoru | {avg_confidence:.0%} |",
        f"| **Genel Sonuç** | **{overall}** |",
        f"",
        f"---",
        f"",
        f"## İddia Detayları",
        f"",
    ]

    for claim, result in zip(claims, results):
        verdict = result.get("verdict", "Belirsiz")
        confidence = result.get("confidence", 0.0)
        explanation = result.get("explanation", "")
        icon = {"Doğru": "✅", "Yanlış": "❌"}.get(verdict, "⚠️")

        lines.append(f"### {icon} İddia {claim['id']}: {claim['claim']}")
        lines.append(f"")
        lines.append(f"- **Sonuç:** {verdict}")
        lines.append(f"- **Güven:** {confidence:.0%}")
        lines.append(f"- **Açıklama:** {explanation}")

        sources = result.get("sources", [])
        if sources:
            lines.append(f"- **Kaynaklar:**")
            for src in sources:
                title = src.get("title", "Kaynak")
                url = src.get("url", "#")
                lines.append(f"  - [{title}]({url})")

        lines.append("")

    lines.extend([
        "---",
        "",
        "*Bu rapor FactShield tarafından otomatik olarak üretilmiştir. "
        "Sonuçlar yalnızca bilgilendirme amaçlıdır ve kesin yargı niteliği taşımaz.*",
    ])

    return "\n".join(lines)


def _overall_verdict(
    avg_confidence: float,
    true_count: int,
    false_count: int,
    total: int,
) -> str:
    """Determine the overall verdict label."""
    if total == 0:
        return "Değerlendirilemedi"
    if false_count > total / 2:
        return "Büyük Ölçüde Yanlış"
    if true_count > total / 2 and avg_confidence >= 0.6:
        return "Büyük Ölçüde Doğru"
    if false_count == 0 and avg_confidence >= 0.7:
        return "Doğru"
    return "Karışık / Belirsiz"
