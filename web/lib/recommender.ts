import { CourseResult, Mobility, RecommendRequest } from "./types";

const AREAS = ["합정", "홍대", "을지로", "성수", "잠실", "건대입구"];

function hashToRange(seed: string, min: number, max: number): number {
  let h = 0;
  for (let i = 0; i < seed.length; i += 1) h = (h * 31 + seed.charCodeAt(i)) >>> 0;
  return min + (h % (max - min + 1));
}

function parkingLabel(mobility: Mobility, idx: number): "available" | "limited" | "unknown" {
  if (mobility === "transit") return "unknown";
  if (idx === 0) return "available";
  if (idx === 1) return "limited";
  return "unknown";
}

export function recommendCourses(input: RecommendRequest): CourseResult[] {
  const maxCourses = Math.max(1, Math.min(5, input.max_courses ?? 3));
  const seed = `${input.male_station}-${input.female_station}-${input.meeting_time}-${input.budget_level}`;
  const baseGap = hashToRange(seed, 6, 18);

  const courses: CourseResult[] = [];
  for (let i = 0; i < maxCourses; i += 1) {
    const area = AREAS[(hashToRange(`${seed}-${i}`, 0, 999) + i) % AREAS.length];
    const fairnessGap = baseGap + i * 3;
    if (fairnessGap > 25) continue;

    const review = 80 - i * 3;
    const neutralMood = 84 - i * 2;
    const realtime = 76 - i;
    const fairness = Math.max(0, 100 - fairnessGap * 3);
    const access = 78 - i * 2;
    const parking = input.mobility === "car_optional" ? 72 - i * 6 : 0;
    const score =
      input.mobility === "car_optional"
        ? 0.35 * review + 0.2 * neutralMood + 0.15 * realtime + 0.15 * fairness + 0.1 * access + 0.05 * parking
        : 0.37 * review + 0.2 * neutralMood + 0.16 * realtime + 0.17 * fairness + 0.1 * access;

    courses.push({
      course_id: `course_${i + 1}`,
      title: `${area} 무난 데이트 코스`,
      score: Number(score.toFixed(1)),
      total_time_min: hashToRange(`${seed}-t-${i}`, 170, 240),
      fairness_gap_min: fairnessGap,
      budget_estimate: input.budget_level === "low" ? "40000-60000" : input.budget_level === "high" ? "90000-130000" : "60000-90000",
      parking_status: parkingLabel(input.mobility, i),
      reason_tags: [
        "후기 대화친화도 높음",
        "시간대 혼잡 리스크 보통 이하",
        `양측 이동격차 ${fairnessGap}분`
      ],
      stops: [
        { type: "meal", name: `${area} 식사 스팟`, area, parking: input.mobility === "car_optional" ? "nearby" : "unknown" },
        { type: "cafe", name: `${area} 카페 스팟`, area, parking: input.mobility === "car_optional" ? "limited" : "unknown" },
        { type: "activity", name: `${area} 활동 스팟`, area, parking: input.mobility === "car_optional" ? "available" : "unknown" }
      ]
    });
  }

  return courses.slice(0, maxCourses);
}
