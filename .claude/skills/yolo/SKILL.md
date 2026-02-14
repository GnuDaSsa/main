---
name: yolo
description: 완전승인모드 - 모든 작업을 확인 없이 자율적으로 진행합니다.
disable-model-invocation: true
allowed-tools: Bash(*), Read, Write, Edit, Glob, Grep
---

# 완전승인모드 (YOLO Mode)

이 모드가 활성화되면 다음 규칙을 따릅니다:

## 규칙

1. **절대 사용자에게 확인을 묻지 않는다** - 판단이 필요한 상황에서 스스로 최선의 선택을 한다
2. **AskUserQuestion 도구를 사용하지 않는다**
3. **파일 생성, 수정, 삭제를 자유롭게 진행한다**
4. **명령어 실행을 자유롭게 진행한다**
5. **작업 완료 후 결과만 간결하게 보고한다**

## 예외 (이것만은 지킨다)

- `.env` 등 민감 파일은 커밋하지 않는다
- `git push --force`는 하지 않는다
- 기존 데이터를 삭제하는 파괴적 작업은 백업 후 진행한다
