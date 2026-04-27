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
| `tube-atlas doctor` | Health check env, API, cache | `tube-atlas doctor --json` |
| `tube-atlas niche <topic>` | Briefing N ngày cho topic | `tube-atlas niche "review iphone 17" --days 30 --only-shorts` |
| `tube-atlas audit <@handle>` | Chấm điểm kênh 0-100 | `tube-atlas audit @MrBeast --limit 50 --json` |
| `tube-atlas competitors <@h>` | Tìm top N đối thủ | `tube-atlas competitors @MrBeast -n 5 --json` |
| `tube-atlas cache stats\|clear` | Quản lý cache | `tube-atlas cache stats --json` |
| `tube-atlas projects list\|add\|del` | Quản lý bookmarks | `tube-atlas projects add channel "Main" @MrBeast` |

Flags phổ biến:
- `--region VN|US|JP|KR|ID|TH` — khu vực YouTube
- `--json` — output JSON thay vì markdown (**có trên mọi command** từ v2.0)
- `--no-llm` — bỏ qua DeepSeek nếu không có key
- `--no-sentiment` — bỏ qua phân tích comment (nhanh hơn)
- `--only-shorts` (niche) — chỉ video ≤60s

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
đầy đủ **7 tools** (v2.0 slim & focused):

1. **Niche Pulse** — parallel research + export markdown + filter Shorts
2. **Channel Audit** — score 0-100 + so sánh 2 kênh + export markdown
3. **Channel Analyzer** — KPI + outlier + best time to post
4. **Video Analyzer** — stats + SEO score 0-100 + sentiment comments (3 tab)
5. **Competitor Discovery** — auto-find top N đối thủ
6. **Title & Script Studio** — title gen / rewrite-spin / brainstorm (3 mode)
7. **Video → Text** — transcript + yt-dlp fallback

+ **My Projects** — bookmark kênh / niche / video yêu thích

```bash
streamlit run app.py
```

## Nguồn / credits

- `/last30days-skill` (mvanhorn): cảm hứng parallel multi-source research
- `agent-reach` (Panniantong): cảm hứng `doctor` health-check CLI
- YouTube Data API v3, DeepSeek, pytrends, yt-dlp
