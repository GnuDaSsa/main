# Dating Course API Spec (MVP)

## 1. Endpoint
- `POST /api/v1/courses/recommend`

## 2. Request
```json
{
  "male_station": "강남",
  "female_station": "홍대입구",
  "meeting_time": "2026-03-01T19:00:00+09:00",
  "budget_level": "normal",
  "mobility": "car_optional",
  "mood": "neutral",
  "max_courses": 3
}
```

## 3. Request Validation
- `male_station`, `female_station`: 수도권 역 이름, 필수
- `meeting_time`: ISO8601, 필수
- `budget_level`: `low|normal|high`
- `mobility`: `transit|car_optional`
- `mood`: `neutral` (MVP 기본)
- `max_courses`: 1~5

## 4. Response
```json
{
  "request_id": "rec_20260227_xxx",
  "input_summary": {
    "male_station": "강남",
    "female_station": "홍대입구",
    "mobility": "car_optional"
  },
  "courses": [
    {
      "course_id": "course_1",
      "title": "합정 무난 데이트 코스",
      "score": 84.2,
      "total_time_min": 210,
      "fairness_gap_min": 9,
      "budget_estimate": "60000-90000",
      "parking_status": "available",
      "reason_tags": [
        "후기 대화친화도 높음",
        "저녁 혼잡 리스크 낮음",
        "양측 이동격차 작음"
      ],
      "stops": [
        {
          "type": "meal",
          "name": "장소 A",
          "area": "합정",
          "parking": "nearby"
        },
        {
          "type": "cafe",
          "name": "장소 B",
          "area": "합정",
          "parking": "limited"
        },
        {
          "type": "activity",
          "name": "장소 C",
          "area": "연남",
          "parking": "available"
        }
      ]
    }
  ]
}
```

## 5. Error Response
```json
{
  "error": {
    "code": "INVALID_STATION",
    "message": "수도권 지하철역만 입력 가능합니다."
  }
}
```

## 6. Error Codes
- `INVALID_STATION`
- `INVALID_TIME`
- `NO_CANDIDATE_AREA`
- `NO_PLACE_CANDIDATE`
- `INTERNAL_ERROR`

## 7. Internal Pipeline (MVP)
1. 입력 역 검증
2. 후보 구역 생성
3. 장소 후보 수집
4. 후기/실시간 신호 반영 스코어 계산
5. 코스 조합 및 상위 n개 반환
