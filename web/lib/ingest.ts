import { getDb } from "./mongodb";

interface IngestOptions {
  queries: string[];
  maxPages?: number;
  pageSize?: number;
}

export async function runIngest(options: IngestOptions) {
  const oc = process.env.LAW_API_OC;
  if (!oc) throw new Error("LAW_API_OC is required.");

  const maxPages = options.maxPages ?? 1;
  const pageSize = options.pageSize ?? 20;
  const db = await getDb();
  const rawCol = db.collection("law_raw_documents");
  const chunkCol = db.collection("law_chunks");
  const logCol = db.collection("law_ingestion_logs");

  let fetchedCount = 0;
  let upsertedCount = 0;
  let chunkCount = 0;

  for (const query of options.queries) {
    for (let page = 1; page <= maxPages; page += 1) {
      const url = new URL("https://www.law.go.kr/DRF/lawSearch.do");
      url.searchParams.set("OC", oc);
      url.searchParams.set("target", "law");
      url.searchParams.set("type", "JSON");
      url.searchParams.set("query", query);
      url.searchParams.set("display", String(pageSize));
      url.searchParams.set("page", String(page));

      const res = await fetch(url.toString(), { method: "GET", cache: "no-store" });
      if (!res.ok) throw new Error(`law api failed: ${res.status}`);
      const data = (await res.json()) as any;
      const list = data?.LawSearch?.law ? (Array.isArray(data.LawSearch.law) ? data.LawSearch.law : [data.LawSearch.law]) : [];
      if (!list.length) break;
      fetchedCount += list.length;

      for (const item of list) {
        const docId = item["법령ID"] || item["법령일련번호"] || item["MST"] || item["ID"] || item["법령명한글"];
        const lawName = item["법령명한글"] || item["법령명"] || "";
        const sourceUrl = item["법령상세링크"] || "";
        const text = [lawName, item["제개정구분명"], item["소관부처명"], sourceUrl].filter(Boolean).join(" ");
        if (!docId) continue;

        await rawCol.updateOne(
          { doc_id: String(docId) },
          {
            $set: {
              doc_id: String(docId),
              law_name: String(lawName),
              source_url: String(sourceUrl),
              text: String(text),
              raw: item,
              updated_at: new Date()
            },
            $setOnInsert: { created_at: new Date() }
          },
          { upsert: true }
        );
        upsertedCount += 1;

        await chunkCol.deleteMany({ doc_id: String(docId) });
        if (text) {
          const row = {
            doc_id: String(docId),
            law_name: String(lawName),
            chunk_index: 0,
            text: String(text),
            vector: [],
            source_url: String(sourceUrl),
            enforcement_date: String(item["시행일자"] || ""),
            created_at: new Date(),
            updated_at: new Date()
          };
          await chunkCol.insertOne(row);
          chunkCount += 1;
        }
      }
    }
  }

  await logCol.insertOne({
    type: "vercel_cron_ingest",
    queries: options.queries,
    max_pages: maxPages,
    page_size: pageSize,
    fetched_count: fetchedCount,
    upserted_count: upsertedCount,
    chunk_count: chunkCount,
    run_at: new Date()
  });

  return { fetchedCount, upsertedCount, chunkCount };
}
