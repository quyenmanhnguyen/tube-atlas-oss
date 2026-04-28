<div align="center">

# 📺 Tube Atlas OSS

**Focused YouTube research & creator toolkit — find a niche, mine keywords, clone winning videos, ship scripts in EN/KO/JA/VI.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![DeepSeek](https://img.shields.io/badge/AI-DeepSeek-blue)](https://platform.deepseek.com)
[![CI](https://github.com/quyenmanhnguyen/tube-atlas-oss/actions/workflows/ci.yml/badge.svg)](https://github.com/quyenmanhnguyen/tube-atlas-oss/actions)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](#-docker)

<img src="https://img.shields.io/badge/Tools-5%20focused%20features-7c3aed?style=for-the-badge" alt="5 focused features">

</div>

---

## 📸 Preview

<div align="center">

### Dashboard
![Dashboard](assets/screenshot-dashboard.png)

### Keyword Generator (no API key needed!)
![Keyword Generator](assets/screenshot-keyword.png)

### Video → Text Converter
![Video to Text](assets/screenshot-transcript.png)

</div>

---

## ✨ Features

Five focused tools, wired together as a **single seamless pipeline**: discover a niche, mine keywords, hunt outlier videos, clone winners → drop any of it into Studio → walk it through Topic → Title → Outline → Script → Humanize Rewrite. No copy-pasting between tools.

### Research

| # | Tool | What it does | API keys |
|---|---|---|---|
| 01 | **Niche Finder** | Trends + long-tail + top channels + **outlier (breakout) detection** + **opportunity score** + **Trend Pulse 7d** (HOT / cooling / stable) + audience sentiment + AI verdict. | YouTube + DeepSeek |
| 02 | **Keyword Finder** | Long-tail suggestions from YouTube Autocomplete + **VidIQ-style Keyword Score** (Volume + Competition gauges, proxy) + **VPH bar chart** of top results + **KGR ease-to-rank** + **question buckets** (`how/what/why/when/where`). | None / YouTube |
| 03 | **Video Cloner** | Paste a URL → fingerprint, hook/structure breakdown, N title clones, full script clone, thumbnail copy & SEO tags — **auto-detects the source video's language**. Transcript backend uses ``youtube-transcript-api`` with **yt-dlp fallback** for cloud-IP environments. | YouTube + DeepSeek |
| 04 | **Outlier Finder** ⭐ | Find **small channels with viral videos** in the last 7/14/30 days. Filters by ``subs ≤ N`` and ``views/subs ≥ K×``. Per-row **🎯 Clone** + **📝 Studio topic** handoff. CSV export. | YouTube |

### Create

| # | Tool | What it does | API keys |
|---|---|---|---|
| 05 | **Studio** | 5-step wizard: ① 20 topic ideas → ② 10 titles (top 3 CTR marked) → ③ 8-part long-form outline (Hook · Empathy · Problem 1 · Small Change · Story · Problems 2&3 · Reflection · CTA) → ④ full long-form script (chunked, up to 24,000 chars) → ⑤ humanize rewrite. State persists across steps; Niche / Keyword / Cloner / Outlier all prefill any step via **"→ Send to Studio"**. | DeepSeek |

UI and AI output respect the language picker (English / 한국어 / 日本語 / Tiếng Việt) in the sidebar — and Video Cloner overrides it with the source video's detected language unless you force otherwise.

### Pipeline diagram

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ 01 Niche    │  │ 02 Keyword  │  │ 03 Cloner   │  │ 04 Outlier  │
│ • Pulse 7d  │  │ • Vol/Comp  │  │ • lang det  │  │ • subs≤100k │
│ • outliers  │  │ • VPH chart │  │ • clone kit │  │ • views/sub │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │                │
       └─── → Send to Studio  ·  → Clone via Cloner  ─────┘
                              │
                              ▼
                ┌──────────────────────────────┐
                │     05 Studio (5 steps)      │
                │ ① Topic ideas (×20)          │
                │ ② Titles (×10 + top-3 CTR)   │
                │ ③ 8-part outline             │
                │ ④ Long-form script (chunked) │
                │ ⑤ Humanize rewrite           │
                └──────────────────────────────┘
```

---

## 🚀 Cài đặt

```bash
# Clone repo
git clone https://github.com/quyenmanhnguyen/tube-atlas-oss.git
cd tube-atlas-oss

# Cài dependencies
pip install -r requirements.txt

# Cấu hình API keys
cp .env.example .env
# Sửa .env → thêm YOUTUBE_API_KEY và DEEPSEEK_API_KEY

# Chạy
streamlit run app.py
```

Mở browser tại **http://localhost:8501** 🎉

---

## 🐳 Docker

```bash
docker build -t tube-atlas-oss .
docker run -p 8501:8501 --env-file .env tube-atlas-oss
```

---

## ☁️ Deploy lên Streamlit Cloud (free)

1. Fork repo này
2. Vào [share.streamlit.io](https://share.streamlit.io) → Connect GitHub
3. Chọn repo `tube-atlas-oss` → Main file: `app.py`
4. Advanced settings → Secrets:
   ```toml
   YOUTUBE_API_KEY = "AIza..."
   DEEPSEEK_API_KEY = "sk-..."
   ```
5. Click Deploy → có URL public trong ~2 phút

---

## 🔑 Lấy API Keys

### YouTube Data API v3 (miễn phí — 10,000 units/ngày)

1. Vào [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Tạo Project → Enable **YouTube Data API v3**
3. Credentials → Create → **API key**
4. Dán vào `.env`: `YOUTUBE_API_KEY=AIza...`

### DeepSeek API

1. Vào [platform.deepseek.com](https://platform.deepseek.com/api_keys)
2. Tạo API key
3. Dán vào `.env`: `DEEPSEEK_API_KEY=sk-...`

---

## 📊 Quota YouTube API

| Endpoint | Cost/call | Ước tính/ngày |
|---|---|---|
| `search.list` | 100 units | ~100 lần search |
| `videos.list` (50 ID) | 1 unit | ~10,000 video lookup |
| `channels.list` | 1 unit | ~10,000 kênh |
| `commentThreads.list` | 1 unit | ~10,000 lần |

---

## 🛠️ Stack

| Layer | Tech |
|---|---|
| Frontend | [Streamlit](https://streamlit.io) (multi-page, dark theme) |
| YouTube API | [google-api-python-client](https://github.com/googleapis/google-api-python-client) |
| Transcript | [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) (7.3k★) |
| Comments | [youtube-comment-downloader](https://github.com/egbertbouman/youtube-comment-downloader) |
| Trends | [pytrends](https://github.com/GeneralMills/pytrends) (`gprop='youtube'`) |
| Sentiment | [vaderSentiment](https://github.com/cjhutto/vaderSentiment) |
| AI | [DeepSeek](https://platform.deepseek.com) via OpenAI SDK |
| Container | [Docker](https://www.docker.com/) |

---

## 📁 Cấu trúc

```
tube-atlas-oss/
├── .env.example          # Template API keys
├── .github/
│   └── workflows/
│       └── ci.yml        # Ruff lint + syntax check
├── .streamlit/
│   └── config.toml       # Dark premium theme
├── Dockerfile            # Docker container
├── app.py                # Dashboard chính
├── core/
│   ├── autocomplete.py   # YouTube keyword suggestions
│   ├── comments.py       # Comment downloader (no API key)
│   ├── i18n.py           # EN/KO/JA/VI strings + language selector
│   ├── keywords.py       # KGR-style score + question buckets
│   ├── lang_detect.py    # Detect transcript language → LangCode
│   ├── llm.py            # DeepSeek integration + Studio pipeline helpers
│   ├── theme.py          # Shared CSS + page_header helper
│   ├── transcript.py     # YouTube transcript (no API key)
│   ├── trends.py         # pytrends YouTube
│   ├── utils.py          # Helpers
│   └── youtube.py        # YouTube Data API v3 + outliers + opportunity score
├── pages/
│   ├── 01_Niche_Finder.py    # opportunity score + breakouts + AI verdict
│   ├── 02_Keyword_Finder.py  # KGR score + question buckets + Send-to-Studio
│   ├── 03_Video_Cloner.py    # auto-language detect + clone kit
│   └── 04_Studio.py          # 5-step wizard (Topic→Title→Outline→Script→Rewrite)
├── tests/                # pytest unit tests
├── assets/
└── requirements.txt
```

---

## 🤝 Contributing

PRs welcome! Fork → Branch → Commit → Pull Request.

---

## 📝 License

MIT — tự do sử dụng, chỉnh sửa, chia sẻ.

---

<div align="center">

**Made with ❤️ using Streamlit + DeepSeek + YouTube Data API**

⭐ Star repo nếu thấy hữu ích!

</div>
