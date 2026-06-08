import { createReadStream, existsSync, readFileSync } from "node:fs";
import { createServer } from "node:http";
import { dirname, extname, join, normalize, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)));
const port = Number(process.env.PORT || 5180);

function readEnv() {
  const envPath = join(root, ".env");
  if (!existsSync(envPath)) return {};
  return Object.fromEntries(
    readFileSync(envPath, "utf8")
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter((line) => line && !line.startsWith("#") && line.includes("="))
      .map((line) => {
        const index = line.indexOf("=");
        const key = line.slice(0, index).trim();
        const value = line.slice(index + 1).trim().replace(/^["']|["']$/g, "");
        return [key, value];
      })
  );
}

function contentType(pathname) {
  return {
    ".css": "text/css; charset=utf-8",
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".md": "text/markdown; charset=utf-8",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".webp": "image/webp"
  }[extname(pathname).toLowerCase()] || "application/octet-stream";
}

createServer((request, response) => {
  const url = new URL(request.url || "/", `http://${request.headers.host}`);

  if (url.pathname === "/runtime-config.js") {
    const env = readEnv();
    const jusoApiKey = env.JUSO_API_KEY || "";
    response.writeHead(200, {
      "Content-Type": "application/javascript; charset=utf-8",
      "Cache-Control": "no-store"
    });
    response.end(`window.ANSIMBODO_CONFIG = ${JSON.stringify({ jusoApiKey })};`);
    return;
  }

  const pathname = decodeURIComponent(url.pathname === "/" ? "/index.html" : url.pathname);
  const filePath = normalize(join(root, pathname));
  if (!filePath.startsWith(root) || !existsSync(filePath)) {
    response.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" });
    response.end("Not found");
    return;
  }

  response.writeHead(200, { "Content-Type": contentType(filePath) });
  createReadStream(filePath).pipe(response);
}).listen(port, () => {
  console.log(`MVP server: http://localhost:${port}/`);
});
