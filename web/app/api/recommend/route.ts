import { NextRequest, NextResponse } from "next/server";
import { recommendCourses } from "../../../lib/recommender";
import { RecommendRequest } from "../../../lib/types";

export async function POST(req: NextRequest) {
  try {
    const body = (await req.json()) as RecommendRequest;
    if (!body?.male_station || !body?.female_station) {
      return NextResponse.json(
        {
          error: { code: "INVALID_STATION", message: "남자/여자 출발역은 필수입니다." }
        },
        { status: 400 }
      );
    }
    if (!body?.meeting_time) {
      return NextResponse.json({ error: { code: "INVALID_TIME", message: "meeting_time이 필요합니다." } }, { status: 400 });
    }

    const courses = recommendCourses(body);
    return NextResponse.json({
      request_id: `rec_${Date.now()}`,
      input_summary: {
        male_station: body.male_station,
        female_station: body.female_station,
        mobility: body.mobility
      },
      courses
    });
  } catch (error: any) {
    return NextResponse.json({ error: { code: "INTERNAL_ERROR", message: error?.message || "unknown error" } }, { status: 500 });
  }
}
