"use client";

import { FormEvent, useState } from "react";
import { CourseResult } from "../lib/types";

export default function HomePage() {
  const [maleStation, setMaleStation] = useState("강남");
  const [femaleStation, setFemaleStation] = useState("홍대입구");
  const [meetingTime, setMeetingTime] = useState("2026-03-01T19:00");
  const [budget, setBudget] = useState("normal");
  const [mobility, setMobility] = useState("transit");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [courses, setCourses] = useState<CourseResult[]>([]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    setCourses([]);
    try {
      const res = await fetch("/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          male_station: maleStation,
          female_station: femaleStation,
          meeting_time: `${meetingTime}:00+09:00`,
          budget_level: budget,
          mobility,
          mood: "neutral",
          max_courses: 3
        })
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data?.error?.message || "추천 요청 실패");
      }
      const data = await res.json();
      setCourses(data.courses || []);
    } catch (err: any) {
      setError(err.message || "에러가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="wrap">
      <h1>Between Us</h1>
      <p className="muted">두 출발역 사이에서 무난한 데이트 코스를 추천합니다.</p>

      <form className="panel" onSubmit={onSubmit}>
        <div className="grid">
          <input className="input" value={maleStation} onChange={(e) => setMaleStation(e.target.value)} placeholder="남자 출발역" />
          <input className="input" value={femaleStation} onChange={(e) => setFemaleStation(e.target.value)} placeholder="여자 출발역" />
          <input className="input" type="datetime-local" value={meetingTime} onChange={(e) => setMeetingTime(e.target.value)} />
          <select className="input" value={budget} onChange={(e) => setBudget(e.target.value)}>
            <option value="low">가성비</option>
            <option value="normal">무난</option>
            <option value="high">여유</option>
          </select>
          <select className="input" value={mobility} onChange={(e) => setMobility(e.target.value)}>
            <option value="transit">대중교통</option>
            <option value="car_optional">차량 가능</option>
          </select>
        </div>
        <div style={{ marginTop: 12 }}>
          <button className="btn" type="submit" disabled={loading}>
            {loading ? "추천 중..." : "코스 추천받기"}
          </button>
        </div>
      </form>

      {error && <p style={{ color: "#b42318" }}>{error}</p>}

      <section className="cards">
        {courses.map((course) => (
          <article key={course.course_id} className="card">
            <h3>{course.title}</h3>
            <p className="muted">
              점수 {course.score} | 이동격차 {course.fairness_gap_min}분 | 예산 {course.budget_estimate} | 주차 {course.parking_status}
            </p>
            <ul>
              {course.reason_tags.map((tag) => (
                <li key={tag}>{tag}</li>
              ))}
            </ul>
          </article>
        ))}
      </section>
    </main>
  );
}
