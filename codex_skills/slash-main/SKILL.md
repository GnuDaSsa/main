---
name: '/main'
description: '/main 명령으로 Codex의 작업 기준을 main 리포지토리(C:\Users\Owner\Desktop\사진우\AI\main)로 전환하고, 이후 모든 수정/실행/반영을 main 리포 기준으로 수행하는 워크플로.'
---

# /main

## 목적
- 사용자가 `/main`이라고 입력하면, Codex는 즉시 **main 리포지토리 기준으로 작업**한다.
- 이후 모든 파일 탐색/수정/실행은 `C:\Users\Owner\Desktop\사진우\AI\main`을 기준으로 한다.

## 즉시 수행(트리거 직후)
1. 작업 디렉터리를 `C:\Users\Owner\Desktop\사진우\AI\main`으로 간주한다.
2. 다음을 빠르게 점검하고 결과를 짧게 보고한다.
- `.git` 존재 여부
- `app.py` 존재 여부
- `assets/monitor_image.png` 또는 `monitor_image.png` 존재 여부
- `origin` 원격 URL(가능하면)

## 작업 규칙
- **부모 폴더 리포(`C:\Users\Owner\Desktop\사진우\AI`)는 건드리지 않는다.**
- 파일 경로 표기는 기본적으로 `main/` 기준 상대경로로 한다(예: `app.py`, `assets/monitor_image.png`).
- Streamlit 실행은 기본적으로 `streamlit run app.py --server.port 8512`를 사용한다.

## 반영(커밋/푸시)
- 커밋/푸시 흐름은 `오케이` 스킬의 승인 규칙을 따른다.
- 사용자가 `/main`만 쳤을 때는 커밋/푸시를 절대 수행하지 않는다.

## 자주 쓰는 명령(참고)
- 로컬 실행: `streamlit run app.py --server.port 8512`
- 포트 확인: `Get-NetTCPConnection -LocalPort 8512 -State Listen`
