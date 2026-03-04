import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from mongo_env import get_setting


SYSTEM_PROMPT = """당신은 음성 녹음 내용을 분석하는 전문가입니다.
변환된 텍스트를 분석하여 다음 형식으로 정리하세요:

## 핵심 요약
(전체 내용을 주제별로 상세하게 정리)

## 할일 / 액션아이템
| 번호 | 액션아이템 | 담당자 | 기한 |
|------|-----------|--------|------|
(언급된 할일, 결정사항, 후속조치를 표로 정리. 담당자/기한 미언급시 -)

담당자나 기한이 명시되지 않은 경우 반드시 -로 표시하세요."""


def run():
    load_dotenv()

    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Noto Sans KR', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 15% 20%, rgba(0, 240, 255, 0.16), transparent 40%),
                radial-gradient(circle at 85% 25%, rgba(255, 77, 166, 0.14), transparent 42%),
                linear-gradient(135deg, #0b1220 0%, #111b2e 55%, #0e1626 100%);
        }

        .glass-card {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.22);
            border-radius: 18px;
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            box-shadow: 0 8px 28px rgba(0, 0, 0, 0.28);
            padding: 18px 20px;
            margin-bottom: 14px;
            animation: fadeIn 0.55s ease;
        }

        .title-wrap {
            background: linear-gradient(90deg, rgba(0, 255, 240, 0.18), rgba(255, 92, 170, 0.16));
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 14px;
            padding: 12px 16px;
            margin-bottom: 6px;
            animation: fadeIn 0.6s ease;
        }

        .title-text {
            font-size: 1.95rem;
            font-weight: 800;
            margin: 0;
            background: linear-gradient(90deg, #7ffcff, #ff8cc8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .sub-text {
            color: rgba(235, 245, 255, 0.9);
            font-size: 0.98rem;
            margin-top: 4px;
            margin-bottom: 0;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="title-wrap">
          <h1 class="title-text">녹음 변환 & 내용 정리</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("음성 파일을 텍스트로 변환하고 핵심 내용과 할일을 자동으로 정리합니다. (최대 25MB)")

    api_key = get_setting("OPENAI_API_KEY")
    if not api_key:
        st.error("OPENAI_API_KEY가 설정되지 않았습니다. 설정을 확인해주세요.")
        return

    client = OpenAI(api_key=api_key)

    for key, default in [
        ("rec_transcript", ""),
        ("rec_summary", ""),
        ("rec_filename", ""),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "오디오 파일 업로드",
        type=["mp3", "mp4", "m4a", "wav", "webm", "ogg", "flac"],
    )
    convert_clicked = st.button("변환 시작", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if convert_clicked:
        if uploaded_file is None:
            st.warning("오디오 파일을 먼저 업로드해주세요.")
        else:
            with st.spinner("변환 중..."):
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=(uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type),
                    language="ko",
                )
                transcript_text = transcription.text

            with st.spinner("요약 중..."):
                summary_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": transcript_text},
                    ],
                    temperature=0.2,
                )
                summary_text = summary_response.choices[0].message.content or ""

            st.session_state.rec_transcript = transcript_text
            st.session_state.rec_summary = summary_text
            st.session_state.rec_filename = uploaded_file.name

    if st.session_state.rec_transcript:
        tab1, tab2 = st.tabs(["요약 & 액션아이템", "원문 텍스트"])
        with tab1:
            st.markdown(st.session_state.rec_summary or "요약 결과가 없습니다.")
        with tab2:
            st.text_area(
                "Whisper 변환 원문",
                value=st.session_state.rec_transcript,
                height=360,
                disabled=True,
            )

        download_text = (
            f"# 요약 & 액션아이템\n\n{st.session_state.rec_summary}\n\n"
            f"# 원문 텍스트\n\n{st.session_state.rec_transcript}\n"
        )
        download_name = (
            f"{st.session_state.rec_filename.rsplit('.', 1)[0]}_summary.txt"
            if st.session_state.rec_filename
            else "recording_summary.txt"
        )
        st.download_button(
            label="txt 다운로드",
            data=download_text,
            file_name=download_name,
            mime="text/plain",
            use_container_width=True,
        )


if __name__ == "__main__":
    run()
