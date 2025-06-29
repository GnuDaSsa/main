import streamlit as st
import importlib.util
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_and_run_page(file_name):
    file_path = os.path.join(BASE_DIR, file_name)
    try:
        module_name = os.path.splitext(file_name)[0]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            st.error(f"'{file_name}'에 대한 모듈 스펙을 찾을 수 없습니다.")
            return
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "run"):
            module.run()
        else:
            st.error(f"'{file_name}'에 'run()' 함수가 정의되어 있지 않습니다.")
    except FileNotFoundError:
        st.error(f"페이지 파일을 찾을 수 없습니다: {file_path}")
    except Exception as e:
        st.error(f"'{file_name}' 모듈을 불러오는 중 오류 발생: {e}")

st.set_page_config(page_title="GnuDaS_GPT_World", layout="wide")

st.markdown(
    """
    <style>
    /* 전체 배경과 글자색: 라이트/다크 모두에서 가시성 확보 */
    body, .stApp {
        background: #f4f6fb !important;
        color: #222222 !important;
    }
    @media (prefers-color-scheme: dark) {
        body, .stApp {
            background: #23272f !important;
            color: #f4f6fb !important;
        }
        .main-card {
            background: #2d3140 !important;
            border: 2.5px solid #444 !important;
        }
        input[type="text"] {
            background-color: #23272f !important;
            border: 2px solid #7a5cff !important;
            color: #f4f6fb !important;
        }
        input[type="text"]::placeholder {
            color: #bbaaff !important;
        }
        section[data-testid="stFileUploaderDropzone"] {
            background-color: #23272f !important;
            border: 2px dashed #7a5cff !important;
        }
        section[data-testid="stFileUploaderDropzone"]:hover {
            border-color: #4b2cff !important;
            background-color: #2d3140 !important;
        }
    }
    .main-card-row {
        display: flex;
        flex-direction: row;
        justify-content: flex-start;
        align-items: stretch;
        margin-top: 3.5rem;
        margin-bottom: 2.5rem;
        margin-left: 6vw;
        margin-right: 0;
        min-height: 700px;
        position: relative;
        z-index: 1;
    }
    .main-card {
        flex: 0 0 auto;
        max-width: 750px;
        min-width: 470px;
        background: #fff !important;
        border-radius: 22px;
        border: 2.5px solid #e0e0e0 !important;
        box-shadow: 0 8px 36px 0 #00000022, 0 2px 12px #00000033;
        padding: 2.7rem 2.7rem 2.2rem 2.7rem;
        margin: 0 0.5vw;
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
        z-index: 2;
    }
    input[type="text"] {
        background-color: #fff !important;
        border: 2px solid #7a5cff !important;
        color: #222 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        padding: 0.5em 0.8em !important;
        box-shadow: 0 2px 8px #00000033 !important;
    }
    input[type="text"]::placeholder {
        color: #7a5cff !important;
        opacity: 1 !important;
        font-weight: bold !important;
    }
    section[data-testid="stFileUploaderDropzone"] {
        background-color: #fff !important;
        border: 2px dashed #7a5cff !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 8px #00000033 !important;
    }
    section[data-testid="stFileUploaderDropzone"]:hover {
        border-color: #4b2cff !important;
        background-color: #f4f6fb !important;
    }
    .main-divider {
        width: 80px;
        height: 10px;
        background: linear-gradient(90deg, #9D5CFF 10%, #5CFFD1 90%);
        border-radius: 5px;
        margin: 1.5rem auto 1.5rem auto;
        opacity: 0.85;
        background-size: 200% 100%;
        background-position: 0% 0%;
        animation: gradient-move 3s ease-in-out infinite alternate;
        box-shadow: 0 2px 12px #bbaaff44;
    }
    @keyframes gradient-move {
        0% { background-position: 0% 0%; }
        100% { background-position: 100% 0%; }
    }
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    @keyframes orbit {
        0% { transform: translate(15px, -10px) scale(0.95); }
        50% { transform: translate(-10px, 15px) scale(1.05); }
        100% { transform: translate(15px, -10px) scale(0.95); }
    }
    .orbital-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 220px;
        height: 220px;
        position: relative;
        margin: 2.2rem auto 1.5rem auto;
        animation: spin 25s linear infinite;
        filter: drop-shadow(0 6px 24px #00000055);
    }
    .orbital-shape {
        position: absolute;
        border-radius: 50%;
        filter: blur(10px);
        opacity: 0.7;
    }
    .shape1 {
        width: 130px;
        height: 130px;
        background: radial-gradient(circle, #D0A2F7, #9D5CFF);
        animation: orbit 12s ease-in-out infinite;
    }
    .shape2 {
        width: 110px;
        height: 110px;
        background: radial-gradient(circle, #A2D2FF, #5C9DFF);
        animation: orbit 10s ease-in-out infinite reverse;
    }
    .shape3 {
        width: 90px;
        height: 90px;
        background: radial-gradient(circle, #A2FFE4, #5CFFD1);
        animation: orbit 8s ease-in-out infinite;
    }
    .main-title {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
        margin-top: 0.2rem;
        letter-spacing: -1px;
        background: linear-gradient(90deg, #9D5CFF 10%, #5CFFD1 90%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .main-sub {
        text-align: center;
        font-size: 1.25rem;
        color: #7a5cff;
        font-weight: 600;
        margin-bottom: 0.2rem;
        letter-spacing: 0.5px;
        text-shadow: 0 2px 8px #e6e6ff55;
    }
    .main-lab {
        text-align: center;
        font-size: 1.08rem;
        color: #555;
        font-weight: 500;
        margin-bottom: 1.2rem;
        letter-spacing: 0.2px;
    }
    .main-desc {
        text-align: center;
        font-size: 1.08rem;
        color: #666;
        margin-bottom: 0.7rem;
        font-weight: 400;
    }
    .main-quote {
        text-align: center;
        font-size: 1.05rem;
        color: #888;
        font-style: italic;
        margin-bottom: 2.2rem;
        letter-spacing: 0.2px;
        text-shadow: 0 1px 6px #00000033;
    }
    .sidebar-section-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #7a5cff;
        margin-bottom: 0.7em;
        margin-top: 0.2em;
        letter-spacing: 1px;
        text-align: left;
    }
    .sidebar-divider {
        border-top: 1px solid #e0e0e0;
        margin: 1.2em 0 0.8em 0;
    }
    div[data-testid="stSidebarUserContent"] { padding: 1rem; }
    </style>
    """,
    unsafe_allow_html=True
)

# 페이지 상태 관리
if 'page' not in st.session_state:
    st.session_state.page = '홈'

with st.sidebar:
    st.markdown('<div class="sidebar-section-title">common</div>', unsafe_allow_html=True)
    if st.button("🏠 홈", use_container_width=True):
        st.session_state.page = '홈'
    if st.button("🧑‍🤝‍🧑 MBTI 검사기", use_container_width=True):
        st.session_state.page = 'MBTI 검사기'
    if st.button("🎭 테토에겐 테스트", use_container_width=True):
        st.session_state.page = '테토에겐 테스트'
    if st.button("📄 한글 ➡️ PDF 일괄변환", use_container_width=True):
        st.session_state.page = 'PDF 일괄 변환'
    if st.button("📋 도급위탁용역 점검표 생성", use_container_width=True):
        st.session_state.page = '도급위탁용역 점검표 생성'
    if st.button("📰 생성형 AI 보도자료 생성기", use_container_width=True):
        st.session_state.page = '생성형 AI 보도자료 생성기'
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">custom</div>', unsafe_allow_html=True)
    with st.expander("💧 수도시설과", expanded=(st.session_state.get('page') in ["급수공사 공문 자동화", "정수기 신고"])):
        if st.button("└ 급수공사 공문 자동화", use_container_width=True):
            st.session_state.page = '급수공사 공문 자동화'
        if st.button("└ 정수기 신고", use_container_width=True):
            st.session_state.page = '정수기 신고'

page_to_run_map = {
    '홈': None,
    'MBTI 검사기': 'page6.py',
    '테토에겐 테스트': 'page7.py',
    '급수공사 공문 자동화': 'page1.py',
    '정수기 신고': 'page2.py',
    'PDF 일괄 변환': 'page3.py',
    '도급위탁용역 점검표 생성': 'page4.py',
    '생성형 AI 보도자료 생성기': 'page5.py',
}
page_file = page_to_run_map.get(st.session_state.page)

if page_file:
    load_and_run_page(page_file)
else:
    st.markdown("""
        <div class="main-card-row">
            <div class="main-card">
                <div class="orbital-container">
                    <div class="orbital-shape shape1"></div>
                    <div class="orbital-shape shape2"></div>
                    <div class="orbital-shape shape3"></div>
                </div>
                <div class="main-title">성남시 AIpha매일</div>
                <div class="main-sub">(AI를 매일 파는 사람들)</div>
                <div class="main-lab">지누다스(GnuDaS)의 AI연구실</div>
                <div class="main-divider"></div>
                <div class="main-desc">
                    반복 업무 자동화와 AI 도구를 제공합니다.<br>
                    좌측 메뉴에서 원하는 기능을 선택하세요.
                </div>
                <div class="main-quote">
                    Empowering your daily work with smart automation.<br>
                    <span style="font-size:0.98rem;">Innovation starts here, with GnuDaS AI Lab.</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

