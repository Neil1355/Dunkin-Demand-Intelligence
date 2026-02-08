// Always prioritize the environment variable, then the Render production URL
const API_BASE =
  import.meta.env.VITE_API_URL || "https://dunkin-demand-intelligence.onrender.com/api/v1";

export async function apiFetch(path: string, options: RequestInit = {}) {
  // Ensure path starts with /
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  
  const res = await fetch(`${API_BASE}${normalizedPath}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    // Required for set-cookie headers to work across domains
    credentials: "include", 
    mode: 'cors'
  });

  if (!res.ok) {
    const text = await res.text();
    // Try to parse JSON error message if available
    try {
      const jsonError = JSON.parse(text);
      throw new Error(jsonError.message || jsonError.error || "API error");
    } catch {
      throw new Error(text || `API Error ${res.status}`);
    }
  }

  return res.json();
}