/**
 * Thin wrapper around the AquaSense backend REST API.
 * Change API_BASE if the backend isn't running on localhost:5000
 * (e.g. point it at your deployed Render/Railway URL).
 */
const API_BASE = window.AQUASENSE_API_BASE || "http://localhost:5000/api";

async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`GET ${path} failed: ${res.status}`);
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body || {})
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `POST ${path} failed: ${res.status}`);
  }
  return res.json();
}

async function apiDelete(path) {
  const res = await fetch(`${API_BASE}${path}`, { method: "DELETE" });
  if (!res.ok) throw new Error(`DELETE ${path} failed: ${res.status}`);
  return res.json();
}

const AquaAPI = {
  health: () => apiGet("/health"),
  listEntries: () => apiGet("/entries"),
  addEntry: (activity, litres, date) => apiPost("/entries", { activity, litres, date }),
  clearEntries: () => apiDelete("/entries"),
  stats: () => apiGet("/stats"),
  tip: (activity, level) => apiGet(`/tips?activity=${encodeURIComponent(activity)}&level=${encodeURIComponent(level)}`),
  seed: () => apiPost("/seed")
};
