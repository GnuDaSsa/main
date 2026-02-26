# AGENTS

## Skill Source Policy
- For this repository, `codex_skills/` is the canonical source for skill definitions.
- When creating or updating a skill, modify `codex_skills/<skill>/SKILL.md` (or `codex_skills/.system/<skill>/SKILL.md`) first.
- After updates, sync skills to local Codex home with:
  - `powershell -ExecutionPolicy Bypass -File .\scripts\sync_codex_skills.ps1`

## Skill Invocation Policy
- When a task requests a skill, resolve it from this repository's `codex_skills/` first.
- If local `C:\Users\Owner\.codex\skills` differs, treat repository content as authoritative and sync before proceeding.

## Validation Rule
- YAML frontmatter must parse cleanly.
- For Windows paths in YAML values, prefer single-quoted strings.
