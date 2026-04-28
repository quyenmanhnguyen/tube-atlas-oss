"""Video → Text — transcript YouTube."""
from __future__ import annotations

import streamlit as st

from core import transcript, youtube as yt

# st.set_page_config moved to app.py (st.navigation entrypoint)
from core.theme import inject; inject()
st.title("📝 Video → Text Converter")
st.caption("Lấy transcript / phụ đề YouTube (kể cả auto-caption).")

url = st.text_input("URL hoặc Video ID", placeholder="https://www.youtube.com/watch?v=...")
langs = st.multiselect(
    "Ngôn ngữ ưu tiên (theo thứ tự)", ["vi", "en", "ja", "ko", "zh-Hans", "zh-Hant", "fr", "es"], default=["vi", "en"]
)

if url:
    try:
        vid = yt.parse_video_id(url)
        with st.spinner("Đang lấy transcript..."):
            segs = transcript.fetch_transcript(vid, languages=langs)
    except Exception as e:
        st.error(f"Lỗi: {e}")
        st.stop()
    if not segs:
        st.warning("Video không có phụ đề.")
        st.stop()

    t1, t2, t3 = st.tabs(["Plain text", "SRT", "Segments"])
    with t1:
        txt = transcript.transcript_to_text(segs)
        st.text_area("Transcript", txt, height=400)
        st.download_button("⬇️ Tải .txt", txt.encode("utf-8"), file_name=f"{vid}.txt")
    with t2:
        srt = transcript.transcript_to_srt(segs)
        st.code(srt[:5000])
        st.download_button("⬇️ Tải .srt", srt.encode("utf-8"), file_name=f"{vid}.srt")
    with t3:
        st.dataframe(segs, use_container_width=True, hide_index=True)
