export type Mobility = "transit" | "car_optional";
export type BudgetLevel = "low" | "normal" | "high";

export interface RecommendRequest {
  male_station: string;
  female_station: string;
  meeting_time: string;
  budget_level: BudgetLevel;
  mobility: Mobility;
  mood?: "neutral";
  max_courses?: number;
}

export interface CourseStop {
  type: "meal" | "cafe" | "activity";
  name: string;
  area: string;
  parking: "available" | "nearby" | "limited" | "unknown";
}

export interface CourseResult {
  course_id: string;
  title: string;
  score: number;
  total_time_min: number;
  fairness_gap_min: number;
  budget_estimate: string;
  parking_status: "available" | "limited" | "unknown";
  reason_tags: string[];
  stops: CourseStop[];
}
