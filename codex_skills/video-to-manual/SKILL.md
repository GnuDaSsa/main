---
name: video-to-manual
description: 화면 녹화 영상을 분석해 단계별 매뉴얼(마크다운/PPTX)을 생성하는 워크플로. "영상 매뉴얼", "프레임 추출", "영상으로 PPTX 만들기", "video to manual" 요청에서 사용.
---

# video-to-manual

화면 녹화 영상을 분석해 단계별 매뉴얼(`.md`)과 발표용 자료(`.pptx`)를 만든다.

## 고정 규칙 (중요)

- 매 작업마다 **새 작업 폴더**를 만든다.
- 지정 루트 경로 아래에 `YYYYMMDD_HHMMSS_{작업명}` 형식으로 생성한다.
- 결과물은 모두 해당 작업 폴더 안에만 저장한다.
- 루트 경로 기본값:
  - `C:\Users\Owner\Desktop\사진우\92. 개인\AI 유용한 자료\매뉴얼화 이미지폴더`

## 트리거

- "영상 매뉴얼"
- "동영상 설명서"
- "화면녹화 매뉴얼"
- "영상 pptx"
- "프레임 추출해서 매뉴얼"
- "영상으로 매뉴얼 만들어"
- "video to manual"

## 워크플로우

### 1단계: 작업 폴더 생성 + 영상 입력

1. 사용자에게 원본 영상 경로를 받는다.
2. 루트 경로(기본값 사용 또는 사용자 지정)를 확인한다.
3. 새 작업 폴더를 만든다. 예:
   - `...\매뉴얼화 이미지폴더\20260225_170500_출장여비-정산`
4. 이후 모든 파일은 이 폴더에 저장한다.

저장 구조:

```text
{job_dir}/
  frames/
  manual.md
  pptx_config.json
  {title}.pptx
```

### 2단계: 영상 메타 확인 + 프레임 추출

```bash
ffprobe -v quiet -print_format json -show_format -show_streams "<video>"
```

간격 규칙:
- 300초 이하: 2초
- 300~900초: 3초
- 900초 초과: 5초

```bash
ffmpeg -i "<video>" -vf "fps=1/<interval>" -q:v 2 "<job_dir>/frames/frame_%04d.jpg"
```

### 3단계: 프레임 분석/분류

- 1차 스캔: 10장 간격 샘플링
- 2차 스캔: 전환 구간 전후 상세 확인
- 분류:
  - 관련 프레임
  - 무관 프레임
  - 민감 프레임(개인정보/내부식별정보 노출)

사용자 확인:
- 섹션 구분/대표 프레임 확정
- 제외 프레임 확정

### 4단계: 마크다운 초안 작성

- `{job_dir}/manual.md` 생성
- 최소 포함:
  - 개요(대상/시간/난이도)
  - STEP별 스크린샷/설명/사용자 행동/시간
  - 요약 테이블
  - 민감정보 처리 권고

### 5단계: PPTX 설정 생성/실행

- `{job_dir}/pptx_config.json` 생성
- 아래 필드를 반드시 포함:
  - `auto_job_folder: false` (이미 작업 폴더를 만든 뒤 실행할 때)
  - `job_dir: "{job_dir}"`
  - `frames_dir: "frames"`
  - `output: "{title}.pptx"`

`make_pptx.py` 실행:

```bash
python C:\Users\Owner\.codex\skills\video-to-manual\scripts\make_pptx.py "<job_dir>\pptx_config.json"
```

## make_pptx.py 경로 규칙

스크립트는 다음 키를 지원한다.

- `job_dir`: 결과물 저장 폴더(상대/절대 모두 가능)
- `auto_job_folder`: `true`이면 `job_root` 아래에 타임스탬프 폴더 자동 생성
- `job_root`: 자동 생성 시 루트 경로
- `job_name`: 자동 생성 폴더명 suffix
- `frames_dir`: 기본값 `frames` (상대경로면 `job_dir` 기준)
- `output`: 절대경로가 아니면 `job_dir` 기준 저장

## 의존성

- `ffmpeg`, `ffprobe`
- `python-pptx`
