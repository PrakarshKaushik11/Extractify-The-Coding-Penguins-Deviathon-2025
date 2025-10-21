// API service for connecting to the backend

// Resolve API base dynamically at runtime with fallback logic:
// - In browser on localhost: use http://localhost:8001/api (dev)
// - In browser in production: try same-origin /api first (Vercel rewrites), else fall back to VITE_API_URL or Render URL
// - In non-browser/SSR: use VITE_API_URL or Render URL
const rawEnv = (import.meta.env.VITE_API_URL as string | undefined)?.trim();
const isBrowser = typeof window !== "undefined";
const isLocalhost = isBrowser && window.location.hostname === "localhost";
const RENDER_BACKEND = "https://extractify-backend.onrender.com";

let resolvedBasePromise: Promise<string> | null = null;

async function resolveApiBase(): Promise<string> {
  if (resolvedBasePromise) return resolvedBasePromise;
  resolvedBasePromise = (async () => {
    if (isBrowser) {
      if (isLocalhost) {
        // Dev server
        return ((rawEnv && rawEnv.length > 0 ? rawEnv : "http://localhost:8001").replace(/\/+$/, "")) + "/api";
      }
      // Production in browser: prefer same-origin /api (rewrites)
      try {
        const res = await fetch("/api/health", { method: "GET" });
        if (res.ok) {
          console.info("API_BASE: /api (via rewrite)");
          return "/api";
        }
      } catch {
        // ignore and fall back
      }
      const fallback = (rawEnv && rawEnv.length > 0 ? rawEnv : RENDER_BACKEND).replace(/\/+$/, "") + "/api";
      console.info("API_BASE fallback:", fallback);
      return fallback;
    }
    // Non-browser contexts (SSR/tests)
    const base = (rawEnv || RENDER_BACKEND).replace(/\/+$/, "") + "/api";
    return base;
  })();
  return resolvedBasePromise;
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
      const primaryBase = await resolveApiBase();
      const fallbackBase = ((rawEnv && rawEnv.length > 0 ? rawEnv : RENDER_BACKEND).replace(/\/+$/, "")) + "/api";

      const buildUrl = (base: string) => input.startsWith("http") ? input : `${base}${input.startsWith("/") ? input : "/" + input}`;

      // Attempt 1: primary base
      const attemptOnce = async (base: string) => {
        const url = buildUrl(base);
        const res = await fetch(url, {
          ...init
        });

        const contentType = res.headers.get("content-type") || "";
        const text = await res.text();

        let payload: any = null;
        try {
          payload = text ? JSON.parse(text) : null;
        } catch (parseError) {
          // HTML or non-JSON response
          if (contentType.includes("text/html") || (text && text.trim().startsWith("<"))) {
            throw new Error(res.ok ? "HTML response instead of JSON" : `${res.status} ${res.statusText}`);
          }
          // keep payload null; error will be thrown by !res.ok
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
      };

      try {
        return await attemptOnce(primaryBase);
      } catch (e) {
        // If primary was same-origin '/api', try fallback once before retry loop
        if (primaryBase === "/api") {
          try {
            const data = await attemptOnce(fallbackBase);
            console.info("API_BASE switched to fallback for this request:", fallbackBase);
            return data;
          } catch (e2) {
            lastError = e2 as Error;
          }
        } else {
          lastError = e as Error;
        }
      }
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
  health: async () => fetchJSON(`/health`),

  // Crawl a domain
  crawl: async (payload: CrawlRequest) =>
    fetchJSON(`/crawl`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  // Extract entities
  extract: async (payload: ExtractRequest = {}) =>
    fetchJSON(`/extract`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),

  // Get results
  getResults: async () => fetchJSON(`/results`),

  // Crawl and extract in one call
  crawlAndExtract: async (payload: CrawlRequest) =>
    fetchJSON(`/crawl-and-extract`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }),
};

export default api;
