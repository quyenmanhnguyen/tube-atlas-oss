# 📺 tube-atlas skill

Phân tích YouTube (niche pulse, channel audit, competitor discovery, outlier,
transcript) bằng YouTube Data API v3 + DeepSeek LLM. Free tier 10k quota/ngày.

Chạy được trong **Claude Code / Claude.ai / Cursor / Gemini CLI / bất kỳ agent
nào có shell**.

## Cài đặt

```bash
git clone https://github.com/quyenmanhnguyen/tube-atlas-oss
cd tube-atlas-oss
pip install -e .
cp .env.example .env   # điền YOUTUBE_API_KEY + DEEPSEEK_API_KEY
tube-atlas doctor      # verify môi trường
```

## Triggers

Dùng skill này khi user yêu cầu:
- Phân tích 1 chủ đề / niche YouTube ("What's trending in AI news last 30 days")
- Chấm điểm SEO / audit 1 kênh YouTube
- Tìm đối thủ / competitor của 1 kênh
- Lấy transcript / trích dẫn 1 video YouTube
- So sánh nhiều kênh, phân tích video viral
- Sinh title / ý tưởng content YouTube

## Commands

| Lệnh | Mô tả | Ví dụ |
|---|---|---|
| `tube-atlas doctor` | Health check env, API, cache | `tube-atlas doctor` |
| `tube-atlas niche <topic>` | Briefing 30 ngày cho topic | `tube-atlas niche "review iphone 17" --days 30` |
| `tube-atlas audit <@handle>` | Chấm điểm kênh 0-100 | `tube-atlas audit @MrBeast --limit 50` |
| `tube-atlas competitors <@h>` | Tìm top N đối thủ | `tube-atlas competitors @MrBeast -n 5` |
| `tube-atlas cache stats` | Cache stats | `tube-atlas cache stats` |

Flags phổ biến:
- `--region VN|US|JP|KR|ID|TH` — khu vực YouTube
- `--json` — output JSON thay vì markdown (dễ parse trong agent)
- `--no-llm` — bỏ qua DeepSeek nếu không có key
- `--no-sentiment` — bỏ qua phân tích comment (nhanh hơn)

## Workflow mẫu cho agent

**Scenario 1: "Research 30 ngày cho niche AI agent"**
```bash
tube-atlas niche "AI agent" --region VN --days 30
```
→ Trả markdown briefing: nhiệt độ chủ đề, format viral, keyword emerging,
sentiment, 3 ý tưởng video mới. Agent có thể đọc thẳng hoặc parse `--json`.

**Scenario 2: "SEO audit kênh này + tìm đối thủ"**
```bash
tube-atlas audit @MrBeast --limit 100
tube-atlas competitors @MrBeast -n 5 --json > competitors.json
```

**Scenario 3: Agent cần raw data để tự phân tích thêm**
```bash
tube-atlas niche "crypto" --json --no-llm | jq '.youtube.videos[:10]'
```

## Giới hạn

- **YouTube quota:** 10,000 units/ngày free. 1 search ≈ 100 units. Cache SQLite
  giảm 5-10x quota cho query lặp.
- **Google Trends:** hay bị rate-limit trên IP cloud (429). Chạy local máy user OK.
- **Transcript:** `youtube-transcript-api` bị YouTube block IP datacenter. Có
  fallback sang `yt-dlp` tự động.

## Environment

Sau khi `pip install -e .`, CLI `tube-atlas` sẵn trong PATH. Dashboard Streamlit
đầy đủ 13 tools (Niche Pulse, Channel Audit, Competitor Discovery, Outlier Scan,
Best Time to Post, Keyword Generator, Trends, Video/Channel Analyzer, Title
Generator, Video→Text, Content Spinner, Browser Extractor, Comment Analyzer,
Shorts Analyzer):

```bash
streamlit run app.py
```

## Nguồn / credits

- `/last30days-skill` (mvanhorn): cảm hứng parallel multi-source research
- `agent-reach` (Panniantong): cảm hứng `doctor` health-check CLI
- YouTube Data API v3, DeepSeek, pytrends, yt-dlp
