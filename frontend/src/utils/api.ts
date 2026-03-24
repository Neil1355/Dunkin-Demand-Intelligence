// Always prioritize the environment variable, then the Render production URL
const API_BASE =
  import.meta.env.VITE_API_URL || "https://dunkin-demand-intelligence.onrender.com/api/v1";

async function fetchWithCredentials(path: string, options: RequestInit = {}) {
  return fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    credentials: "include",
    mode: "cors",
  });
}

export async function apiFetch(path: string, options: RequestInit = {}) {
  // Ensure path starts with /
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;

  let res = await fetchWithCredentials(normalizedPath, options);

  // Attempt one refresh for expired/rotated sessions, then retry original request once.
  if (res.status === 401 && !normalizedPath.startsWith('/auth/')) {
    const refreshRes = await fetchWithCredentials('/auth/refresh', { method: 'POST' });
    if (refreshRes.ok) {
      res = await fetchWithCredentials(normalizedPath, options);
    }
  }

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