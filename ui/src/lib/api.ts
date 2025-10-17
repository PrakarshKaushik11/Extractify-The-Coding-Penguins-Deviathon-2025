// API service for connecting to the backend

// Resolve base URL:
// - production: use VITE_API_URL (set to https://extractify-80dl.onrender.com in Render)
// - local dev: fallback to http://localhost:8000 ONLY if no env var is found
// ui/src/lib/api.ts — ensure API_BASE points to /api on deployed host
const raw = (import.meta.env.VITE_API_URL as string | undefined)?.trim() ||
            (typeof window !== "undefined" && window.location.hostname === "localhost"
               ? "http://localhost:8000"
               : "https://extractify-80dl.onrender.com");

// ensure calls go to /api prefix
export const API_BASE = raw.replace(/\/+$/, "") + "/api";


// ---- Types ----
export interface CrawlRequest {
  domain: string;
  keywords: string[];
  max_pages: number;
  max_depth: number;
}

export interface ExtractRequest {
  keywords?: string[];
  target?: string;
  min_score?: number;
}

// ---- Helper for JSON fetch with better errors ----
async function fetchJSON(input: string, init?: RequestInit) {
  const res = await fetch(input, init);
  let payload: any = null;

  try {
    payload = await res.json();
  } catch {
    // ignore parse errors, payload stays null
  }

  if (!res.ok) {
    const detail =
      payload?.detail ||
      payload?.message ||
      `${res.status} ${res.statusText}` ||
      "Request failed";
    throw new Error(detail);
  }
  return payload;
}

// ---- API functions ----
export const api = {
  // Health check
  health: async () => fetchJSON(`${API_BASE}/health`),

  // Crawl a domain
  crawl: async (payload: CrawlRequest) =>
    fetchJSON(`${API_BASE}/crawl`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  // Extract entities
  extract: async (payload: ExtractRequest = {}) =>
    fetchJSON(`${API_BASE}/extract`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  // Get results
  getResults: async () => fetchJSON(`${API_BASE}/results`),

  // Crawl and extract in one call
  crawlAndExtract: async (payload: CrawlRequest) =>
    fetchJSON(`${API_BASE}/crawl-and-extract`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
};

export default api;
