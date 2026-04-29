"""Trends Generator — pytrends gprop='youtube'."""
from __future__ import annotations

import plotly.express as px
import streamlit as st

from core import trends

st.set_page_config(page_title="Trends Generator", page_icon="📈", layout="wide")
from core.theme import inject; inject()
st.title("📈 Trends Generator")
st.caption("Xu hướng tìm kiếm trên YouTube qua Google Trends (pytrends).")

tabs = st.tabs(["So sánh keyword", "Related queries", "Trending searches"])

with tabs[0]:
    with st.form("compare"):
        kws = st.text_input(
            "Keyword (cách nhau bằng dấu phẩy, tối đa 5)",
            placeholder="iphone 16, samsung s24, pixel 9",
        )
        c1, c2 = st.columns(2)
        with c1:
            geo = st.selectbox("Quốc gia", ["VN", "US", "GB", "JP", "KR", ""], index=0, format_func=lambda x: x or "Toàn cầu")
        with c2:
            tf = st.selectbox(
                "Khoảng thời gian",
                ["now 7-d", "today 1-m", "today 3-m", "today 12-m", "today 5-y"],
                index=2,
            )
        ok = st.form_submit_button("So sánh", type="primary")
    if ok and kws.strip():
        keywords = [k.strip() for k in kws.split(",") if k.strip()][:5]
        with st.spinner("Đang lấy dữ liệu trends..."):
            df = trends.interest_over_time(keywords, geo=geo, timeframe=tf)
        if df.empty:
            st.warning("Không có dữ liệu cho keyword/khoảng thời gian này.")
        else:
            fig = px.line(df.reset_index(), x="date", y=keywords, title="Interest over time (YouTube)")
            st.plotly_chart(fig, width='stretch')
            st.dataframe(df, width='stretch')

with tabs[1]:
    with st.form("rq"):
        kw = st.text_input("Keyword đơn", placeholder="vd: review điện thoại")
        c1, c2 = st.columns(2)
        with c1:
            geo2 = st.selectbox("Quốc gia ", ["VN", "US", "GB", ""], index=0, key="rq_geo")
        with c2:
            tf2 = st.selectbox("Khoảng thời gian ", ["today 1-m", "today 3-m", "today 12-m"], index=1, key="rq_tf")
        ok2 = st.form_submit_button("Lấy related", type="primary")
    if ok2 and kw.strip():
        with st.spinner("Đang lấy related queries..."):
            data = trends.related_queries(kw.strip(), geo=geo2, timeframe=tf2)
        col_top, col_rising = st.columns(2)
        with col_top:
            st.subheader("Top")
            top = data.get("top")
            if top is not None and not top.empty:
                st.dataframe(top, hide_index=True, width='stretch')
            else:
                st.info("Không có dữ liệu.")
        with col_rising:
            st.subheader("Rising 🚀")
            rising = data.get("rising")
            if rising is not None and not rising.empty:
                st.dataframe(rising, hide_index=True, width='stretch')
            else:
                st.info("Không có dữ liệu.")

with tabs[2]:
    pn = st.selectbox("Quốc gia", ["vietnam", "united_states", "japan", "south_korea", "united_kingdom"], index=0)
    if st.button("Lấy trending searches"):
        with st.spinner("..."):
            df = trends.trending_searches(pn=pn)
        st.dataframe(df, width='stretch')
