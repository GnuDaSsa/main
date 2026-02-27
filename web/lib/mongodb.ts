import { MongoClient } from "mongodb";

const uri = process.env.MONGODB_URI;
const dbName = process.env.MONGODB_DB || "dlc";

let cachedClient: MongoClient | null = null;

export async function getDb() {
  if (!uri) throw new Error("MONGODB_URI is required.");
  if (!cachedClient) {
    cachedClient = new MongoClient(uri);
    await cachedClient.connect();
  }
  return cachedClient.db(dbName);
}
