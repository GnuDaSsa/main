# Codex Skills Registry

This repository is the source of truth for project skills.

## Included skills
- `pdca`
- `video-to-manual`
- `오케이`
- `slash-main`
- `.system/skill-creator`
- `.system/skill-installer`

## Layout
- `codex_skills/<skill-name>/SKILL.md`
- `codex_skills/.system/<skill-name>/SKILL.md`

## Operating rule
1. Create or update skills in this repository first.
2. Sync repository skills to local Codex home when needed:
   - `powershell -ExecutionPolicy Bypass -File .\scripts\sync_codex_skills.ps1`
3. Use synced local skills from `C:\Users\Owner\.codex\skills` during execution.

## Add a new skill
1. Create `codex_skills/<new-skill>/SKILL.md`
2. Follow valid YAML frontmatter:
   - `name: '<skill-name>'`
   - `description: '<short description>'`
3. Run sync script and verify loading.

## Notes
- Use single quotes in YAML strings that include Windows paths (`C:\...`) to avoid escape parsing errors.
