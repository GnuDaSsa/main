import { NextRequest, NextResponse } from "next/server";
import { runIngest } from "../../../../lib/ingest";

export async function POST(req: NextRequest) {
  try {
    const secret = req.headers.get("x-ingest-secret");
    if (!process.env.INGEST_SECRET || secret !== process.env.INGEST_SECRET) {
      return NextResponse.json({ error: { code: "UNAUTHORIZED", message: "invalid ingest secret" } }, { status: 401 });
    }

    const body = await req.json().catch(() => ({}));
    const queries: string[] = Array.isArray(body?.queries) && body.queries.length ? body.queries : ["근로기준법", "민법", "상법"];
    const result = await runIngest({
      queries,
      maxPages: Number(body?.max_pages || 1),
      pageSize: Number(body?.page_size || 20)
    });
    return NextResponse.json({ ok: true, ...result });
  } catch (error: any) {
    return NextResponse.json({ ok: false, error: error?.message || "unknown error" }, { status: 500 });
  }
}
