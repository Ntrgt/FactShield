# 🛡️ FactShield — Yapay Zeka Destekli Haber Doğrulama Platformu

**FactShield**, kullanıcıdan gelen bir haber linki veya ham metin üzerinden iddiaları ayrıştıran, internette arama yaparak bu iddiaları doğrulayan ve kanıta dayalı güven skoru üreten bir yapay zeka uygulamasıdır.

🔗 **Canlı Demo:** [https://factshield-sjvxrhvdnumqmpfvd7w549.streamlit.app](https://factshield-sjvxrhvdnumqmpfvd7w549.streamlit.app)

---

## 📸 Ekran Görüntüsü

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" />
  <img src="https://img.shields.io/badge/Streamlit-1.30+-red?logo=streamlit" />
  <img src="https://img.shields.io/badge/LLM-Groq%20%7C%20Gemini%20%7C%20Anthropic-green" />
  <img src="https://img.shields.io/badge/Search-Tavily%20API-orange" />
</p>

---

## 🚀 Nasıl Çalışır?

```
Kullanıcı (URL / Metin)
        │
        ▼
  ┌─────────────┐
  │  Web Scraping │  Newspaper3k ile haber çekme
  └──────┬──────┘
         ▼
  ┌──────────────────┐
  │  İddia Çıkarma    │  LLM ile doğrulanabilir iddiaları tespit etme
  └──────┬───────────┘
         ▼
  ┌──────────────────┐
  │  RAG Engine       │  Tavily ile web araması → LLM ile kanıt doğrulama
  └──────┬───────────┘
         ▼
  ┌──────────────────┐
  │  Rapor Üretimi    │  Güven skoru + kaynak linkli Markdown rapor
  └──────────────────┘
```

1. **Haber Çekme** — URL girildiğinde Newspaper3k ile makale metni, başlık ve tarih otomatik çekilir.
2. **İddia Çıkarma** — LLM, metindeki doğrulanabilir olgusal iddiaları (sayılar, isimler, olaylar) maddeler halinde ayırır.
3. **RAG ile Doğrulama** — Her iddia için Tavily API ile güncel web kaynakları aranır. LLM'e yalnızca bulunan kanıtlar verilir ve "Doğru", "Yanlış" veya "Belirsiz" kararı üretilir.
4. **Raporlama** — Tüm sonuçlar güven skoru barı, renk kodlu kartlar ve indirilebilir Markdown rapor olarak sunulur.

---

## 🏗️ Proje Yapısı

```
FactShield/
├── app.py                 # Streamlit arayüzü (ana uygulama)
├── scraping.py            # URL'den haber çekme
├── claim_extraction.py    # LLM ile iddia çıkarma
├── rag_engine.py          # RAG: Tavily arama + LLM doğrulama
├── report.py              # Markdown rapor üretimi
├── config.py              # Ayarlar ve ortam değişkenleri
├── llm_factory.py         # Çoklu LLM provider desteği
├── requirements.txt       # Bağımlılıklar
├── .env.example           # API key şablonu
└── .streamlit/
    └── config.toml        # Streamlit tema ayarları
```

---

## 🛠️ Kullanılan Teknolojiler

| Kategori | Teknoloji | Açıklama |
|----------|-----------|----------|
| **Arayüz** | Streamlit | Python-native web arayüzü |
| **LLM** | Groq (Llama 3.3 70B) | Ücretsiz, hızlı dil modeli |
| **Web Arama** | Tavily API | Haber doğrulama için optimize arama |
| **Orkestrasyon** | LangChain | LLM entegrasyon framework'ü |
| **Scraping** | Newspaper3k | Haber sitelerine özel metin çıkarıcı |

> 💡 Groq dışında **Google Gemini** ve **Anthropic Claude** da desteklenmektedir.

---

## ⚡ Kurulum

```bash
# 1. Repoyu klonlayın
git clone https://github.com/Ntrgt/FactShield.git
cd FactShield

# 2. Sanal ortam oluşturun
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. API anahtarlarını ayarlayın
copy .env.example .env
# .env dosyasını açıp anahtarları girin

# 5. Uygulamayı çalıştırın
python -m streamlit run app.py
```

---

## 🔑 API Anahtarları

| API | Nereden Alınır | Ücret |
|-----|---------------|-------|
| **Groq** | [console.groq.com/keys](https://console.groq.com/keys) | Ücretsiz |
| **Tavily** | [tavily.com](https://tavily.com) | Ücretsiz (1000 arama/ay) |
| **Gemini** (opsiyonel) | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | Ücretsiz |

---

## 🤖 RAG (Retrieval-Augmented Generation) Nedir?

FactShield, LLM'e direkt "bu haber doğru mu?" diye sormaz. Bunun yerine:

1. **Retrieval** — Her iddia için internetten güncel kanıtlar toplanır
2. **Augmented** — Bu kanıtlar LLM'e bağlam olarak verilir
3. **Generation** — LLM yalnızca verilen kanıtlara dayanarak karar üretir

Bu yaklaşım, LLM'in kendi bilgisini uydurmasını (halüsinasyon) engelleyerek güvenilir sonuçlar üretir.

---

## ⚠️ Sınırlamalar

- Paywall'lu (ücretli erişimli) haber sitelerinden metin çekilemez
- Görsel ve video içerikler analiz edilemez
- Çok taze haberlerde kaynak yetersizliği nedeniyle "Belirsiz" sonucu çıkabilir
- Sonuçlar bilgilendirme amaçlıdır, kesin yargı niteliği taşımaz

---

## 📄 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.
