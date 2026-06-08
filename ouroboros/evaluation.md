# Ouroboros Evaluation: Seongnam Vehicle Road-Damage MVP

## Latest Interview Input

User correction:

- Start by fixing the vehicle road-accident flow.
- Incident statement is ultimately a form, so provide a mock form download.
- Vehicle damage evidence is for insurer submission and should not be requested at the municipal first-guidance stage.
- Location material should not be a separate upload; it belongs in the incident statement.
- User should directly pin the accident location on a map.
- Seongnam is a good demo city because Sujeong/Jungwon/Bundang district separation is clear.
- After map selection, show the competent district road-management team number.
- Use these configured numbers:
  - Sujeong-gu: `031-729-5354`
  - Jungwon-gu: `031-729-6354`
  - Bundang-gu: `031-729-7364`
- Flow order:
  1. competent road-management team number
  2. Smart City Department CCTV request only when needed
- CCTV request is mostly needed when there is no dashcam footage, so show it only when the user checks `블랙박스가 없어요`.
- Pothole and sinkhole should be merged into one practical user choice.
- Remove decorative district shapes from the map.
- Allow location search by road-name/jibun-like text before map pinning.
- Replace producer-facing labels like `지자체 단계에서 필요한 것` and `경위서 가라 서식` with citizen-facing language.
- If the user clicks outside Seongnam, do not force-classify it as Sujeong-gu; lock the map and reject out-of-demo-bounds coordinates.
- Sidewalk flow was accidentally removed and must be restored.
- If there is no visible road damage, asking for a map location is wrong; guide the user directly to State Compensation.
- State Compensation section must explain what the system is, provide a form example, and explain where to send it for Seongnam.

## Mechanical Verification

- Static artifact: `index.html`
- Browser smoke test: pass
- Console errors: none
- Damage choices: 3
- Map stage appears after selecting `도로 꺼짐·패임`.
- Location search works with demo road-name keywords such as `성남대로`.
- Page load after bounds patch: pass
- Search UI and out-of-bounds message present: pass
- Source inspection confirms Leaflet `maxBounds` and coordinate bounds guard.
- First screen now has road/sidewalk choices: pass
- Sidewalk choices restored: pass
- No-visible-road-damage goes directly to State Compensation without map: pass
- State Compensation section includes explanation, Seongnam send-to office, and form download: pass
- Bundang sample maps to `분당구`.
- Result stage shows `031-729-7364`.
- CCTV panel is hidden before checking `블랙박스가 없어요`.
- CCTV panel appears after checking `블랙박스가 없어요`.
- Source inspection confirms downloadable `.doc` incident statement is generated using a Blob.

Download note:

- Codex in-app browser does not support download-event verification, so the download was verified by source inspection rather than by capturing the browser download event.

## Acceptance Criteria

| Criterion | Result |
| --- | --- |
| Road and sidewalk first-choice flow | Pass |
| Pothole/sinkhole merged into one road-hole choice | Pass |
| Decorative district shapes removed from map | Pass |
| Road-name/jibun-like location search implemented | Pass |
| Seongnam-only map bounds and out-of-bounds guard implemented | Pass |
| Sidewalk flow restored | Pass |
| No-visible-road-damage bypasses map and opens State Compensation guidance | Pass |
| State Compensation explanation and Seongnam send-to office added | Pass |
| Map pin structure implemented | Pass |
| Seongnam district routing implemented | Pass |
| User-specified district phone numbers shown | Pass |
| Separate vehicle damage evidence UI removed | Pass |
| Separate location-material UI removed | Pass |
| Citizen-facing incident form download implemented | Pass |
| CCTV guidance hidden unless no dashcam | Pass |
| Legal/compensation judgment avoided | Pass |

## Reviewer Notes

This loop corrected the product logic substantially. The MVP now matches the intended municipal-first workflow:

```text
road damage type -> search or map pin -> district road-management team -> incident form download -> CCTV only if no dashcam
```

Remaining risks:

- District detection uses demo nearest-center logic inside a Seongnam-only bounding box, not official GIS boundary polygons.
- The incident form is a mock `.doc` generated in-browser.
- Smart City Department CCTV guidance uses the city representative number path rather than a verified direct CCTV operations number.

## Evolve

Recommended next question:

```text
사고 내용 작성 양식에 꼭 들어가야 하는 항목을 실제 공문 느낌으로 더 늘릴까요, 아니면 심사 데모용으로 지금처럼 짧게 둘까요?
```
