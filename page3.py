# pages/3_PDF_변환.py

import streamlit as st
import os
import win32com.client as win32
import pythoncom
import tempfile
import zipfile
import io
import time

# --- 함수 정의 부분 ---
def convert_hwp_to_pdf(hwp_file, output_dir):
    # (기존 convert_hwp_to_pdf 함수 내용은 변경 없음)
    pythoncom.CoInitialize()
    hwp = None
    tmp_hwp_path = None
    try:
        hwp = win32.Dispatch("HWPFrame.HwpObject")
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".hwp") as tmp_hwp:
            tmp_hwp.write(hwp_file.getvalue())
            tmp_hwp_path = tmp_hwp.name
        hwp.Open(tmp_hwp_path, "HWP", "versionwarning:false")
        base_filename = os.path.splitext(hwp_file.name)[0]
        pdf_path = os.path.join(output_dir, f"{base_filename}.pdf")
        hwp.HAction.GetDefault("FileSaveAsPdf", hwp.HParameterSet.HFileOpenSave.HSet)
        hwp.HParameterSet.HFileOpenSave.filename = pdf_path
        hwp.HParameterSet.HFileOpenSave.Format = "PDF"
        hwp.HAction.Execute("FileSaveAsPdf", hwp.HParameterSet.HFileOpenSave.HSet)
        return pdf_path
    except Exception as e:
        st.error(f"'{hwp_file.name}' 변환 중 오류 발생: {e}")
        return None
    finally:
        if hwp:
            hwp.Quit()
        time.sleep(0.5)
        if tmp_hwp_path and os.path.exists(tmp_hwp_path):
            os.remove(tmp_hwp_path)
        pythoncom.CoUninitialize()

# --- 이 페이지의 모든 UI와 로직을 run() 함수 안에 배치 ---
def run():
    st.title("📄 한글(HWP) 파일을 PDF로 일괄 변환")
    st.warning("⚠️ **주의:** 이 앱은 Windows 및 한컴오피스가 설치된 환경에서만 작동합니다.")

    uploaded_files = st.file_uploader(
        "PDF로 변환할 한글 파일(.hwp, .hwpml)을 모두 선택하세요.",
        type=['hwp', 'hwpml'],
        accept_multiple_files=True
    )

    if not uploaded_files:
        st.info("파일을 업로드하면 변환 버튼이 나타납니다.")
    else:
        if st.button("모든 파일을 PDF로 변환하기", type="primary"):
            # (이하 변환 및 다운로드 로직은 기존과 동일)
            with tempfile.TemporaryDirectory() as temp_dir:
                pdf_files = []
                progress_bar = st.progress(0, text="변환을 시작합니다...")
                total_files = len(uploaded_files)
                for i, file in enumerate(uploaded_files):
                    progress_text = f"'{file.name}' 변환 중... ({i+1}/{total_files})"
                    progress_bar.progress((i + 1) / total_files, text=progress_text)
                    pdf_path = convert_hwp_to_pdf(file, temp_dir)
                    if pdf_path:
                        pdf_files.append(pdf_path)
                        st.write(f"✅ '{file.name}' → '{os.path.basename(pdf_path)}' 변환 완료")
                progress_bar.empty()
                if pdf_files:
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w") as zf:
                        for pdf_file in pdf_files:
                            zf.write(pdf_file, os.path.basename(pdf_file))
                    st.success("🎉 모든 파일 변환이 완료되었습니다!")
                    st.download_button(
                        label="변환된 모든 PDF 파일 다운로드 (.zip)",
                        data=zip_buffer.getvalue(),
                        file_name="converted_pdfs.zip",
                        mime="application/zip",
                    )
                else:
                    st.error("변환된 PDF 파일이 없습니다.")

# 이 파일을 직접 실행할 경우를 대비해 추가 (선택 사항)
if __name__ == '__main__':
    run()