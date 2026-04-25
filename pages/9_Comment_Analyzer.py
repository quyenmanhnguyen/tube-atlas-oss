"""Comment Analyzer — fetch comment + sentiment (VADER nhanh + DeepSeek deep)."""
from __future__ import annotations

import json

import pandas as pd
import plotly.express as px
import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from core import comments, llm, youtube as yt

st.set_page_config(page_title="Comment Analyzer", page_icon="💬", layout="wide")
from core.theme import inject; inject()
st.title("💬 Comment Analyzer")
st.caption("Lấy comment YouTube và phân tích sentiment.")

with st.form("c"):
    url = st.text_input("URL hoặc Video ID")
    c1, c2, c3 = st.columns(3)
    with c1:
        n = st.slider("Số comment", 50, 1000, 200, step=50)
    with c2:
        sort = st.selectbox("Sort", ["popular", "recent"], index=0)
    with c3:
        engine = st.selectbox("Sentiment engine", ["VADER (nhanh, EN)", "DeepSeek (đa ngôn ngữ, sâu)"])
    ok = st.form_submit_button("Phân tích", type="primary")

if ok and url.strip():
    vid = yt.parse_video_id(url)
    with st.spinner(f"Đang lấy {n} comment..."):
        try:
            cmts = comments.fetch_comments(vid, limit=n, sort=sort)
        except Exception as e:
            st.error(f"Lỗi: {e}")
            st.stop()
    if not cmts:
        st.warning("Không có comment.")
        st.stop()

    df = pd.DataFrame(cmts)[["author", "text", "votes", "time", "heart"]]

    if engine.startswith("VADER"):
        an = SentimentIntensityAnalyzer()
        scores = df["text"].apply(an.polarity_scores)
        df["compound"] = [s["compound"] for s in scores]
        df["sentiment"] = pd.cut(
            df["compound"], bins=[-1.01, -0.05, 0.05, 1.01], labels=["negative", "neutral", "positive"]
        )
    else:
        sys = (
            "Phân loại sentiment từng comment thành positive/neutral/negative. "
            "Trả JSON: {\"results\":[{\"index\":int,\"sentiment\":\"positive|neutral|negative\",\"reason\":str}]}."
        )
        batch = "\n".join(f"{i}. {t[:200]}" for i, t in enumerate(df["text"].tolist()))
        with st.spinner("DeepSeek đang phân tích..."):
            data = json.loads(llm.chat_json(f"Comments:\n{batch}", system=sys))
        labels = {r["index"]: r["sentiment"] for r in data.get("results", [])}
        df["sentiment"] = df.index.map(lambda i: labels.get(i, "neutral"))

    counts = df["sentiment"].value_counts().reset_index()
    counts.columns = ["sentiment", "count"]
    fig = px.pie(counts, names="sentiment", values="count", title="Phân bố sentiment")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top comment")
    st.dataframe(df.sort_values("votes", ascending=False, key=lambda s: s.astype(str)).head(50), hide_index=True, use_container_width=True)

    if st.button("📋 Tóm tắt audience qua DeepSeek"):
        sample = "\n".join(df["text"].head(80).tolist())
        sys = "Tóm tắt insight về audience: chủ đề chính, khen, chê, đề xuất cải thiện. Trả markdown ngắn gọn."
        with st.spinner("..."):
            st.markdown(llm.chat(sample, system=sys, temperature=0.4))

    st.download_button(
        "⬇️ Tải CSV", df.to_csv(index=False).encode("utf-8"), file_name=f"comments_{vid}.csv"
    )
