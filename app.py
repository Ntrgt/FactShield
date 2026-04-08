"""FactShield — AI-powered news fact-checking application."""

import streamlit as st

from claim_extraction import extract_claims
from rag_engine import RAGEngine
from report import generate_report
from scraping import scrape_article

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="FactShield",
    page_icon="🛡️",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        text-align: center;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .verdict-card {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .true-card  { background-color: #d1fae5; border-left: 4px solid #10b981; }
    .false-card { background-color: #fee2e2; border-left: 4px solid #ef4444; }
    .uncertain-card { background-color: #fef3c7; border-left: 4px solid #f59e0b; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown('<p class="main-header">🛡️ FactShield</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Yapay Zeka Destekli Haber Doğrulama Platformu</p>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar — settings
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Ayarlar")

    import config

    provider = st.selectbox(
        "LLM Sağlayıcı",
        ["groq", "gemini", "anthropic"],
        index=0,
        help="Groq ve Gemini ücretsiz, Anthropic ücretli.",
    )
    config.LLM_PROVIDER = provider

    if provider == "groq":
        groq_key = st.text_input("Groq API Key (ücretsiz)", type="password")
        if groq_key:
            config.GROQ_API_KEY = groq_key
        st.caption("https://console.groq.com/keys adresinden alabilirsiniz.")
    elif provider == "gemini":
        google_key = st.text_input("Google API Key (ücretsiz)", type="password")
        if google_key:
            config.GOOGLE_API_KEY = google_key
        st.caption("https://aistudio.google.com/apikey adresinden alabilirsiniz.")
    else:
        anthropic_key = st.text_input("Anthropic API Key", type="password")
        if anthropic_key:
            config.ANTHROPIC_API_KEY = anthropic_key

    tavily_key = st.text_input("Tavily API Key", type="password")
    if tavily_key:
        config.TAVILY_API_KEY = tavily_key
    st.caption("https://tavily.com adresinden ücretsiz alabilirsiniz.")

    st.markdown("---")
    st.markdown(
        "**Nasıl Çalışır?**\n"
        "1. Haber URL'si veya metin girin\n"
        "2. AI iddiaları çıkarır\n"
        "3. Her iddia internette araştırılır\n"
        "4. Kanıtlara dayalı doğruluk raporu üretilir"
    )

# ---------------------------------------------------------------------------
# Input section
# ---------------------------------------------------------------------------
st.markdown("### 📰 Haber Girişi")
input_mode = st.radio(
    "Giriş yöntemi seçin:",
    ["URL ile", "Metin olarak"],
    horizontal=True,
)

article_info: dict | None = None
news_text: str = ""

if input_mode == "URL ile":
    url = st.text_input("Haber URL'sini yapıştırın:", placeholder="https://...")
    if url:
        article_info = {"title": "", "source_url": url, "publish_date": None}
else:
    news_text = st.text_area(
        "Haber metnini yapıştırın:",
        height=250,
        placeholder="Haber içeriğini buraya yapıştırın...",
    )
    if news_text:
        article_info = {
            "title": "Kullanıcı Tarafından Girilen Metin",
            "source_url": "N/A",
            "publish_date": None,
        }

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
if st.button("🔍 Analizi Başlat", type="primary", use_container_width=True):
    if not article_info and not news_text:
        st.warning("Lütfen bir URL veya metin girin.")
        st.stop()

    # Step 1 — Scrape or use raw text
    with st.status("📥 Haber metni alınıyor...", expanded=True) as status:
        try:
            if input_mode == "URL ile":
                scraped = scrape_article(url)
                article_info = scraped
                news_text = scraped["text"]
                st.write(f"**Başlık:** {scraped['title']}")
            else:
                st.write("Kullanıcı metni kullanılıyor.")
            status.update(label="📥 Metin alındı!", state="complete")
        except ValueError as e:
            st.error(f"Hata: {e}")
            st.stop()

    # Step 2 — Extract claims
    with st.status("🧠 İddialar çıkarılıyor...", expanded=True) as status:
        try:
            claims = extract_claims(news_text)
            st.write(f"**{len(claims)} iddia** tespit edildi.")
            for c in claims:
                st.write(f"- {c['claim']}")
            status.update(label="🧠 İddialar çıkarıldı!", state="complete")
        except ValueError as e:
            st.error(f"Hata: {e}")
            st.stop()

    # Step 3 — Verify each claim via RAG
    with st.status("🔎 İddialar doğrulanıyor...", expanded=True) as status:
        try:
            engine = RAGEngine()
            results = []
            progress = st.progress(0)
            for i, claim in enumerate(claims):
                st.write(f"İddia {claim['id']} araştırılıyor...")
                result = engine.analyze_claim(claim["id"], claim["claim"])
                results.append(result)
                progress.progress((i + 1) / len(claims))
            status.update(label="🔎 Doğrulama tamamlandı!", state="complete")
        except (ValueError, RuntimeError) as e:
            st.error(f"Doğrulama hatası: {e}")
            st.stop()

    # Step 4 — Display results
    st.markdown("---")
    st.markdown("## 📊 Sonuçlar")

    # Summary metrics
    verdicts = [r.get("verdict", "Belirsiz") for r in results]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Toplam İddia", len(claims))
    col2.metric("✅ Doğru", verdicts.count("Doğru"))
    col3.metric("❌ Yanlış", verdicts.count("Yanlış"))
    col4.metric("⚠️ Belirsiz", verdicts.count("Belirsiz"))

    # Overall confidence bar
    confidences = [r.get("confidence", 0.0) for r in results]
    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
    st.markdown("### Genel Güven Skoru")
    st.progress(avg_conf)
    st.caption(f"{avg_conf:.0%}")

    # Per-claim cards
    st.markdown("### İddia Detayları")
    for claim, result in zip(claims, results):
        verdict = result.get("verdict", "Belirsiz")
        css_class = {
            "Doğru": "true-card",
            "Yanlış": "false-card",
        }.get(verdict, "uncertain-card")
        icon = {"Doğru": "✅", "Yanlış": "❌"}.get(verdict, "⚠️")

        with st.expander(f"{icon} İddia {claim['id']}: {claim['claim']}"):
            st.markdown(f"**Sonuç:** {verdict}")
            st.markdown(f"**Güven:** {result.get('confidence', 0):.0%}")
            st.progress(result.get("confidence", 0.0))
            st.markdown(f"**Açıklama:** {result.get('explanation', '')}")

            sources = result.get("sources", [])
            if sources:
                st.markdown("**Kaynaklar:**")
                for src in sources:
                    st.markdown(f"- [{src.get('title', 'Kaynak')}]({src.get('url', '#')})")

    # Step 5 — Markdown report
    st.markdown("---")
    st.markdown("## 📄 Tam Rapor")
    md_report = generate_report(article_info, claims, results)
    st.markdown(md_report)
    st.download_button(
        label="📥 Raporu İndir (Markdown)",
        data=md_report,
        file_name="factshield_rapor.md",
        mime="text/markdown",
    )
