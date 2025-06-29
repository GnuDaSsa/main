import streamlit as st
import io
from odf.opendocument import load
from odf.text import P, Span, H, ListItem
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# (필요시 추가 CSS를 이용하여 입력 바의 너비를 조정할 수 있음)
st.markdown(
    """
    <style>
    /* 좌측 컨테이너 내 입력 상자들을 줄이는 예시 CSS */
    .small-input .stTextInput>div {
        max-width: 50% !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def replace_text_in_node(node, search_text, replace_text):
    if node.nodeType == node.TEXT_NODE:
        if search_text in node.data:
            node.data = node.data.replace(search_text, str(replace_text))
    else:
        for child in node.childNodes:
            replace_text_in_node(child, search_text, replace_text)

def replace_text_in_elements(doc, replacements):
    elements = [P, Span, H, ListItem]
    for elem in elements:
        for node in doc.getElementsByType(elem):
            for search_text, replace_text in replacements.items():
                replace_text_in_node(node, search_text, replace_text)

def run():
    st.title("공문 자동화 프로그램")
    st.write("아래 입력 칸에 값을 입력하세요.")
    
    # 2개의 열 생성: 왼쪽은 입력 필드, 오른쪽은 예시 이미지
    left_col, right_col = st.columns(2)
    
    with left_col:
        # 입력 칸 (좌측 열에 배치되어 페이지 전체의 절반 너비를 사용)
        facility      = st.text_input("시설명")
        report_number = st.text_input("신고번호")
        address       = st.text_input("소재지 주소")
        before_change = st.text_input("변경전")
        after_change  = st.text_input("변경후")
        
        if st.button("생성"):
            if not (facility and report_number and address and before_change and after_change):
                st.error("모든 필드를 입력해주세요.")
            else:
                try:
                    filepath = os.path.join(BASE_DIR, "서식", "page1", "정수기자동화", "수리.odt")
                    with open(filepath, "rb") as f:
                        odt_data = f.read()
                    
                    # ODT 문서 로드
                    doc = load(io.BytesIO(odt_data))
                    
                    # 치환할 변수 매핑 (오리지널 텍스트 "지누다스1" ~ "지누다스5"를 입력값으로 대체)
                    replacements = {
                        "지누다스1": facility,
                        "지누다스2": report_number,
                        "지누다스3": address,
                        "지누다스4": before_change,
                        "지누다스5": after_change
                    }
                    replace_text_in_elements(doc, replacements)
                    
                    # 변경된 문서를 메모리 버퍼에 저장
                    output = io.BytesIO()
                    doc.save(output)
                    output.seek(0)
                    
                    st.download_button(
                        label="공문 다운로드",
                        data=output,
                        file_name="수리_공문.odt",
                        mime="application/vnd.oasis.opendocument.text"
                    )
                    st.success("공문이 성공적으로 생성되었습니다.")
                except Exception as e:
                    st.error(f"오류 발생: {e}")
    
    with right_col:
        st.markdown("### 예시 이미지")
        image_path = os.path.join(BASE_DIR, "서식", "page1", "정수기자동화", "image", "example.png")
        if os.path.exists(image_path):
            st.image(image_path, caption="예시", use_container_width=True)
        else:
            st.error("예시 이미지 파일을 찾을 수 없습니다.")

if __name__ == "__main__":
    run()
