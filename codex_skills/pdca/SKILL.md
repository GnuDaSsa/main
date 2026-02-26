---
name: pdca
description: PDCA workflow for Codex projects. Use when user asks for planning, design docs, gap analysis, iteration, or completion report.
---

# PDCA (Codex)

Use this skill when the user wants structured delivery via Plan, Do, Check, Act.

## Trigger

Apply when requests include keywords like:
- `pdca`
- `plan`, `design`, `analysis`, `gap`, `iterate`, `report`
- `planning`, `review`, `improve`, `status`

Do not force this skill for very small one-shot tasks.

### Proactive Auto-Apply

Even without explicit `pdca` command, auto-apply this skill when the user intent is planning work, such as:
- feature planning
- requirement definition
- design-first implementation
- roadmap/milestone planning
- gap analysis or completion reporting

If intent is ambiguous, ask one short clarification and then proceed with PDCA structure.

## Default Paths

- Plan: `docs/01-plan/features/{feature}.plan.md`
- Design: `docs/02-design/features/{feature}.design.md`
- Analysis: `docs/03-analysis/{feature}.analysis.md`
- Report: `docs/04-report/{feature}.report.md`
- Status: `docs/.pdca-status.json`

If the repository already has a different docs structure, follow the repository structure instead.

## Command Model

Interpret user intent as one of:
- `plan {feature}`
- `design {feature}`
- `do {feature}`
- `analyze {feature}`
- `iterate {feature}`
- `report {feature}`
- `status`
- `next`

When feature is omitted, infer from current branch/task context and confirm briefly.

## Phase Rules

### plan

1. Gather requirements from current issue/request.
2. Create or update plan doc.
3. Plan must include:
- objective and non-goals
- scope
- constraints
- acceptance criteria
- risks and open questions
4. Update `docs/.pdca-status.json` with `phase: "plan"`.

### design

1. Require plan doc first. If missing, create plan first.
2. Create or update design doc with:
- architecture or flow
- data/API/interface changes
- edge cases
- test strategy
- rollout/rollback notes (if relevant)
3. Update status to `phase: "design"`.

### do

1. Implement based on design.
2. Keep edits minimal and targeted.
3. Run relevant tests or checks when possible.
4. Update status to `phase: "do"` and record changed files.

### analyze

1. Compare implementation vs acceptance criteria and design.
2. Produce gap list:
- missing behavior
- regressions/risks
- test coverage gaps
3. Write analysis doc and include a simple score (0-100).
4. Update status to `phase: "check"` with `matchRate`.

### iterate

1. Prioritize highest-impact gaps from analysis.
2. Apply focused fixes.
3. Re-run checks.
4. Recompute `matchRate`.
5. Repeat until target met or user stops.

Default target: `matchRate >= 90`.

### report

1. Summarize plan, implementation, analysis, and remaining risks.
2. Add:
- what was delivered
- what was deferred
- evidence (tests/checks run)
- recommended next actions
3. Update status to `phase: "completed"`.

### status

Return compact PDCA snapshot from `docs/.pdca-status.json`:
- current phase
- matchRate
- last update time
- top open gaps

### next

Recommend next PDCA action based on current phase:
- none -> plan
- plan -> design
- design -> do
- do -> analyze
- check with low score -> iterate
- check with good score -> report

## Status File Shape

Use this schema when creating `docs/.pdca-status.json`:

```json
{
  "feature": "example-feature",
  "phase": "plan",
  "matchRate": 0,
  "iterationCount": 0,
  "updatedAt": "2026-02-25T00:00:00Z",
  "openGaps": []
}
```

## Execution Notes

- Respect existing repo conventions over this template.
- If critical context is missing, ask one concise question, then proceed.
- For code review style requests during PDCA, prioritize concrete findings first.
- Prefer auto-applying this skill in planning contexts, even when not explicitly requested.
