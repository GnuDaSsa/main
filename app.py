import streamlit as st
import importlib.util
import os
from PIL import Image

# 페이지 설정 (앱 전체에 적용)
# st.set_page_config는 앱에서 한 번만 호출되어야 합니다.
st.set_page_config(page_title="GnuDaS_GPT_World", layout="wide")

# 커스텀 CSS
st.markdown(
    """
    <style>
    label[data-baseweb="radio"] > div:first-child {
        display: none !important;
    }
    label[data-baseweb="radio"] {
        display: block;
        margin-bottom: 1rem;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        background: #fafafa;
        transition: background-color 0.3s, box-shadow 0.3s;
        cursor: pointer;
        width: 100% !important;
    }
    label[data-baseweb="radio"] [type="radio"]:checked + div {
        background: linear-gradient(to right, #ff7e5f, #feb47b);
        color: #ffffff;
        font-weight: bold;
        box-shadow: 0 0 5px rgba(0,0,0,0.2);
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.title("메뉴")
# 새로운 탭 "도급위탁용역 점검표 생성" 추가
choice = st.sidebar.radio("탭:", ["홈", "급수공사 공문 자동화", "정수기 신고", "PDF 변환", "도급위탁용역 점검표 생성"])

# 각 탭에 따라 다른 페이지 모듈을 동적으로 로드 및 실행
if choice == "홈":
    st.title("GnuDaS Ai World")
    st.write("사진우의 Ai 연구실")
    # 이미지 경로를 올바르게 설정해주세요.
    # Streamlit 앱이 실행되는 환경에 따라 절대 경로보다는 상대 경로를 사용하는 것이 좋습니다.
    # 예: image_path = "서식/mainpage/image/main_banner.jpg"
    image_path = r"C:\Users\Owner\Desktop\사진우\AI\gnudasAI\서식\mainpage\image\main_banner.jpg"
    if os.path.exists(image_path):
        image = Image.open(image_path)
        # use_column_width를 use_container_width로 변경합니다.
        st.image(image, use_container_width=True)
    else:
        st.error(f"메인 배너 이미지를 찾을 수 없습니다: {image_path}")

elif choice == "급수공사 공문 자동화":
    st.title("급수공사 공문 자동화")
    file_path = r"C:\Users\Owner\Desktop\사진우\AI\gnudasAI\page1.py"
    try:
        spec = importlib.util.spec_from_file_location("page1", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "run"):
            module.run()
        else:
            st.error(f"'{file_path}'에 'run()' 함수가 정의되어 있지 않습니다.")
    except Exception as e:
        st.error(f"'{file_path}' 모듈을 불러오는 중 오류 발생: {e}")

elif choice == "정수기 신고":
    st.title("정수기 신고")
    file_path = r"C:\Users\Owner\Desktop\사진우\AI\gnudasAI\page2.py"
    if not os.path.exists(file_path):
        st.error(f"파일을 찾을 수 없습니다: {file_path}")
    else:
        try:
            spec = importlib.util.spec_from_file_location("page2", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "run"):
                module.run()
            # else: st.error(f"'{file_path}'에 'run()' 함수가 정의되어 있지 않습니다.")
        except Exception as e:
            st.error(f"'{file_path}' 모듈을 불러오는 중 오류 발생: {e}")

elif choice == "PDF 일괄 변환":
    st.title("PDF 일괄 변환")
    file_path = r"C:\Users\Owner\Desktop\사진우\AI\gnudasAI\page3.py"
    if not os.path.exists(file_path):
        st.error(f"파일을 찾을 수 없습니다: {file_path}")
    else:
        try:
            spec = importlib.util.spec_from_file_location("page3", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "run"):
                module.run()
            # else: st.error(f"'{file_path}'에 'run()' 함수가 정의되어 있지 않습니다.")
        except Exception as e:
            st.error(f"'{file_path}' 모듈을 불러오는 중 오류 발생: {e}")

elif choice == "도급위탁용역 점검표 생성":
    st.title("도급위탁용역 점검표 생성")
    # page4.py 파일 경로 지정 (실제 파일 경로로 변경 필요)
    file_path = r"C:\Users\Owner\Desktop\사진우\AI\gnudasAI\page4.py"
    if not os.path.exists(file_path):
        st.error(f"파일을 찾을 수 없습니다: {file_path}")
    else:
        try:
            spec = importlib.util.spec_from_file_location("page4", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "run"):
                module.run()
            else:
                st.error(f"'{file_path}'에 'run()' 함수가 정의되어 있지 않습니다. 이 페이지는 'run()' 함수를 포함해야 합니다.")
        except Exception as e:
            st.error(f"'{file_path}' 모듈을 불러오는 중 오류 발생: {e}")

