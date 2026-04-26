<div align="center">

# 📺 Tube Atlas OSS

**Bộ công cụ nghiên cứu YouTube mã nguồn mở — thay thế Tube Atlas Premium / VidIQ / TubeBuddy**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.36+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![DeepSeek](https://img.shields.io/badge/AI-DeepSeek-blue)](https://platform.deepseek.com)
[![CI](https://github.com/quyenmanhnguyen/tube-atlas-oss/actions/workflows/ci.yml/badge.svg)](https://github.com/quyenmanhnguyen/tube-atlas-oss/actions)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](#-docker)

<img src="https://img.shields.io/badge/Tools-10%20features-7c3aed?style=for-the-badge" alt="10 features">

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

## ✨ Tính năng

| # | Tool | Mô tả | Cần API key? |
|---|---|---|---|
| 🔑 | **Keyword Generator** | Long-tail keywords từ YouTube Autocomplete | ❌ Free |
| 📈 | **Trends Generator** | Google Trends cho YouTube + related queries | ❌ Free |
| 🎬 | **Video Analyzer** | Stats, engagement, tags chi tiết | ✅ YouTube |
| 📊 | **Channel Analyzer** | KPI kênh, upload frequency, top videos | ✅ YouTube |
| ✨ | **Title Generator** | Gợi ý title CTR cao bằng AI | ✅ DeepSeek |
| 📝 | **Video → Text** | Transcript / phụ đề từ YouTube | ❌ Free |
| 🌀 | **Content Spinner** | Spin / rewrite nội dung bằng AI | ✅ DeepSeek |
| 🕸️ | **Browser Extractor** | Search + scrape data bulk | ✅ YouTube |
| 💬 | **Comment Analyzer** | Sentiment analysis + audience insight | ❌ Free* |
| 🩳 | **Shorts Analyzer** | Phân tích YouTube Shorts & trends | ✅ YouTube |

> **6/10 tools hoạt động ngay** mà không cần API key nào!

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
│   ├── llm.py            # DeepSeek integration
│   ├── theme.py          # Premium CSS module
│   ├── transcript.py     # YouTube transcript (no API key)
│   ├── trends.py         # pytrends YouTube
│   ├── utils.py          # Helpers
│   └── youtube.py        # YouTube Data API v3 wrapper
├── pages/                # 10 Streamlit pages
│   ├── 1_Keyword_Generator.py
│   ├── 2_Trends_Generator.py
│   ├── ...
│   └── 10_Shorts_Analyzer.py
├── assets/               # Screenshots
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
