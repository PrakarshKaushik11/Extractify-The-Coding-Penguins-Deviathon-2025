// API service for connecting to the backend

// Resolve base URL:
// - local dev: http://localhost:8001 (when running vite locally)
// - production: prefer VITE_API_URL if provided; otherwise use same-origin with Vercel rewrites
const rawEnv = (import.meta.env.VITE_API_URL as string | undefined)?.trim();
const isLocalhost = typeof window !== "undefined" && window.location.hostname === "localhost";
const raw = rawEnv && rawEnv.length > 0
  ? rawEnv
  : (isLocalhost ? "http://localhost:8001" : ""); // same-origin in prod to leverage Vercel rewrites

// ensure calls go to /api prefix
export const API_BASE = (raw || "").replace(/\/+$/, "") + "/api";
if (typeof window !== "undefined") {
  // Helpful for debugging which base is used
  console.info("API_BASE:", API_BASE);
}


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

// ---- Helper for JSON fetch with better errors and retry logic ----
async function fetchJSON(input: string, init?: RequestInit, retries = 2) {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const res = await fetch(input, {
        ...init
        // No timeout signal
      });
      
      let payload: any = null;

      try {
        const text = await res.text();
        payload = text ? JSON.parse(text) : null;
      } catch (parseError) {
        // ignore parse errors, payload stays null
        console.warn("Failed to parse response:", parseError);
      }

      if (!res.ok) {
        const detail =
          payload?.detail ||
          payload?.message ||
          (res.status === 404 ? "Endpoint not found. Make sure the backend API is running." :
           res.status === 500 ? "Internal server error. Check backend logs." :
           res.status === 503 ? "Service unavailable. Backend may be starting up." :
           `${res.status} ${res.statusText}`) ||
          "Request failed";
        throw new Error(detail);
      }
      
      return payload;
    } catch (error) {
      lastError = error as Error;
      
      // Don't retry on client errors (400-499)
      if (error instanceof Error && error.message.includes("404")) {
        throw error;
      }
      
      // If this isn't the last attempt, wait before retrying
      if (attempt < retries) {
        await new Promise(resolve => setTimeout(resolve, 1000 * (attempt + 1))); // Exponential backoff
      }
    }
  }

  throw new Error(lastError?.message || "Network request failed after retries");
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
