import json
import os
import base64
import io

import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from google import genai as genai_new
from google.genai import types

from mongo_env import get_setting


STYLES = {
    '사실적 (Photorealistic)': 'photorealistic',
    '시네마틱 (Cinematic)': 'cinematic',
    '초현실적 (Surreal)': 'surreal',
    '애니메이션 (Anime)': 'anime',
    '수채화 (Watercolor)': 'watercolor',
}

ASPECT_RATIOS = ['1:1', '16:9', '4:3', '3:4', '9:16']


def _convert_to_json(model, user_prompt, style, aspect_ratio):
    system_prompt = """You are an expert image prompt engineer.
Convert the user's natural language request into a structured JSON object.
Return ONLY valid JSON. Fill ALL fields with rich, specific detail — never leave fields empty.

JSON schema:
{
  "description": "A detailed English description of the image scene (2-3 sentences)",
  "style": {
    "primary": "string (e.g. photorealistic, cinematic, surreal, anime, watercolor)",
    "rendering_quality": "string (e.g. 4K ultra-HD, 8K hyperrealistic)",
    "lighting": {
      "type": "string (e.g. soft natural daylight, dramatic studio lighting, neon glow)",
      "direction": "string (e.g. side-lit 45°, backlit, top-down)",
      "mood": "string (e.g. warm, moody, ethereal, dramatic)"
    }
  },
  "technical": {
    "resolution": "string (e.g. 4K)",
    "aspect_ratio": "string",
    "camera": {
      "focal_length": "string (e.g. 85mm, 35mm wide-angle)",
      "depth_of_field": "string (e.g. shallow f/1.4, deep f/11)"
    }
  },
  "composition": {
    "framing": "string (e.g. rule of thirds, centered, close-up)",
    "perspective": "string (e.g. eye-level, low-angle, bird's-eye)"
  },
  "environment": {
    "atmosphere": "string (e.g. foggy, clear, dusty, misty)",
    "temporal": "string (e.g. golden hour, midnight, overcast afternoon)"
  },
  "quality": {
    "include": ["list of desired qualities"],
    "avoid": ["list of things to avoid"]
  }
}

Requirements:
- The 'description' field must be a vivid, detailed English scene description.
- Fill every field with contextually appropriate values based on user intent.
- Never return empty objects or arrays.""".strip()

    user_content = json.dumps({
        "user_prompt": user_prompt,
        "requested_style": style,
        "requested_aspect_ratio": aspect_ratio,
    }, ensure_ascii=False)

    try:
        response = model.generate_content(
            f"{system_prompt}\n\nUser request:\n{user_content}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                response_mime_type="application/json",
            ),
        )
        return json.loads(response.text)
    except Exception:
        return None


def _build_image_prompt(json_data: dict) -> str:
    desc = json_data.get("description", "")
    style = json_data.get("style", {})
    tech = json_data.get("technical", {})
    comp = json_data.get("composition", {})
    env = json_data.get("environment", {})
    quality = json_data.get("quality", {})

    parts = []
    if desc:
        parts.append(desc)

    style_str = style.get("primary", "")
    if style.get("rendering_quality"):
        style_str += f", {style['rendering_quality']}"
    lighting = style.get("lighting", {})
    if lighting.get("type"):
        style_str += f", {lighting['type']} lighting"
    if lighting.get("mood"):
        style_str += f", {lighting['mood']} mood"
    if style_str:
        parts.append(f"Style: {style_str}.")

    camera = tech.get("camera", {})
    if camera.get("focal_length") or camera.get("depth_of_field"):
        parts.append(f"Shot with {camera.get('focal_length', '')} lens, {camera.get('depth_of_field', '')}.")

    if comp.get("framing") or comp.get("perspective"):
        parts.append(f"{comp.get('framing', '')} composition, {comp.get('perspective', '')} view.")

    if env.get("atmosphere") or env.get("temporal"):
        parts.append(f"{env.get('atmosphere', '')} atmosphere, {env.get('temporal', '')}.")

    includes = quality.get("include", [])
    if includes:
        parts.append(f"Ensure: {', '.join(includes)}.")

    avoids = quality.get("avoid", [])
    if avoids:
        parts.append(f"Avoid: {', '.join(avoids)}.")

    return " ".join(parts)


def _generate_image(api_key, json_data: dict, ref_images=None):
    try:
        prompt = _build_image_prompt(json_data)
        client = genai_new.Client(api_key=api_key)

        if ref_images:
            contents = [
                types.Part.from_bytes(data=img_bytes, mime_type=mime)
                for img_bytes, mime in ref_images
            ]
            contents.append(prompt)
        else:
            contents = prompt

        response = client.models.generate_content(
            model='gemini-2.5-flash-image',
            contents=contents,
            config=types.GenerateContentConfig(response_modalities=['TEXT', 'IMAGE']),
        )

        for part in response.candidates[0].content.parts:
            if getattr(part, 'inline_data', None):
                data = part.inline_data.data
                mime_type = getattr(part.inline_data, 'mime_type', 'image/png')
                if isinstance(data, str):
                    try:
                        return base64.b64decode(data), mime_type
                    except Exception:
                        return data.encode('utf-8'), mime_type
                return data, mime_type

        return None, None
    except Exception:
        return None, None


def _run_generation(model, api_key, user_prompt, style, aspect_ratio,
                    ref_images=None):
    with st.spinner('프롬프트를 JSON으로 변환 중...'):
        json_result = _convert_to_json(model, user_prompt, style, aspect_ratio)

    if json_result is None:
        st.error('JSON 프롬프트 변환에 실패했습니다. 입력을 조금 더 구체적으로 작성한 뒤 다시 시도해주세요.')
        return

    st.session_state.img_json_prompt = json_result

    with st.expander('변환된 JSON 프롬프트', expanded=True):
        st.json(json_result)

    with st.spinner('이미지 생성 중... (최대 30초 소요)'):
        image_bytes, mime_type = _generate_image(
            api_key, json_result, ref_images=ref_images,
        )

    if image_bytes is None:
        st.error('이미지 생성에 실패했습니다. 잠시 후 다시 시도해주세요.')
        return

    st.session_state.img_generated_image = image_bytes
    st.session_state.img_mime_type = mime_type or 'image/png'
    st.session_state.img_generation_count += 1

    st.image(io.BytesIO(image_bytes), caption='생성된 이미지', use_container_width=True)
    st.download_button(
        label='이미지 다운로드',
        data=image_bytes,
        file_name='generated_image.png',
        mime=st.session_state.img_mime_type,
        use_container_width=True,
    )


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
          <h1 class="title-text">AI 이미지 프롬프트 변환기</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption('자연어 설명을 구조화된 JSON 프롬프트로 변환하고, Gemini 2.5 Flash Image(나노바나나)로 이미지를 생성합니다.')

    api_key = get_setting('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not api_key:
        st.error('GEMINI_API_KEY가 설정되지 않았습니다. 환경 변수 또는 설정을 확인해주세요.')
        return

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    for key, default in [
        ('img_generated_image', None), ('img_json_prompt', None),
        ('img_generation_count', 0), ('img_mime_type', 'image/png'),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    ref_files = st.file_uploader(
        '참조 이미지 (선택사항, 여러 장 가능)',
        type=['png', 'jpg', 'jpeg', 'webp'],
        accept_multiple_files=True,
        help='이미지를 첨부하면 해당 이미지를 기반으로 생성합니다. 없으면 텍스트만으로 생성합니다.',
    )
    if ref_files:
        cols = st.columns(min(len(ref_files), 4))
        for i, f in enumerate(ref_files):
            cols[i % len(cols)].image(f, caption=f.name, width=180)

    user_prompt = st.text_area(
        '이미지 설명 입력',
        height=150,
        placeholder='예: 빗속 네온사인이 비치는 서울의 밤거리에서 우산을 든 인물을 시네마틱하게 표현해줘\n\n(참조 이미지 첨부 시) 이 이미지를 수채화 스타일로 바꿔줘',
    )

    col1, col2 = st.columns(2)
    with col1:
        style_label = st.selectbox('스타일', list(STYLES.keys()), index=0)
    with col2:
        aspect_ratio = st.selectbox('화면 비율', ASPECT_RATIOS, index=0)

    generate = st.button('이미지 생성', type='primary', use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if generate:
        if not user_prompt.strip():
            st.warning('이미지 설명을 먼저 입력해주세요.')
        else:
            ref_images = []
            if ref_files:
                for f in ref_files:
                    ref_images.append((f.getvalue(), f.type or 'image/png'))
            _run_generation(
                model, api_key, user_prompt.strip(),
                STYLES[style_label], aspect_ratio,
                ref_images=ref_images,
            )

    # ── 이전 결과 표시 ──
    if not generate and st.session_state.img_generated_image is not None:
        if st.session_state.img_json_prompt is not None:
            with st.expander('최근 JSON 프롬프트', expanded=False):
                st.json(st.session_state.img_json_prompt)
        prev_stream = io.BytesIO(st.session_state.img_generated_image)
        st.image(prev_stream, caption='최근 생성 이미지', use_container_width=True)
        st.download_button(
            label='이미지 다운로드',
            data=st.session_state.img_generated_image,
            file_name='generated_image.png',
            mime=st.session_state.img_mime_type or 'image/png',
            use_container_width=True,
        )

    st.caption(f"총 생성 횟수: {st.session_state.img_generation_count}")


if __name__ == '__main__':