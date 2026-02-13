import base64
import importlib.util
import os
import textwrap

import streamlit as st

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_and_run_page(file_name: str) -> None:
    file_path = os.path.join(BASE_DIR, file_name)
    try:
        module_name = os.path.splitext(file_name)[0]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            st.error(f"'{file_name}' module spec not found.")
            return
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "run"):
            module.run()
        else:
            st.error(f"'{file_name}' does not define run().")
    except FileNotFoundError:
        st.error(f"Page file not found: {file_path}")
    except Exception as e:
        st.error(f"Error loading '{file_name}': {e}")


def image_to_data_uri(image_path: str) -> str | None:
    if not os.path.exists(image_path):
        return None
    ext = os.path.splitext(image_path)[1].lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


st.set_page_config(page_title="GnuDaS_GPT_World", layout="wide")
background_image_path = os.path.join(BASE_DIR, "..", "monitor_image.png")
if not os.path.exists(background_image_path):
    background_image_path = os.path.join(BASE_DIR, "assets", "flash_banner.png")
flash_data_uri = image_to_data_uri(background_image_path)

st.markdown(
    textwrap.dedent(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700;800&family=Noto+Sans+KR:wght@500;700;800&display=swap');
:root { --text-main:#eef4ff; --text-sub:#d5def3; --panel:rgba(8,10,34,0.42); --panel-border:rgba(125,187,255,0.42); }
.stApp {
  color: var(--text-main);
  background: transparent;
}
.stApp, .stApp button, .stApp input, .stApp textarea {
  font-family: "Space Grotesk", "Noto Sans KR", sans-serif !important;
}
.global-flash-overlay {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}
.global-flash-overlay::before {
  content: "";
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 22% 20%, rgba(117, 232, 255, 0.22), transparent 38%),
    radial-gradient(circle at 80% 14%, rgba(255, 119, 230, 0.2), transparent 34%),
    linear-gradient(180deg, rgba(12, 18, 62, 0.78), rgba(7, 8, 22, 0.90));
  z-index: 2;
}
.global-flash-overlay img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 1.00;
  transform: scale(1);
  filter: saturate(1.22) contrast(1.05) brightness(1.5);
}
section[data-testid="stSidebar"],
div[data-testid="stAppViewContainer"] > .main,
div[data-testid="stAppViewContainer"] > .main > div {
  position: relative;
  z-index: 2;
}
section[data-testid="stSidebar"] button {
  font-size: calc(0.92rem + 2pt) !important;
  font-weight: 700 !important;
}
.sidebar-section-title { font-size:calc(1.02rem + 2pt); font-weight:700; color:#8db9ff; margin-bottom:.7em; margin-top:.2em; letter-spacing:1px; text-align:left; }
.sidebar-divider { border-top:1px solid #2d3e67; margin:1.2em 0 .8em 0; }
div[data-testid="stSidebarUserContent"] { padding:1rem; }

.landing-shell { max-width:1260px; margin:2rem auto 1rem auto; padding:0 1rem; }
.top-banner {
  position: relative;
  width: 100%;
  min-height: 160px;
  border-radius: 20px;
  border: 1px solid rgba(133, 209, 255, .56);
  background: linear-gradient(90deg, rgba(9, 25, 82, .92), rgba(55, 21, 105, .94));
  box-shadow: 0 16px 46px rgba(0,0,0,.38), inset 0 0 0 1px rgba(255,255,255,.08);
  padding: 1rem 1.2rem;
  margin-bottom: 1rem;
  overflow: hidden;
}
.top-banner-image {
  display: none;
}
.top-banner-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, rgba(7,12,34,.68), rgba(19,12,52,.62));
}
.top-banner-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  gap: .36rem;
}
.top-banner-label {
  color: #7bd6ff;
  font-size: calc(.84rem + 2pt);
  font-weight: 700;
  letter-spacing: .18em;
  text-transform: uppercase;
}
.top-banner-date {
  color: #bfd8ff;
  font-size: calc(.74rem + 2pt);
  font-weight: 700;
  letter-spacing: .06em;
}
.top-banner-name {
  margin-top: .04rem;
  color: #f8fbff;
  font-size: clamp(1.55rem, 2.9vw, 2.55rem);
  font-weight: 900;
  letter-spacing: .02em;
  text-shadow: 0 0 16px rgba(103,229,255,.38), 0 0 34px rgba(180,123,255,.32);
}
.top-banner-sub {
  margin-top: .1rem;
  color: #d6e8ff;
  font-size: calc(.95rem + 2pt);
  font-weight: 700;
  letter-spacing: .03em;
}
.top-banner-meta {
  margin-top: .2rem;
  display: flex;
  gap: .6rem;
  flex-wrap: wrap;
}
.meta-badge {
  display: inline-flex;
  align-items: center;
  padding: .34rem .74rem;
  border-radius: 999px;
  border: 1px solid rgba(130, 207, 255, .58);
  background: rgba(8, 20, 50, .64);
  color: #f2f8ff;
  font-size: calc(.84rem + 2pt);
  font-weight: 800;
}
.top-banner-trace {
  margin-top: .28rem;
  height: 2px;
  width: min(580px, 95%);
  background: linear-gradient(90deg, rgba(122, 223, 255, .95), rgba(194, 118, 255, .78));
  box-shadow: 0 0 18px rgba(122, 223, 255, .52);
  border-radius: 2px;
}
.landing-grid { display:block; }
.info-panel { border-radius:24px; border:1px solid var(--panel-border); background:var(--panel); box-shadow:0 18px 64px rgba(0,0,0,.45), inset 0 0 0 1px rgba(255,255,255,.04); overflow:hidden; min-height:auto; padding:1.45rem 1.5rem 1.2rem; display:flex; flex-direction:column; gap:.8rem; }
.hub-grid { display:grid; grid-template-columns:repeat(2, minmax(0, 1fr)); gap:.85rem; margin-top:.15rem; }
.info-title { margin:0; font-size:calc(1.3rem + 2pt); font-weight:900; color:#f3f7ff; }
.info-desc { margin:0; color:var(--text-sub); line-height:1.6; font-size:calc(1.05rem + 2pt); }
.chip-wrap { display:flex; flex-wrap:wrap; gap:.45rem; }
.chip {
  padding:.5rem .85rem; border-radius:999px; border:1px solid rgba(150,197,255,.42);
  background:rgba(12,26,62,.56); color:#e6efff; font-size:calc(.94rem + 2pt); font-weight:700; letter-spacing:.02em;
}
.activity-card {
  border-radius:14px; border:1px solid rgba(165,201,255,.33);
  background:linear-gradient(180deg, rgba(17,28,65,.48), rgba(11,18,45,.56)); padding:.86rem;
}
.activity-title {
  margin: 0 0 .55rem !important;
  color: #f7fbff !important;
  font-size: calc(1.25rem + 2pt) !important;
  font-weight: 800 !important;
  line-height: 1.3 !important;
}
.activity-line {
  margin: .34rem 0 !important;
  color: #c4d4f3 !important;
  font-size: calc(1.14rem + 2pt) !important;
  line-height: 1.52 !important;
  font-weight: 600 !important;
}
.cta-note {
  margin-top:.2rem; border-radius:12px; border:1px solid rgba(103,229,255,.4);
  background:linear-gradient(90deg, rgba(10,30,67,.58), rgba(27,20,74,.52));
  color:#dbedff; font-size:calc(.92rem + 2pt); font-weight:700; padding:.78rem .9rem;
}
@media (max-width:980px) {
  .hub-grid { grid-template-columns:1fr; }
  .top-banner { min-height: 180px; }
}
</style>
        """
    ),
    unsafe_allow_html=True,
)

HOME = "\ud648"
MBTI = "MBTI \uac80\uc0ac\uae30"
TETO = "\ud14c\ud1a0\uc5d0\uac90 \ud14c\uc2a4\ud2b8"
PDF = "PDF \uc77c\uad04 \ubcc0\ud658"
CHECK = "\ub3c4\uae09\uc704\ud0c1\uc6a9\uc5ed \uc810\uac80\ud45c \uc0dd\uc131"
PRESS = "\uc0dd\uc131\ud615 AI \ubcf4\ub3c4\uc790\ub8cc \uc0dd\uc131\uae30"
WATER_DOC = "\uae09\uc218\uacf5\uc0ac \uacf5\ubb38 \uc790\ub3d9\ud654"
WATER_REPORT = "\uc815\uc218\uae30 \uc2e0\uace0"

if "page" not in st.session_state:
    st.session_state.page = HOME

with st.sidebar:
    st.markdown('<div class="sidebar-section-title">common</div>', unsafe_allow_html=True)
    if st.button(HOME, use_container_width=True):
        st.session_state.page = HOME
    if st.button(MBTI, use_container_width=True):
        st.session_state.page = MBTI
    if st.button(TETO, use_container_width=True):
        st.session_state.page = TETO
    if st.button(PDF, use_container_width=True):
        st.session_state.page = PDF
    if st.button(CHECK, use_container_width=True):
        st.session_state.page = CHECK
    if st.button(PRESS, use_container_width=True):
        st.session_state.page = PRESS

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">custom</div>', unsafe_allow_html=True)
    with st.expander("\uc218\ub3c4\uc2dc\uc124\uacfc", expanded=(st.session_state.get("page") in [WATER_DOC, WATER_REPORT])):
        if st.button("\u2514 " + WATER_DOC, use_container_width=True):
            st.session_state.page = WATER_DOC
        if st.button("\u2514 " + WATER_REPORT, use_container_width=True):
            st.session_state.page = WATER_REPORT

if flash_data_uri:
    st.markdown(
        (
            '<div class="global-flash-overlay">'
            f'<img src="{flash_data_uri}" alt="flash overlay" />'
            "</div>"
        ),
        unsafe_allow_html=True,
    )

page_to_run_map = {
    HOME: None,
    MBTI: "page6.py",
    TETO: "page7.py",
    WATER_DOC: "page1.py",
    WATER_REPORT: "page2.py",
    PDF: "page3.py",
    CHECK: "page4.py",
    PRESS: "page5.py",
}

page_file = page_to_run_map.get(st.session_state.page)

if page_file:
    load_and_run_page(page_file)
else:
    if flash_data_uri:
        top_banner_html = (
            '<div class="top-banner">'
            '<div class="top-banner-overlay"></div>'
            '<div class="top-banner-content">'
            '<div class="top-banner-label">AI CLUB</div>'
            '<div class="top-banner-date">Updated 2026-02-13</div>'
            '<div class="top-banner-name">Deep Learning Crew</div>'
            '<div class="top-banner-meta">'
            '<span class="meta-badge">\ud68c\uc7a5 \uc0ac\uc9c4\uc6b0</span>'
            '<span class="meta-badge">\ucd1d\ubb34 \uae40\ub3d9\uc8fc</span>'
            "</div>"
            '<div class="top-banner-trace"></div>'
            "</div>"
            "</div>"
        )
    else:
        top_banner_html = (
            '<div class="top-banner">'
            '<div class="top-banner-content">'
            '<div class="top-banner-label">AI CLUB</div>'
            '<div class="top-banner-date">Updated 2026-02-13</div>'
            '<div class="top-banner-name">Deep Learning Crew</div>'
            '<div class="top-banner-meta">'
            '<span class="meta-badge">\ud68c\uc7a5 \uc0ac\uc9c4\uc6b0</span>'
            '<span class="meta-badge">\ucd1d\ubb34 \uae40\ub3d9\uc8fc</span>'
            "</div>"
            '<div class="top-banner-trace"></div>'
            "</div>"
            "</div>"
        )

    st.markdown(
        (
            '<div class="landing-shell">'
            f"{top_banner_html}"
            '<div class="landing-grid">'
            '<section class="info-panel">'
            '<h2 class="info-title">Main Hub</h2>'
            '<div class="chip-wrap">'
            '<span class="chip">AUTOMATION</span>'
            '<span class="chip">INNOVATION</span>'
            '<span class="chip">CODING</span>'
            '<span class="chip">CONTENT</span>'
            '<span class="chip">COMPETITION</span>'
            "</div>"
            '<div class="hub-grid">'
            '<div class="activity-card">'
            '<p class="activity-title">\ud65c\ub3d9\ub0b4\uc6a9 - Passive</p>'
            '<p class="activity-line">\uc790\ub8cc\uacf5\uc720</p>'
            '<p class="activity-line">\uc544\uc774\ub514\uc5b4 \uc81c\uc548 \ubc0f \uace0\ub3c4\ud654</p>'
            '<p class="activity-line">\uc5c5\ubb34\ud65c\uc6a9\uc0ac\ub840 \uc9c8\uc758\uc751\ub2f5</p>'
            '<p class="activity-line">\uce74\ud1a1\ubc29 \uc6b4\uc601</p>'
            "</div>"
            '<div class="activity-card">'
            '<p class="activity-title">\ud65c\ub3d9\ub0b4\uc6a9 - Active</p>'
            '<p class="activity-line">\ubc18\uae30 1\ud68c \uc624\ud504\ub77c\uc778 \ubaa8\uc784</p>'
            '<p class="activity-line">\uc544\uc774\ub514\uc5b4\ud68c\uc758</p>'
            "</div>"
            "</div>"
            '<div class="activity-card">'
            '<p class="activity-title">\uc774\ubc88 \ubd84\uae30 \ubaa9\ud45c</p>'
            '<p class="activity-line">\ub098\ub9cc\uc758 AI\ucee8\ud150\uce20 \ub9cc\ub4e4\uae30</p>'
            "</div>"
            '<div class="cta-note">\uc88c\uce21 \ud0ed\uc5d0\uc11c \uae30\ub2a5\uc744 \uc120\ud0dd\ud558\uc5ec \ud65c\uc6a9\ud558\uc138\uc694.</div>'
            "</section>"
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

