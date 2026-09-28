const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const { headers, ...restOptions } = options;
  const response = await fetch(`${API}${path}`, {
    ...restOptions,
    headers: {
      "Content-Type": "application/json",
      ...(headers || {}),
    },
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    let msg = "Request failed";
    if (typeof data.detail === "string") {
      msg = data.detail;
    } else if (Array.isArray(data.detail)) {
      msg = data.detail.map((err) => `${err.loc?.slice(1).join(" ") || "field"}: ${err.msg}`).join("; ");
    }
    throw new Error(msg);
  }
  return data;
}

export function register(body) {
  return request("/auth/register", { method: "POST", body: JSON.stringify(body) });
}

export function login(body) {
  return request("/auth/login", { method: "POST", body: JSON.stringify(body) });
}

export function getInventory(token) {
  return request("/inventory", { headers: { Authorization: `Bearer ${token}` } });
}

export function addFood(token, body) {
  return request("/inventory", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(body),
  });
}

export function deleteFood(token, id) {
  return request(`/inventory/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${token}` },
  });
}

// ── M2: Freshness Analysis ────────────────────────────────────────────────

export async function analyzeFoodImage(token, file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API}/analysis/predict`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
    // Do NOT set Content-Type — browser sets it automatically with boundary
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    let msg = "Analysis failed";
    if (typeof data.detail === "string") msg = data.detail;
    else if (Array.isArray(data.detail))
      msg = data.detail.map((e) => e.msg).join("; ");
    throw new Error(msg);
  }
  return data;
}

export function getAnalysisHistory(token) {
  return request("/analysis/history", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function downloadAnalysisReport(token, analysisId) {
  const response = await fetch(`${API}/analysis/${analysisId}/report`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    let msg = "Failed to download report";
    if (typeof data.detail === "string") msg = data.detail;
    throw new Error(msg);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `FreshGuard_Report_${analysisId}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

// ── M3: Shelf-life, storage, and analytics ───────────────────────────────


export function createShelfLifePrediction(token, body) {
  return request("/m3/shelf-life/predict", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(body),
  });
}

export function getShelfLifeHistory(token) {
  return request("/m3/shelf-life/history", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function getM3Analytics(token, days = 7) {
  return request(`/m3/analytics?days=${days}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function getM3Recommendations(token, predictionId) {
  return request(`/m3/recommendations/${predictionId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

// C2: Storage condition history
export function getStorageConditions(token) {
  return request("/m3/storage-conditions", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

// C3: Expiring-soon inventory items (days=1–365, default 7)
export function getExpiringSoon(token, days = 7) {
  return request(`/inventory/expiring-soon?days=${days}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}
