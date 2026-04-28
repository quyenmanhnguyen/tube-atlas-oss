# 📖 Tube Atlas OSS — Hướng dẫn sử dụng (v2.0)

Tài liệu đầy đủ: input / output / công dụng của từng tool trong hệ thống.
7 tool web + 1 CLI + Claude Skill.

---

## Mục lục

1. [Cài đặt nhanh](#1-cài-đặt-nhanh)
2. [Lấy API keys miễn phí](#2-lấy-api-keys-miễn-phí)
3. [7 tools Streamlit](#3-7-tools-streamlit)
   - [🔥 Niche Pulse](#-niche-pulse)
   - [🩺 Channel Audit](#-channel-audit)
   - [📊 Channel Analyzer](#-channel-analyzer)
   - [🎬 Video Analyzer](#-video-analyzer)
   - [🕵️ Competitor Discovery](#-competitor-discovery)
   - [✨ Title & Script Studio](#-title--script-studio)
   - [📝 Video → Text](#-video--text)
   - [📌 My Projects](#-my-projects)
4. [CLI `tube-atlas`](#4-cli-tube-atlas)
5. [Cache & quota](#5-cache--quota)
6. [Claude Skill integration](#6-claude-skill-integration)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Cài đặt nhanh

```bash
git clone https://github.com/quyenmanhnguyen/tube-atlas-oss
cd tube-atlas-oss
pip install -r requirements.txt
pip install -e .                     # để có CLI `tube-atlas`
cp .env.example .env                 # điền 2 API key
streamlit run app.py                 # mở http://localhost:8501
```

**Docker:**

```bash
docker build -t tube-atlas .
docker run -p 8501:8501 --env-file .env tube-atlas
```

## 2. Lấy API keys miễn phí

| Key | Dùng cho | Link | Giới hạn free |
|---|---|---|---|
| `YOUTUBE_API_KEY` | 5/7 tools (tất cả tool gọi YouTube) | https://console.cloud.google.com/apis/credentials | 10,000 units/ngày |
| `DEEPSEEK_API_KEY` | Niche Pulse briefing + Title Studio | https://platform.deepseek.com/api_keys | Trả theo token (rất rẻ ~10x GPT-4) |

Dán vào `.env`:

```env
YOUTUBE_API_KEY=AIza...
DEEPSEEK_API_KEY=sk-...
```

## 3. 7 tools Streamlit

### 🔥 Niche Pulse

**Công dụng:** briefing tổng thể cho 1 niche / topic — lấy song song từ YouTube (N ngày gần nhất) + Google Trends + YouTube Autocomplete + top comments → DeepSeek tổng hợp thành 5-phần markdown.

**Input:**
- Topic (VD: `review iphone 17`, `AI agent`, `dạy tiếng anh`)
- Khu vực: VN / US / JP / KR / ID / TH
- Số ngày: 7–90 (default 30)
- Checkbox: sentiment comments · AI briefing · **Chỉ Shorts (≤60s)** _(v2.0 mới)_

**Output:**
- Metrics: số video mới, tổng view top 25, tỷ lệ Shorts, thời gian quét
- 🤖 AI Briefing markdown 5 mục (nhiệt độ chủ đề, format viral, keyword emerging, sentiment, 3 ý tưởng video)
- Tab "Top videos" (CSV export)
- Tab "Trending tags" (bar chart 15 tags phổ biến nhất)
- Tab "Autocomplete" (30 long-tail keyword)
- Tab "Google Trends" (top + rising queries)
- Tab "Sentiment" (positive/neutral/negative + sample quotes)
- **📥 Export briefing Markdown** _(v2.0 mới)_

**API key:** YouTube (bắt buộc) + DeepSeek (tuỳ chọn cho briefing)
**Quota:** ~110 units / topic / run (1 search + 1 videos.list + 5 comments nếu sentiment)
**Cache:** 1 giờ / (topic, region, days, sentiment, llm, only_shorts)

### 🩺 Channel Audit

**Công dụng:** chấm điểm kênh 0-100 trên 5 tiêu chí + recommendations cải thiện.
**v2.0 mới:** chế độ **so sánh 2 kênh side-by-side** với radar chart overlay + export markdown.

**Input:**
- Mode 1 ("🔎 Audit 1 kênh"): `@handle` hoặc Channel ID + số video phân tích (25–200)
- Mode 2 ("⚖️ So sánh 2 kênh"): 2 ô `@handle` + số video

**Output (single):**
- Metrics kênh: subs / views / videos
- Tổng điểm 0-100 + grade A+/A/B/C/D/F
- Radar chart 5 tiêu chí
- Từng tiêu chí với progress bar + ghi chú
- Recommendations chi tiết
- **📥 Export markdown**

**Output (compare):**
- 2 cột metrics cạnh nhau
- Radar chart overlay 2 màu (tím + xanh lá)
- Bảng điểm 2 kênh cạnh nhau
- Export markdown cả 2

**Công thức:** Upload frequency (20%) + Engagement rate (30%) + Tags coverage (15%) + Title length (15%) + Thumbnail HD (20%)

**Quota:** ~2–4 units / audit (playlistItems + videos.list batched)

### 📊 Channel Analyzer

**Công dụng:** KPI kênh đầy đủ + outlier score + best time to post. Cross-nav nhanh sang Channel Audit / Competitor Discovery.

**Input:** `@handle` / Channel ID / URL + số video (25–500)

**Output:**
- Header: subs, views, videos + **links nhanh sang Audit / Competitors / YouTube**
- Biểu đồ upload theo tháng
- Bảng top videos (sort theo views) kèm Outlier badge (🔥 viral ≥5x median, 📈 trên TB 2-5x)
- Best Time to Post: weekday + hour UTC+7

**Quota:** ~2–10 units (1 channels + N × playlistItems + chunked videos)

### 🎬 Video Analyzer

**Công dụng (v2.0 tái cấu trúc):** 3 tab trong 1 page — không còn Comment Analyzer riêng.

**Input:** URL / Video ID

**Tab "📋 Overview":** stats, tags, topic categories, thumbnail HD.

**Tab "🎯 SEO Score" _(v2.0 mới)_:**
- Score 0-100 + grade
- Chi tiết 6 tiêu chí (title length, description, tags, thumbnail, engagement, keyword coverage)
- Recommendations cụ thể từng tiêu chí

**Tab "💬 Comments & Sentiment" _(gộp từ Comment Analyzer cũ)_:**
- Lấy 20–300 comments (popular / recent)
- VADER sentiment: % tích cực / trung lập / tiêu cực
- Bảng comment + CSV export

**Quota:** 1 unit (videos.list) + 0 unit (comments dùng youtube-comment-downloader không qua API)

### 🕵️ Competitor Discovery

**Công dụng:** tìm top N kênh đối thủ cùng niche.
**v2.0 cải tiến:** keyword extraction có **bigrams** (e.g. "iphone 17" chính xác hơn "iphone") + **recency bias** (video 10 gần nhất weight 1.3x) + expanded stop-words EN+VN + loại token trong tên kênh seed.

**Input:** `@handle` seed + region + số đối thủ muốn tìm (3–10)

**Output:**
- Keywords extract được từ kênh seed
- Bảng top N kênh: title, subs, videos, matched_keywords, score
- Score = matched_keywords × 0.4 + log10(subs) × 0.6

**Quota:** ~30–80 units (1 channels + 1 playlistItems + N × search)
**Cache:** 6 giờ / (seed, region, N)

### ✨ Title & Script Studio

**Công dụng (v2.0 tái cấu trúc):** 3 mode trong 1 page — gộp Title Generator cũ + Content Spinner + brainstorm.

**Mode "🎯 Generate Title":**
- Input: topic + số title (5-20) + ngôn ngữ + phong cách + keyword cần nhồi
- Output: danh sách title + lý do + số ký tự

**Mode "🔁 Rewrite / Spin" _(v2.0 mới — thay Content Spinner)_:**
- Input: nội dung gốc + số biến thể + giọng văn + ngôn ngữ
- Output: danh sách biến thể với note đã đổi gì

**Mode "💡 Brainstorm Ideas":**
- Input: niche + số ý tưởng + ưu tiên format
- Output: ý tưởng video có hook + format + lý do hot

**API key:** DeepSeek (bắt buộc)

### 📝 Video → Text

**Công dụng:** lấy transcript / phụ đề từ video YouTube.

**Input:** URL / Video ID + ngôn ngữ ưu tiên (vi/en/...)

**Output:**
- Full transcript với timestamps
- Fallback tự động: `youtube-transcript-api` → `yt-dlp` nếu IP bị block
- Download .txt / .srt

**API key:** Không cần.

### 📌 My Projects

**Công dụng (v2.0 mới):** bookmark kênh / niche / video yêu thích để mở nhanh lần sau. Lưu local SQLite (`~/.tube_atlas_cache.sqlite`).

**Input:**
- Kind: channel / niche / video
- Label (tên gợi nhớ)
- Value (`@handle` / topic / URL)
- Note tuỳ chọn

**Output:**
- Tabs theo kind với links nhanh sang tool tương ứng
- CRUD: add / delete

**CLI tương đương:**
```bash
tube-atlas projects add channel "Kênh chính" @MrBeast
tube-atlas projects list --kind channel --json
tube-atlas projects del 3
```

## 4. CLI `tube-atlas`

Sau `pip install -e .`:

```bash
tube-atlas doctor                                    # check env + API + cache
tube-atlas doctor --json                             # cho agent parse

tube-atlas niche "AI agent" --days 30                # briefing markdown
tube-atlas niche "shorts vlog" --only-shorts         # chỉ Shorts
tube-atlas niche "crypto" --json --no-llm            # JSON không LLM

tube-atlas audit @MrBeast --limit 100                # markdown
tube-atlas audit @MrBeast --json                     # JSON cho agent

tube-atlas competitors @MrBeast -n 5                 # markdown
tube-atlas competitors @MrBeast -n 5 --json          # JSON

tube-atlas cache stats                               # cache info
tube-atlas cache clear                               # xoá cache

tube-atlas projects list --kind channel              # list bookmarks
tube-atlas projects add channel "Main" @MrBeast
tube-atlas projects del 1
```

Tất cả các command hỗ trợ `--json` (v2.0 fix — trước đây chỉ `niche` / `competitors` có).

## 5. Cache & quota

**SQLite cache:** `~/.tube_atlas_cache.sqlite` — chung cho web + CLI + bookmarks.

| Endpoint | TTL |
|---|---|
| Niche Pulse | 1 giờ |
| Videos.list | 6 giờ |
| Search | 3 giờ |
| Competitor Discovery | 6 giờ |

**YouTube API quota (10,000 units/ngày):**

| Call | Units |
|---|---|
| search.list | 100 |
| videos.list (batch 50) | 1 |
| channels.list | 1 |
| playlistItems.list | 1 |

→ Niche Pulse 1 topic ≈ 101 units. 1 ngày free chạy được ~99 topic.

## 6. Claude Skill integration

Copy thư mục `skills/tube-atlas/` vào:
- Claude Code: `~/.claude/skills/tube-atlas/`
- Cursor: (tự sắp xếp theo convention của bạn)

Rồi trong Claude:

> niche pulse review iphone 17 trong 14 ngày ở VN

→ Claude tự gọi `tube-atlas niche "review iphone 17" --region VN --days 14 --json`, parse JSON, trả briefing trong chat.

## 7. Troubleshooting

| Lỗi | Cách fix |
|---|---|
| `ImportError: dotenv` | `pip install python-dotenv` |
| YouTube 403 quotaExceeded | Đợi reset UTC 00:00 hoặc enable billing (quota 50k+) |
| Trends 429 Too Many Requests | Cloud IP bị Google block — chạy local máy OK |
| Transcript "no subtitles" | Fallback yt-dlp tự động; video có thể tắt subtitle hoàn toàn |
| DeepSeek 401 | Key sai / revoked — tạo lại tại https://platform.deepseek.com/api_keys |
| `streamlit: command not found` | `pip install streamlit` (hoặc `pip install -r requirements.txt`) |

---

## Tóm tắt 1 dòng / tool

- 🔥 **Niche Pulse** — quét song song YT + Trends + Autocomplete + comments → AI briefing. Có filter Shorts + export Markdown.
- 🩺 **Channel Audit** — chấm điểm kênh 0-100 (5 tiêu chí). So sánh 2 kênh cạnh nhau + export Markdown.
- 📊 **Channel Analyzer** — KPI + outlier viral + best time to post. Cross-nav nhanh sang các tool khác.
- 🎬 **Video Analyzer** — stats + SEO score 0-100 + sentiment comments (3 tab).
- 🕵️ **Competitor Discovery** — auto tìm top N đối thủ cùng niche. Keyword extraction bigrams + recency bias.
- ✨ **Title & Script Studio** — sinh title / rewrite-spin / brainstorm ý tưởng (3 mode).
- 📝 **Video → Text** — transcript (+ yt-dlp fallback).
- 📌 **My Projects** — bookmark kênh / niche / video y thích.

7 tools thay thế Tube Atlas Premium / VidIQ / TubeBuddy cho 80% use cases với giá $0.
