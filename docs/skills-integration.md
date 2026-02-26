# Skills Integration Summary

## Objective
Centralize currently active Codex skills in this repository and use repository-first skill lifecycle.

## Integrated Skills
- `pdca`
- `video-to-manual`
- `오케이`
- `slash-main`
- `.system/skill-creator`
- `.system/skill-installer`

## What was changed
- Copied active local skills into `codex_skills/` with one-skill-per-folder structure.
- Added repository operation guide: `codex_skills/README.md`
- Added repository-wide agent rule: `AGENTS.md`
- Added sync script: `scripts/sync_codex_skills.ps1`

## Workflow from now on
1. Create or modify skills in `codex_skills/`.
2. Commit and push to GitHub.
3. On any device, pull repository and run:
   - `powershell -ExecutionPolicy Bypass -File .\scripts\sync_codex_skills.ps1`
4. Invoke skills after local sync completes.

## Validation checklist
- `SKILL.md` frontmatter parses without YAML errors.
- Skill name and folder path stay aligned.
- Windows paths in YAML values use single quotes.
