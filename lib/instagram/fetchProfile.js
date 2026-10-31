import { headers as nextHeaders } from "next/headers";

const IG_BASE = "https://www.instagram.com";

export async function fetchProfileHtml(username) {
  const clean = String(username || "").trim().replace(/^@+/, "");
  if (!clean) {
    throw new Error("Username is required");
  }

  const url = `${IG_BASE}/${encodeURIComponent(clean)}/`;

  const headers = {
    "user-agent":
      "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
    accept:
      "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9",
    "upgrade-insecure-requests": "1"
  };

  // Forward a minimal set of headers if helpful (not critical)
  try {
    const incoming = nextHeaders();
    const lang = incoming.get("accept-language");
    if (lang) headers["accept-language"] = lang;
  } catch {
    // ignore in non-request contexts
  }

  const res = await fetch(url, {
    headers,
    redirect: "follow"
  });

  if (!res.ok) {
    throw new Error(`Instagram returned HTTP ${res.status}`);
  }

  const text = await res.text();
  if (!text) {
    throw new Error("Empty response body from Instagram");
  }
  return text;
}

