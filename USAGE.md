# 📖 Tube Atlas OSS — Hướng dẫn đầy đủ

Tài liệu này liệt kê **toàn bộ 13 tính năng dashboard + 5 lệnh CLI** của Tube Atlas OSS, kèm yêu cầu đầu vào, kết quả đầu ra, công dụng thực tế và ví dụ.

---

## 🚀 Cài đặt nhanh

```bash
git clone https://github.com/quyenmanhnguyen/tube-atlas-oss
cd tube-atlas-oss

# Cài dependencies
pip install -r requirements.txt
# Hoặc (để có lệnh CLI `tube-atlas` global)
pip install -e .

# Cấu hình keys
cp .env.example .env
# Mở .env và điền:
#   YOUTUBE_API_KEY=AIza...
#   DEEPSEEK_API_KEY=sk-...
#   DEEPSEEK_MODEL=deepseek-chat   (mặc định, không cần đổi)

# Chạy dashboard
streamlit run app.py
# Mở http://localhost:8501

# Hoặc chạy CLI
tube-atlas doctor
```

### Lấy API keys (miễn phí)

| Key | Lấy ở đâu | Free tier | Bắt buộc? |
|---|---|---|---|
| `YOUTUBE_API_KEY` | [Google Cloud Console](https://console.cloud.google.com/apis/credentials) → Enable YouTube Data API v3 → Create API Key | 10.000 units/ngày (~100 search hoặc 10.000 video lookup) | ✅ Cần cho 8/13 tools |
| `DEEPSEEK_API_KEY` | [platform.deepseek.com/api_keys](https://platform.deepseek.com/api_keys) | ~3M tokens đầu tiên free | ⚠️ Cần cho 3 tools có AI |

**5/13 tool hoạt động không cần bất kỳ key nào.**

---

## 🛠️ 13 tính năng Dashboard

Mỗi tool là 1 trang Streamlit trong sidebar. Dưới đây mô tả theo thứ tự.

### 1. 🔑 Keyword Generator — `pages/1_Keyword_Generator.py`

Khám phá long-tail keywords bằng YouTube Autocomplete.

| Thuộc tính | Giá trị |
|---|---|
| **API key cần** | Không |
| **Input** | Seed keyword (VD `review iphone 17`), ngôn ngữ (`vi`/`en`), khu vực (`VN`, `US`, …), có bật "mở rộng alphabet" không |
| **Output** | Danh sách 30–300 keyword kèm export CSV |
| **Công dụng** | Tìm từ khoá người dùng đang gõ thật trong YouTube → dùng để đặt title, tag, nghiên cứu nội dung |

**Ví dụ use case:** Bạn muốn làm series "dạy tiếng Anh" → seed = `học tiếng anh` → output: `học tiếng anh giao tiếp`, `học tiếng anh qua phim`, `học tiếng anh cho người mới bắt đầu`, v.v. → ưu tiên những cụm có nhiều người gõ.

---

### 2. 📈 Trends Generator — `pages/2_Trends_Generator.py`

Google Trends cho nền tảng YouTube (`gprop=youtube`).

| Thuộc tính | Giá trị |
|---|---|
| **API key cần** | Không |
| **Input** | Danh sách keyword (tối đa 5 cái), timeframe (1 tháng/3 tháng/12 tháng), khu vực |
| **Output** | Biểu đồ interest theo thời gian + **related queries** (top + rising) + trending searches theo quốc gia |
| **Công dụng** | So sánh độ hot của nhiều chủ đề, phát hiện topic "đang lên" (rising queries) |

**Lưu ý:** Google Trends hay rate-limit IP datacenter (AWS/GCP) → chạy local máy nhà sẽ ổn định.

**Ví dụ use case:** So 3 keyword `tiktok vs youtube shorts vs instagram reels` trong 12 tháng → thấy Shorts đang tăng mạnh → quyết định đầu tư vào Shorts.

---

### 3. 🎬 Video Analyzer — `pages/3_Video_Analyzer.py`

Phân tích chi tiết 1 video bất kỳ.

| Thuộc tính | Giá trị |
|---|---|
| **API key cần** | ✅ YouTube |
| **Input** | URL video hoặc Video ID (VD `https://youtu.be/dQw4w9WgXcQ` hoặc `dQw4w9WgXcQ`) |
| **Output** | Thumbnail, title, channel, views, likes, comments, duration, published date, **engagement rate %**, tags đầy đủ, category, made-for-kids flag |
| **Công dụng** | Reverse-engineer video viral của đối thủ: xem tags nào họ dùng, engagement rate bao nhiêu, duration sweet spot |

**Ví dụ use case:** Dán link video competitor đạt 10M view → thấy họ dùng 18 tag, video dài 11:42, engagement 6.2% → bắt chước format.

---

### 4. 📊 Channel Analyzer — `pages/4_Channel_Analyzer.py`

Phân tích toàn diện 1 kênh. **Đã nâng cấp v1.1 với Outlier Score + Best Time to Post.**

| Thuộc tính | Giá trị |
|---|---|
| **API key cần** | ✅ YouTube |
| **Input** | `@handle` hoặc `Channel ID` (UC…), số video lấy (25–200) |
| **Output** | KPI kênh (subs, total views, video count), biểu đồ **upload frequency theo tháng**, bảng top 20 video sort theo view, **⚡ Outlier Score** (🔥 Viral / 📈 Trên TB / ✅ BT / ⬇️ Yếu cho mỗi video), **⏰ Best Time to Post** (ngày trong tuần + giờ VN UTC+7) |
| **Công dụng** | Hiểu tổng quan 1 kênh, phát hiện video nào viral bất thường (≥5x median), biết khi nào kênh hay post |

**Outlier Score logic:** `views_video / median(views_kênh)`. ≥5x = 🔥 Viral, 2–5x = 📈 Trên TB, 0.5–2x = ✅ BT, <0.5x = ⬇️ Yếu.

**Ví dụ use case:** Phân tích `@MrBeast` → thấy 6 video viral ≥5x median, best post Wednesday 23:00 VN → nếu bắt chước niche, nên post tối thứ 4.

---

### 5. ✨ Title Generator — `pages/5_Title_Generator.py`

AI sinh title CTR cao bằng DeepSeek.

| Thuộc tính | Giá trị |
|---|---|
| **API key cần** | ✅ DeepSeek |
| **Input** | Mô tả video + niche (VD "Review iPhone 17 Pro Max, nhấn mạnh camera"), số title muốn (3–20), ngôn ngữ |
| **Output** | Danh sách title kèm **đếm ký tự** + **giải thích lý do mỗi title CTR cao** (hook gì, emoti cảm xúc nào) |
| **Công dụng** | Brainstorm 10 title trong 5s, chọn cái ưng ý. Mỗi title dài 45–60 ký tự đúng chuẩn YouTube (không bị cắt) |

**Ví dụ use case:** Nhập "Review iPhone 17 Pro Max, camera đỉnh cao" → AI trả 10 title như "iPhone 17 Pro Max: Camera này sẽ thay thế máy ảnh DSLR?" (52 ký tự, dùng câu hỏi tạo tò mò).

---

### 6. 📝 Video → Text — `pages/6_Video_To_Text.py`

Trích xuất transcript / phụ đề.

| Thuộc tính | Giá trị |
|---|---|
| **API key cần** | Không |
| **Input** | URL video hoặc Video ID, ngôn ngữ ưu tiên (`vi`, `en`, `auto`) |
| **Output** | Transcript đầy đủ + download .txt / .srt, thống kê số từ, thời lượng |
| **Công dụng** | Chuyển video dài thành văn bản để (a) đọc nhanh, (b) làm subtitle, (c) feed cho LLM viết lại / tóm tắt |

**Cơ chế 2 lớp:** Thử `youtube-transcript-api` trước → nếu fail (IP block, phổ biến trên cloud) tự động fallback sang `yt-dlp`. Local máy nhà hầu như luôn work lớp 1.

**Ví dụ use case:** Lấy transcript video lecture 2 giờ → paste vào ChatGPT "tóm tắt thành 10 bullet points" → tiết kiệm 2 giờ.

---

### 7. 🌀 Content Spinner — `pages/7_Content_Spinner.py`

AI spin / rewrite / sinh ý tưởng nội dung.

| Thuộc tính | Giá trị |
|---|---|
| **API key cần** | ✅ DeepSeek |
| **Input** | Văn bản gốc (script, mô tả video, 1 câu brief) + chế độ (`spin nhẹ`, `viết lại sâu`, `sinh 5 ý tưởng mới`), ngôn ngữ |
| **Output** | Text đã spin / ý tưởng mới kèm hook gợi ý |
| **Công dụng** | Làm nhiều version title/description/script cho A-B test. Phá block sáng tạo khi bí ý tưởng |

**Ví dụ use case:** Dán script cũ → chọn "sinh 5 ý tưởng mới theo format reaction" → AI trả 5 concept hoàn toàn khác.

---

### 8. 🕸️ Browser Extractor — `pages/8_Browser_Extractor.py`

Search YouTube bulk + scrape data ngay trên dashboard.

| Thuộc tính | Giá trị |
|---|---|
| **API key cần** | ✅ YouTube |
| **Input** | Query (VD `review iphone 17 pro max`), khu vực, sort (`relevance`/`viewCount`/`date`/`rating`), số kết quả (10–50) |
| **Output** | Bảng 10–50 video kèm view count, channel, published, link + export CSV |
| **Công dụng** | Spy competitor, thu thập data trong 1 niche cho pitch/research, lấy đầu vào cho Title Generator |

**Ví dụ use case:** Search `review iphone 17 pro max` VN sort by viewCount → lấy 30 video top để biết ai đang dominate niche này.

---

### 9. 💬 Comment Analyzer — `pages/9_Comment_Analyzer.py`

Sentiment analysis trên comment (VADER) + AI deep insight.

| Thuộc tính | Giá trị |
|---|---|
| **API key cần** | Không (VADER) · ✅ DeepSeek (nếu muốn deep insight) |
| **Input** | Video URL/ID, số comment lấy (50–500), sort (`popular`/`recent`), bật VADER / DeepSeek insight |
| **Output** | Phân phối positive/neutral/negative, word cloud, top phrases, **DeepSeek insight**: khán giả khen gì, chê gì, câu hỏi phổ biến |
| **Công dụng** | Hiểu khán giả nghĩ gì về video của bạn hoặc đối thủ → điều chỉnh nội dung |

**Ví dụ use case:** Phân tích 300 comment video của bạn → AI phát hiện 40% khán giả hỏi "link mua ở đâu" → thêm link vào pinned comment + description.

---

### 10. 📱 Shorts Analyzer — `pages/10_Shorts_Analyzer.py`

Phát hiện & phân tích YouTube Shorts.

| Thuộc tính | Giá trị |
|---|---|
| **API key cần** | ✅ YouTube |
| **Input** | Query, khu vực, số kết quả |
| **Output** | Bảng video ≤60s (Shorts), view/like trung bình, hashtag thường dùng, tỷ lệ Shorts vs long-form trong kết quả search |
| **Công dụng** | Research niche Shorts: xem Shorts có dominate niche này không, hashtag nào phổ biến |

**Ví dụ use case:** Search `shorts vlog` VN → 18/20 là Shorts, #fyp và #shorts mỗi cái xuất hiện 15+ lần → chuẩn hoá dùng 2 hashtag này.

---

### 11. 🩺 Channel Audit — `pages/11_Channel_Audit.py` **(v1.1, mới)**

Chấm điểm kênh 0–100 trên 5 tiêu chí + recommendation.

| Thuộc tính | Giá trị |
|---|---|
| **API key cần** | ✅ YouTube |
| **Input** | `@handle` hoặc Channel ID, số video phân tích (25–200) |
| **Output** | Tổng điểm **0–100 + Grade A+ → F**, radar chart, breakdown per tiêu chí + note, danh sách recommendation cụ thể |
| **Công dụng** | Audit SEO/chất lượng kênh giống VidIQ's Channel Audit (~$24/tháng). Biết kênh đang yếu chỗ nào để sửa |

**5 tiêu chí + weight:**

| Tiêu chí | Weight | Logic chấm |
|---|---|---|
| Upload frequency | 20% | TB ngày/video × độ ổn định (std/mean) |
| Engagement rate | 30% | (likes + comments) / views; 1% = OK, 4% = xuất sắc |
| Tags coverage | 15% | % video có tag × sweet spot 8–15 tag |
| Title length | 15% | % title trong khoảng 30–70 ký tự |
| Thumbnail HD | 20% | % video có thumbnail `maxres` |

**Ví dụ use case:** Audit `@MrBeast` → **61.2/100 Grade C**. Thumbnail HD 100% (xuất sắc) nhưng tags 0% (MrBeast ẩn tags public) → nếu bạn là kênh nhỏ hơn, bật tags đầy đủ sẽ win điểm ở mặt này.

---

### 12. 🔥 Niche Pulse — `pages/12_Niche_Pulse.py` **(v1.2, mới)**

Briefing song song YouTube + Trends + Autocomplete + top comments → AI tổng hợp. Cảm hứng từ `/last30days-skill`.

| Thuộc tính | Giá trị |
|---|---|
| **API key cần** | ✅ YouTube · ⚠️ DeepSeek (nếu muốn AI briefing) |
| **Input** | Chủ đề (VD `AI agent`), khu vực, số ngày (7–90), bật sentiment, bật LLM briefing |
| **Output** | 4 metric cards + **🤖 AI Briefing 5 mục** (nhiệt độ chủ đề, format viral, keyword emerging, sentiment, 3 ý tưởng video) + 5 tab raw data (top videos, trending tags, autocomplete, Google Trends, sentiment detail) |
| **Công dụng** | "What's hot in [niche] right now" trong 30–60 giây → lên plan content tuần này |

**Cơ chế:** ThreadPoolExecutor 3 workers chạy song song YouTube (`publishedAfter=N ngày trước, sort=viewCount`) + Autocomplete expansion + Google Trends. Sau đó (optional) gom 30 comment × 5 video hot nhất → VADER sentiment → DeepSeek synthesize.

**Cache:** 1 giờ/topic (SQLite).

**Ví dụ use case:** `AI agent` 30 ngày → AI briefing chỉ ra "video về *Cloud run AI agents* đang trending, hook thường là câu hỏi *Can AI replace [role]?*" → bạn lên kịch bản theo đúng pattern đó.

---

### 13. 🕵️ Competitor Discovery — `pages/13_Competitor_Discovery.py` **(v1.2, mới)**

Auto tìm top N kênh cùng niche dựa trên seed channel.

| Thuộc tính | Giá trị |
|---|---|
| **API key cần** | ✅ YouTube |
| **Input** | Kênh seed (`@handle` hoặc Channel ID), khu vực, số đối thủ muốn (3–15) |
| **Output** | Keywords extract từ kênh seed, bảng top N đối thủ kèm subs, videos, views, matched keywords, score, link + export CSV |
| **Công dụng** | Dựng bản đồ cạnh tranh trong niche: ai là competitor lớn nhất của bạn? |

**Thuật toán:** Lấy tags + title tokens của 25 video gần nhất của seed (tags weighted 2x) → song song search top 10 keyword (5 workers) → dedupe channel IDs → rank bằng `matched_keywords × 0.4 + log10(subs) × 0.6`.

**Ví dụ use case:** Seed `@MrBeast` → top 5 đối thủ bao gồm Mark Rober (76M subs), Amaury Guichon (23M subs) → mở Channel Audit cho từng kênh để so sánh điểm SEO.

**Quota tốn:** ~50–80 units/lần chạy (vì 10 search × ~5 unit sau cache). Cache 6h.

---

## 🖥️ CLI — `tube-atlas` command

Sau `pip install -e .` CLI có sẵn trong PATH. Tất cả command có `--json` flag để pipe vào agent.

### `tube-atlas doctor`

Health check môi trường.

```bash
tube-atlas doctor
```

**Input:** Không. **Output:**
- YOUTUBE_API_KEY set? + probe search test
- DEEPSEEK_API_KEY set? + probe chat test
- Cache path + entries (total/active/expired)
- Transcript deps (transcript-api + yt-dlp)

Exit code `0` nếu mọi check xanh, `1` nếu có fail.

---

### `tube-atlas niche <topic>`

Niche Pulse ra markdown / JSON.

```bash
tube-atlas niche "review iphone 17" --days 30
tube-atlas niche "AI agent" --region VN --no-llm --no-sentiment
tube-atlas niche "crypto" --json > /tmp/crypto.json
```

| Flag | Giá trị mặc định | Mô tả |
|---|---|---|
| `--region` | `VN` | Khu vực YouTube |
| `--days` | `30` | Số ngày lùi về quá khứ |
| `--no-sentiment` | off | Bỏ phân tích comment (nhanh hơn ~20s) |
| `--no-llm` | off | Bỏ qua DeepSeek briefing |
| `--json` | off | In JSON raw thay vì markdown |

---

### `tube-atlas audit <@handle>`

Chấm điểm kênh 0–100.

```bash
tube-atlas audit @MrBeast --limit 50
tube-atlas audit UCX6OQ3DkcsbYNE6H8uQQuVA --limit 100
```

| Flag | Giá trị mặc định | Mô tả |
|---|---|---|
| `--limit` | `50` | Số video lấy để phân tích (max 200) |

**Output:** Markdown table với tổng điểm + grade + 5 row chi tiết + recommendations.

---

### `tube-atlas competitors <@handle>`

Tìm top N đối thủ.

```bash
tube-atlas competitors @MrBeast -n 5
tube-atlas competitors @MrBeast -n 10 --json | jq '.competitors[].title'
```

| Flag | Giá trị mặc định | Mô tả |
|---|---|---|
| `--region` | `VN` | Khu vực search |
| `-n` | `5` | Số đối thủ |
| `--json` | off | Output JSON |

---

### `tube-atlas cache stats` / `tube-atlas cache clear`

Quản lý SQLite cache.

```bash
tube-atlas cache stats   # Xem total/active/expired entries
tube-atlas cache clear   # Xoá toàn bộ cache
```

Cache path: `~/.tube_atlas_cache.sqlite`

---

## 💾 Cơ chế cache (SQLite)

Tube Atlas tự cache YouTube API response để tiết kiệm quota:

| Endpoint | TTL mặc định |
|---|---|
| `search.list` | 3 giờ |
| `videos.list` / `channels.list` | 6 giờ |
| Niche Pulse full pipeline | 1 giờ |
| Competitor Discovery | 6 giờ |

**Tiết kiệm:** ~5–10x quota nếu bạn mở lại cùng kênh / search cùng query trong TTL.

Xoá cache: `tube-atlas cache clear` hoặc `rm ~/.tube_atlas_cache.sqlite`.

---

## 📊 Quota YouTube API (free 10.000 units/ngày)

| Endpoint | Cost/call | Số lần/ngày |
|---|---|---|
| `search.list` | 100 units | ~100 |
| `videos.list` (batch 50 ID) | 1 unit | ~10.000 video lookup |
| `channels.list` | 1 unit | ~10.000 kênh |
| `commentThreads.list` | 1 unit | ~10.000 lần |

**Ước tính quota theo tool:**

| Tool | 1 lần chạy |
|---|---|
| Keyword Generator | 0 (không dùng API) |
| Trends Generator | 0 |
| Video Analyzer | 1 unit |
| Channel Analyzer (100 video) | ~3–5 units |
| Browser Extractor | 100 units |
| Shorts Analyzer | 100 units |
| Channel Audit (100 video) | ~5 units |
| **Niche Pulse** | ~105 units (1 search + 25 video lookup) |
| **Competitor Discovery** | ~500–800 units (5 search × 100) |

→ Dùng bình thường hàng ngày không lo cháy quota. Chỉ cần thận trọng với Competitor Discovery.

---

## 🧩 Claude Skill (Claude Code / Cursor / Gemini CLI)

Xem `skills/tube-atlas/SKILL.md`. Ngắn gọn:

```bash
# Claude Code
git clone https://github.com/quyenmanhnguyen/tube-atlas-oss ~/.claude/skills/tube-atlas
cd ~/.claude/skills/tube-atlas && pip install -e .

# Sau đó, trong Claude Code:
# /tube-atlas niche "AI agent" --days 30
```

Agent sẽ tự gọi CLI ở trên và parse output.

---

## 🐛 Troubleshooting

| Lỗi | Nguyên nhân | Fix |
|---|---|---|
| `Thiếu YOUTUBE_API_KEY` | Chưa điền `.env` | `cp .env.example .env` → điền key |
| `429 Too Many Requests` khi dùng Trends | Google block IP cloud | Chạy local máy nhà, hoặc thử sau |
| Video → Text: "IP blocked" | YouTube chặn `youtube-transcript-api` từ datacenter IP | App tự fallback `yt-dlp`. Nếu vẫn fail, chạy trên local máy |
| `401 DeepSeek invalid` | Key sai / đã revoke | Tạo key mới tại https://platform.deepseek.com/api_keys |
| Competitor Discovery không ra kết quả chuẩn | Keyword extract ngắn / generic | Dùng `core/competitors.py::_extract_keywords` để thêm stop-words vào list |
| `quotaExceeded` từ YouTube | Đã tiêu hết 10k units/ngày | Đợi reset 00:00 Pacific Time hoặc tạo project Google Cloud thứ 2 |

---

## 🔗 Links quan trọng

- **Repo:** https://github.com/quyenmanhnguyen/tube-atlas-oss
- **PR #1 (v1.1):** https://github.com/quyenmanhnguyen/tube-atlas-oss/pull/1
- **PR #2 (v1.2):** https://github.com/quyenmanhnguyen/tube-atlas-oss/pull/2
- **Cảm hứng:** [`/last30days-skill`](https://github.com/mvanhorn/last30days-skill) · [`agent-reach`](https://github.com/Panniantong/Agent-Reach)

---

## 📝 Tóm tắt 1 dòng cho mỗi tool

| # | Tool | 1 câu |
|---|---|---|
| 1 | Keyword Generator | Từ 1 seed → 30-300 long-tail keyword người thật đang gõ |
| 2 | Trends Generator | So sánh độ hot nhiều chủ đề + rising queries |
| 3 | Video Analyzer | Reverse-engineer 1 video viral: tags, engagement, duration |
| 4 | Channel Analyzer | Toàn cảnh 1 kênh + outlier score + best time to post |
| 5 | Title Generator | 10 title CTR cao trong 5 giây + lý do |
| 6 | Video → Text | Transcript full + SRT download |
| 7 | Content Spinner | Spin/rewrite/brainstorm ý tưởng |
| 8 | Browser Extractor | Search bulk + CSV export 1 niche |
| 9 | Comment Analyzer | Sentiment + audience insight bằng AI |
| 10 | Shorts Analyzer | Phát hiện Shorts & hashtag trong niche |
| 11 | Channel Audit | Điểm SEO 0-100 + recommendation cụ thể |
| 12 | Niche Pulse | Briefing 30 ngày song song YT+Trends+AI |
| 13 | Competitor Discovery | Auto tìm 5 đối thủ cùng niche |

**CLI:** `tube-atlas doctor|niche|audit|competitors|cache` — mọi lệnh có `--json` để pipe vào agent.
