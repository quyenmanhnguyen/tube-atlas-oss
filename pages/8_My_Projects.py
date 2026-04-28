"""My Projects — lưu kênh, niche, video hay theo dõi."""
from __future__ import annotations

import datetime as dt

import streamlit as st

from core import projects

st.set_page_config(page_title="My Projects", page_icon="📌", layout="wide")
from core.theme import inject  # noqa: E402

inject()
st.title("📌 My Projects")
st.caption("Bookmark kênh, niche, video để mở nhanh lần sau. Lưu local trên máy bạn.")


def _fmt_ts(ts: int) -> str:
    return dt.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


# -------- Add new --------
with st.expander("➕ Thêm bookmark mới", expanded=False):
    with st.form("add_project"):
        c1, c2 = st.columns([1, 3])
        kind = c1.selectbox("Loại", ["channel", "niche", "video"])
        label = c2.text_input("Tên gợi nhớ", placeholder="vd: Kênh chính, Niche AI...")
        value = st.text_input(
            "Giá trị",
            placeholder={
                "channel": "@MrBeast hoặc UCX6OQ3DkcsbYNE6H8uQQuVA",
                "niche": "review iphone 17",
                "video": "https://youtube.com/watch?v=...",
            }[kind],
        )
        note = st.text_area("Ghi chú (tuỳ chọn)", height=80)
        ok = st.form_submit_button("Lưu bookmark", type="primary")
    if ok:
        if not label.strip() or not value.strip():
            st.warning("Nhập đủ label + value.")
        else:
            pid = projects.add(kind, label, value, note)
            st.success(f"Đã lưu bookmark #{pid}")
            st.rerun()


# -------- List by kind --------
tabs = st.tabs(["📺 Channels", "🎯 Niches", "🎬 Videos"])
kinds = ["channel", "niche", "video"]

for tab, k in zip(tabs, kinds):
    with tab:
        items = projects.list_all(kind=k)
        if not items:
            st.info(f"Chưa có bookmark {k} nào.")
            continue
        for item in items:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 3, 1])
                with col1:
                    st.markdown(f"**{item['label']}**")
                    st.caption(f"`{item['value']}`")
                    if item["note"]:
                        st.caption(f"📝 {item['note']}")
                with col2:
                    st.caption(f"🕒 {_fmt_ts(item['created_at'])}")
                    # Quick action links
                    if k == "channel":
                        handle = item["value"].lstrip("@")
                        st.markdown(
                            "👉 [📊 Analyzer](/Channel_Analyzer)  ·  "
                            "[🩺 Audit](/Channel_Audit)  ·  "
                            "[🕵️ Competitors](/Competitor_Discovery)  ·  "
                            f"[▶️ YouTube](https://youtube.com/@{handle})"
                        )
                    elif k == "niche":
                        st.markdown(
                            "👉 [🔥 Mở Niche Pulse](/Niche_Pulse)  "
                            "rồi dán topic vào form."
                        )
                    else:
                        st.markdown(
                            "👉 [🎬 Mở Video Analyzer](/Video_Analyzer)  ·  "
                            "[📝 Transcript](/Video_To_Text)"
                        )
                with col3:
                    if st.button("🗑️", key=f"del_{item['id']}"):
                        projects.delete(item["id"])
                        st.rerun()

st.divider()
st.caption(
    f"Tổng {projects.count()} bookmarks. "
    f"Lưu tại `~/.tube_atlas_cache.sqlite` (cùng cache)."
)
