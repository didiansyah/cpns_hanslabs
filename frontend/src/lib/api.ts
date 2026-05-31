const BASE = "/api";

export async function api(path: string, options: RequestInit = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("cpns_token") : null;
  const headers: Record<string, string> = { "Content-Type": "application/json", ...(options.headers as Record<string, string> || {}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  let url = `${BASE}${path}`;
  if (!url.includes("?") && !url.endsWith("/")) url += "/";
  const res = await fetch(url, { ...options, headers, redirect: "follow" });
  return res.json();
}

export const apiGet = (path: string) => api(path);
export const apiPost = (path: string, body: any) => api(path, { method: "POST", body: JSON.stringify(body) });
export const apiPut = (path: string, body: any) => api(path, { method: "PUT", body: JSON.stringify(body) });
