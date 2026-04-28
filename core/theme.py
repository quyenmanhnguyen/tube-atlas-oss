"""Tube Atlas v3.2 — Polished Studio theme (Light + Dark).

Inspired by modern dashboard UI (cream/peach light + clean dark). Uses CSS
custom properties so the same rules work for both modes — just swap the
:root variable block.
"""
from __future__ import annotations

import streamlit as st

# ─── Color tokens ───────────────────────────────────────────────────────────
LIGHT_VARS = """
:root, .stApp {
    --bg-app: #FFF8F0;
    --bg-card: #FFFFFF;
    --bg-sidebar: #FFFFFF;
    --bg-soft: #FEF1E3;
    --bg-elevated: #FFFFFF;
    --text-primary: #1A1F2E;
    --text-secondary: #4A5568;
    --text-muted: #6B7280;
    --accent: #FFB088;
    --accent-strong: #F09060;
    --accent-soft: #FFE5D2;
    --pill-green: #A8E6A1;
    --pill-green-soft: #DDF5DA;
    --pill-green-text: #2D6B27;
    --border: rgba(26,31,46,0.06);
    --border-strong: rgba(26,31,46,0.12);
    --shadow-sm: 0 1px 3px rgba(26,31,46,0.04), 0 1px 2px rgba(26,31,46,0.06);
    --shadow-md: 0 4px 16px rgba(26,31,46,0.04), 0 2px 6px rgba(26,31,46,0.05);
    --shadow-lg: 0 12px 32px rgba(26,31,46,0.06), 0 4px 12px rgba(26,31,46,0.04);
    --radius-sm: 12px;
    --radius-md: 16px;
    --radius-lg: 20px;
    color-scheme: light;
}
"""

DARK_VARS = """
:root, .stApp {
    --bg-app: #0F1218;
    --bg-card: #181C26;
    --bg-sidebar: #13171F;
    --bg-soft: #1F2430;
    --bg-elevated: #1E222D;
    --text-primary: #F5F5F5;
    --text-secondary: #C4CCDA;
    --text-muted: #9CA3AF;
    --accent: #FFB088;
    --accent-strong: #FFC9A8;
    --accent-soft: rgba(255,176,136,0.15);
    --pill-green: #A8E6A1;
    --pill-green-soft: rgba(168,230,161,0.18);
    --pill-green-text: #A8E6A1;
    --border: rgba(255,255,255,0.06);
    --border-strong: rgba(255,255,255,0.10);
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.2);
    --shadow-md: 0 4px 16px rgba(0,0,0,0.25);
    --shadow-lg: 0 12px 32px rgba(0,0,0,0.30);
    --radius-sm: 12px;
    --radius-md: 16px;
    --radius-lg: 20px;
    color-scheme: dark;
}
"""

BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

.stApp { background: var(--bg-app) !important; color: var(--text-primary); }
.block-container { padding-top: 2rem !important; padding-bottom: 3rem !important; max-width: 1280px !important; }
[data-testid="stHeader"] { background: var(--bg-app) !important; }
[data-testid="stToolbar"] { background: transparent !important; }

/* ─── Sidebar ───────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] [data-testid="stSidebarNav"] { padding: 8px 12px; }
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {
    border-radius: 12px;
    margin: 3px 0;
    padding: 10px 14px !important;
    transition: background 0.15s ease, color 0.15s ease;
    color: var(--text-secondary) !important;
    font-weight: 500;
}
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover {
    background: var(--bg-soft) !important;
    color: var(--text-primary) !important;
}
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-current="page"] {
    background: var(--pill-green) !important;
    color: #1A1F2E !important;
    font-weight: 600;
}
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] span,
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"] div {
    color: inherit !important;
}
[data-testid="stSidebarNav"] [role="presentation"],
[data-testid="stSidebar"] [data-testid="stSidebarNavSeparator"] + div {
    color: var(--text-muted) !important;
    font-weight: 600 !important;
    font-size: 0.7rem !important;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    padding: 14px 14px 6px !important;
}

/* ─── Headings ─────────────────────────────────────────────────────────── */
h1, h2, h3, h4, h5 { color: var(--text-primary) !important; font-weight: 700 !important; }
h1 { font-size: 2rem !important; letter-spacing: -0.02em; }
h2 { font-size: 1.4rem !important; }
h3 { font-size: 1.15rem !important; }
/* Soft default text for body content (don't override widget-internal nodes) */
.stApp > div p,
.stApp > div > div > div > div > p {
    color: var(--text-secondary);
}

/* Make sure button + tab labels inherit their host color (not soft default) */
.stButton > button *, .stDownloadButton > button * { color: inherit !important; }
.stTabs [data-baseweb="tab"] * { color: inherit !important; }
[data-testid="stMetricValue"] *, [data-testid="stMetricLabel"] * { color: inherit !important; }

/* ─── Cards (generic) ──────────────────────────────────────────────────── */
.ta-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    padding: 22px 24px;
}

/* ─── Metric cards ─────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 18px 22px;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.2s ease, transform 0.2s ease;
}
[data-testid="stMetric"]:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
}
[data-testid="stMetricValue"] {
    font-size: 1.7rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    font-weight: 600;
}

/* ─── Buttons ──────────────────────────────────────────────────────────── */
.stButton > button {
    background: var(--accent) !important;
    color: #1A1F2E !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
    box-shadow: var(--shadow-sm) !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease !important;
}
.stButton > button:hover {
    filter: brightness(0.97);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md) !important;
}
.stDownloadButton > button {
    background: var(--pill-green) !important;
    color: #1A1F2E !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}

/* ─── Forms / inputs ───────────────────────────────────────────────────── */
[data-testid="stForm"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 24px;
    box-shadow: var(--shadow-sm);
}
input, textarea, select {
    border-radius: 12px !important;
    border: 1px solid var(--border-strong) !important;
    background: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
    transition: border 0.15s ease, box-shadow 0.15s ease;
}
input::placeholder, textarea::placeholder { color: var(--text-muted) !important; opacity: 0.8; }
input:focus, textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-soft) !important;
    outline: none !important;
}
[data-baseweb="select"] > div, [data-baseweb="input"] > div {
    border-radius: 12px !important;
    border: 1px solid var(--border-strong) !important;
    background: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
}
/* Force text color inside baseweb composite widgets (selectbox, multiselect,
   date input). Without this, inner text inherits baseweb light defaults and
   becomes unreadable in dark mode. */
[data-baseweb="select"] *,
[data-baseweb="input"] *,
[data-baseweb="popover"] *,
[data-baseweb="menu"] * {
    color: var(--text-primary) !important;
}
[data-baseweb="popover"] [role="option"],
[data-baseweb="menu"] [role="option"] {
    background: var(--bg-card) !important;
}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="menu"] [role="option"]:hover {
    background: var(--bg-soft) !important;
}

/* Make sure Streamlit form submit buttons keep peach bg + dark text */
[data-testid="stFormSubmitButton"] > button,
[data-testid="stFormSubmitButton"] > button * {
    color: #1A1F2E !important;
}
.stButton > button p, .stButton > button span, .stButton > button div {
    color: #1A1F2E !important;
}

/* ─── Tabs ─────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: var(--bg-soft);
    border-radius: 12px;
    padding: 5px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 600;
    color: var(--text-muted);
    transition: all 0.15s ease;
    padding: 8px 16px !important;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--text-primary); }
.stTabs [aria-selected="true"] {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    box-shadow: var(--shadow-sm);
}

/* ─── Tables / expanders / alerts ──────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: var(--radius-md);
    overflow: hidden;
    border: 1px solid var(--border);
}
[data-testid="stExpander"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-sm);
}
[data-testid="stAlert"] {
    border-radius: var(--radius-md);
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    color: var(--text-primary);
    box-shadow: var(--shadow-sm);
}
[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: var(--border) !important;
    border-radius: var(--radius-md) !important;
}

/* ─── Scrollbar ────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-strong); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ─── Custom: Hero greeting (Home) ─────────────────────────────────────── */
.greeting-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 26px 28px;
    box-shadow: var(--shadow-md);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    flex-wrap: wrap;
    margin-bottom: 20px;
}
.greeting-text h1 {
    font-size: 1.6rem !important;
    margin: 0 !important;
    color: var(--text-primary) !important;
}
.greeting-text p {
    margin: 4px 0 0 0;
    color: var(--text-muted);
    font-size: 0.9rem;
}
.greeting-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 14px;
    background: var(--accent-soft);
    color: var(--accent-strong);
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.4px;
}

/* ─── Custom: Step row (3-step workflow) ───────────────────────────────── */
.step-row {
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
    margin: 8px 0 16px;
}
.step-card {
    flex: 1;
    min-width: 220px;
    padding: 22px 22px 20px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
    position: relative;
    overflow: hidden;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.step-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}
.step-card .step-icon-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 44px; height: 44px;
    border-radius: 12px;
    background: var(--accent-soft);
    font-size: 1.4rem;
    margin-bottom: 12px;
}
.step-card .step-num {
    color: var(--text-muted);
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}
.step-card .step-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 4px 0 6px;
}
.step-card .step-desc {
    color: var(--text-muted);
    font-size: 0.85rem;
    line-height: 1.5;
}

/* ─── Custom: Tool cards (2x2 grid) ────────────────────────────────────── */
.tool-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 18px 20px;
    min-height: 130px;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.2s ease, transform 0.2s ease;
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.tool-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
}
.tool-card .tool-name {
    font-weight: 700;
    color: var(--text-primary);
    font-size: 1rem;
}
.tool-card .tool-desc {
    color: var(--text-muted);
    font-size: 0.85rem;
    line-height: 1.5;
    flex: 1;
}
.tool-card .tool-status {
    display: inline-block;
    margin-top: 6px;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.4px;
    text-transform: uppercase;
    align-self: flex-start;
}
.tool-card .tool-status.ok {
    background: var(--pill-green-soft);
    color: var(--pill-green-text);
    border: 1px solid var(--pill-green);
}
.tool-card .tool-status.warn {
    background: var(--accent-soft);
    color: var(--accent-strong);
    border: 1px solid var(--accent);
}
/* ─── Toggle button styling for theme switch ───────────────────────────── */
[data-testid="stSidebar"] [data-testid="stToggle"] {
    padding: 8px 12px;
    background: var(--bg-soft);
    border-radius: 12px;
    border: 1px solid var(--border);
    margin: 4px 6px 12px;
}
"""


def _inject(theme: str) -> None:
    vars_block = DARK_VARS if theme == "dark" else LIGHT_VARS
    st.markdown(
        f"<style>{vars_block}\n{BASE_CSS}</style>",
        unsafe_allow_html=True,
    )
    # Hint to UA for built-in form controls / scrollbars.
    st.markdown(
        f"<div style='display:none' data-theme='{theme}'></div>",
        unsafe_allow_html=True,
    )


def apply() -> str:
    """Render theme toggle in sidebar + inject CSS. Returns active theme name.

    Persists across reruns via st.session_state['theme']. Default = light.
    """
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"

    with st.sidebar:
        is_dark = st.toggle(
            "🌙 Dark mode",
            value=(st.session_state["theme"] == "dark"),
            key="theme_toggle",
            help="Bật/tắt chế độ tối",
        )
    new_theme = "dark" if is_dark else "light"
    if new_theme != st.session_state["theme"]:
        st.session_state["theme"] = new_theme
    _inject(st.session_state["theme"])
    return st.session_state["theme"]


# Backwards-compat: existing pages call inject().
def inject() -> None:
    """Compat shim — call apply() in app.py once; this is a no-op for pages.

    Pages still call inject() at the top, so we re-inject the CSS for the
    currently selected theme (cheap, idempotent) without rendering the toggle.
    """
    theme = st.session_state.get("theme", "light")
    _inject(theme)
