import streamlit as st
import importlib.util
import os
from PIL import Image

# --- 1. 경로 설정 및 페이지 로딩 함수 (기존과 동일) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_and_run_page(file_name):
    """지정된 파이썬 파일을 불러와서 그 안의 run() 함수를 실행하는 함수"""
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

# --- 2. 페이지 기본 설정 및 CSS 수정 ---
st.set_page_config(page_title="GnuDaS_GPT_World", layout="wide")

# 버튼 및 Expander 스타일을 위한 CSS 수정
st.markdown(
    """
    <style>
    div[data-testid="stSidebarUserContent"] {
        padding: 1rem;
    }

    /* --- 상위 메뉴 버튼 스타일 --- */
    div[data-testid="stSidebarUserContent"] > div > div > div[data-testid="stButton"] > button {
        display: block;
        width: 100%;
        text-align: left !important; /* 좌측 정렬 강제 */
        margin-bottom: 0.75rem;
        padding: 0.75rem 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        background-color: #ffffff;
        color: #31333F;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    div[data-testid="stSidebarUserContent"] > div > div > div[data-testid="stButton"] > button:hover {
        background-color: #0068c9;
        color: white;
        border-color: #005fb3;
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0, 104, 201, 0.2);
    }
    
    /* --- '수도시설과' Expander 제목 스타일 --- */
    div[data-testid="stExpander"] summary {
        font-size: 1rem;
        font-weight: 600;
        background-color: #0068c9;
        color: white;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 0rem; /* expander와 하위 버튼 간격 제거 */
        transition: all 0.2s ease-in-out;
    }
    div[data-testid="stExpander"] summary:hover {
        background-color: #005fb3;
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0, 104, 201, 0.2);
    }

    /* --- [수정됨] Expander 내용물(펼쳐지는 부분)의 배경과 테두리 제거 --- */
    div[data-testid="stExpander"] div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    /* 내용물과의 불필요한 간격 제거 */
    div[data-testid="stExpander"] div[data-testid="stVerticalBlock"] {
        padding: 0 !important;
        margin-top: 0.5rem; /* 제목과 하위 메뉴 사이 간격 */
    }


    /* --- 하위 메뉴 버튼 스타일 ('수도시설과' 내부) --- */
    div[data-testid="stExpander"] div[data-testid="stButton"] > button {
        display: block;
        width: 100%;
        text-align: left !important; /* 좌측 정렬 강제 */
        margin: 0 0 0.5rem 0.5rem; /* 왼쪽에 살짝 여백을 주어 계층 표현 */
        padding: 0.5rem 1rem;
        border: none; 
        border-radius: 6px;
        background-color: #f0f2f6; 
        color: #555;
        font-weight: 500;
        transition: all 0.2s ease-in-out;
    }
    div[data-testid="stExpander"] div[data-testid="stButton"] > button:hover {
        background-color: #e2e6eb;
        color: #0068c9;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 3. 사이드바 메뉴 구성 (기존과 동일) ---
st.sidebar.title("메뉴")

if 'page' not in st.session_state:
    st.session_state.page = '홈'

def set_page(page_name):
    st.session_state.page = page_name

st.sidebar.button("🏠 홈", on_click=set_page, args=('홈',), use_container_width=True)

with st.sidebar.expander("💧 수도시설과", expanded=(st.session_state.page in ["급수공사 공문 자동화", "정수기 신고"])):
    st.button("└ 급수공사 공문 자동화", on_click=set_page, args=('급수공사 공문 자동화',), use_container_width=True)
    st.button("└ 정수기 신고", on_click=set_page, args=('정수기 신고',), use_container_width=True)

st.sidebar.button("📄 PDF 일괄 변환", on_click=set_page, args=('PDF 일괄 변환',), use_container_width=True)
st.sidebar.button("📋 도급위탁용역 점검표 생성", on_click=set_page, args=('도급위탁용역 점검표 생성',), use_container_width=True)


# --- 4. 페이지 라우팅 및 실행 (기존과 동일) ---
page_to_run_map = {
    '홈': None, 
    '급수공사 공문 자동화': 'page1.py',
    '정수기 신고': 'page2.py',
    'PDF 일괄 변환': 'page3.py',
    '도급위탁용역 점검표 생성': 'page4.py'
}

page_file = page_to_run_map.get(st.session_state.page)

if page_file:
    load_and_run_page(page_file)
else:
    st.title("GnuDaS Ai World")
    st.write("사진우의 Ai 연구실")
    
    image_path = os.path.join(BASE_DIR, "서식", "mainpage", "image", "main_banner.jpg")
    if os.path.exists(image_path):
        st.image(Image.open(image_path), use_container_width=True)
    else:
        st.error(f"메인 배너 이미지를 찾을 수 없습니다: {image_path}")