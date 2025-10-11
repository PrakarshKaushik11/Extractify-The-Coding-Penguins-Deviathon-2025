// API service for connecting to the backend

// Base API URL - adjust this based on where your backend is running
const API_BASE_URL = 'http://localhost:8000';

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

// API functions
export const api = {
  // Health check
  health: async () => {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  },

  // Crawl a domain
  crawl: async (payload: CrawlRequest) => {
    const response = await fetch(`${API_BASE_URL}/crawl`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to crawl domain');
    }
    
    return response.json();
  },

  // Extract entities
  extract: async (payload: ExtractRequest = {}) => {
    const response = await fetch(`${API_BASE_URL}/extract`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to extract entities');
    }
    
    return response.json();
  },

  // Get results
  getResults: async () => {
    const response = await fetch(`${API_BASE_URL}/results`);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get results');
    }
    
    return response.json();
  },

  // Crawl and extract in one call
  crawlAndExtract: async (payload: CrawlRequest) => {
    const response = await fetch(`${API_BASE_URL}/crawl-and-extract`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to crawl and extract');
    }
    
    return response.json();
  },
};

export default api;