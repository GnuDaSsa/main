import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from mongo_env import get_setting


MAX_CHUNK = 24 * 1024 * 1024  # 24 MB


def _transcribe(client, file_bytes: bytes, filename: str, mime_type: str, progress_cb=None) -> str:
    if len(file_bytes) <= MAX_CHUNK:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=(filename, file_bytes, mime_type),
            language="ko",
        )
        return result.text
    chunks = [file_bytes[i:i + MAX_CHUNK] for i in range(0, len(file_bytes), MAX_CHUNK)]
    texts = []
    for i, chunk in enumerate(chunks):
        if progress_cb:
            progress_cb(i, len(chunks))
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=(filename, chunk, mime_type),
            language="ko",
        )
        texts.append(result.text)
    return " ".join(texts)


SYSTEM_PROMPT = """당신은 음성 녹음 내용을 분석하는 전문가입니다.

먼저 텍스트를 보고 화자가 여럿인지 판단하세요.
화자 감지 기준: 질문-답변 패턴, 대화체 문장 교차, '~라고 했다/말했다' 표현, 명확한 시점 전환 등.

[단일 화자인 경우]
아래 계층 구조로 핵심 내용을 정리하세요:
■ 대주제 (굵은 항목)
  ● 세부 항목
    - 상세 내용
    ' 인용 또는 예시 문구

[다중 화자인 경우]
1단계: 각 화자를 [화자 A], [화자 B] 순으로 구분하여 대화 흐름을 간략히 정리
2단계: 전체 내용을 위 계층 구조(■ ● - ')로 통합 요약

## 핵심 요약
(위 규칙에 따라 작성)"""


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
          <h1 class="title-text">녹음TXT변환 및 요약</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("음성 파일을 텍스트로 변환하고 핵심 내용을 자동으로 정리합니다. (최대 25MB, 초과 시 자동 분할)")

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

    uploaded_file = st.file_uploader(
        "오디오 파일 업로드",
        type=["mp3", "mp4", "m4a", "wav", "webm", "ogg", "flac"],
    )
    convert_clicked = st.button("변환 시작", type="primary", use_container_width=True)

    if convert_clicked:
        if uploaded_file is None:
            st.warning("오디오 파일을 먼저 업로드해주세요.")
        else:
            with st.spinner("변환 중..."):
                file_bytes = uploaded_file.getvalue()
                total_chunks = max(1, -(-len(file_bytes) // MAX_CHUNK))
                if total_chunks > 1:
                    size_mb = len(file_bytes) / (1024 * 1024)
                    chunk_status = st.empty()
                    def progress_cb(i, total):
                        chunk_status.info(f"청크 {i+1}/{total} 변환 중... ({size_mb:.1f}MB 파일 자동 분할)")
                    transcript_text = _transcribe(client, file_bytes, uploaded_file.name, uploaded_file.type, progress_cb)
                    chunk_status.empty()
                else:
                    transcript_text = _transcribe(client, file_bytes, uploaded_file.name, uploaded_file.type)

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
        tab1, tab2 = st.tabs(["핵심 요약", "원문 텍스트"])
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
            f"# 핵심 요약\n\n{st.session_state.rec_summary}\n\n"
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
