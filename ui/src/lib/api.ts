// API service for connecting to the backend

// Resolve base URL:
// - production: set VITE_API_BASE to your Railway backend (e.g. https://penguins-backend.up.railway.app)
// - local dev: falls back to http://localhost:8000
const RESOLVED_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined)?.trim() ||
  (typeof window !== "undefined" && window.location.hostname === "localhost"
    ? "http://localhost:8000"
    : "http://localhost:8000"); // change if you use a different default

const API_BASE = RESOLVED_BASE.replace(/\/+$/, ""); // trim trailing slashes

// Types
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

// Helper for JSON fetch with better errors
async function fetchJSON(input: string, init?: RequestInit) {
  const res = await fetch(input, init);
  let payload: any = null;

  try {
    // Try to parse JSON body no matter what
    payload = await res.json();
  } catch {
    // swallow JSON parse errors; payload remains null
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

// API functions
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
