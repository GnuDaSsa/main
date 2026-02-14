---
name: push
description: 변경사항을 Git에 커밋하고 GitHub에 푸시합니다.
disable-model-invocation: true
allowed-tools: Bash(git *)
---

# Git Commit & Push

변경사항을 커밋하고 GitHub에 푸시합니다.

## 절차

1. `git status`로 변경된 파일 확인
2. `git diff`로 변경 내용 확인
3. `git log --oneline -3`으로 최근 커밋 스타일 확인
4. 변경된 파일을 `git add`로 스테이징 (민감 파일 .env 등 제외)
5. 변경 내용을 요약하여 커밋 메시지 작성 후 `git commit`
6. `git push origin main`으로 푸시
7. 결과 확인

## 커밋 메시지 규칙

- 한국어 또는 영어로 간결하게 작성
- 변경 목적을 중심으로 작성
- 인자가 제공되면 해당 내용을 커밋 메시지로 사용: $ARGUMENTS

## 주의사항

- `.env` 파일은 절대 커밋하지 않는다
- 커밋 메시지 끝에 항상 추가: `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>`
