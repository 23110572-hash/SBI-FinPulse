// API client — thin fetch wrapper around the FastAPI backend.
const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const STAFF_TOKEN = process.env.NEXT_PUBLIC_STAFF_TOKEN || "";

async function request(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  // attach staff bearer token when configured (no-op in open demo mode)
  if (STAFF_TOKEN && !headers.Authorization) {
    headers.Authorization = `Bearer ${STAFF_TOKEN}`;
  }
  // `signal` (AbortController) is honoured if passed via options.
  const res = await fetch(`${BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch (_) {}
    throw new Error(detail);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  base: BASE,

  // customers
  listCustomers: (opts) => request("/api/customers", opts),
  getCustomer: (id, opts) => request(`/api/customers/${id}`, opts),
  getTransactions: (id, limit = 200, opts) =>
    request(`/api/customers/${id}/transactions?limit=${limit}`, opts),

  // analysis
  getSteps: (opts) => request("/api/analysis/steps", opts),
  getAnalysis: (id, opts) => request(`/api/analysis/${id}`, opts),
  analyze: (id) => request(`/api/analyze/${id}`, { method: "POST" }),
  streamUrl: (id) => `${BASE}/api/analyze/${id}/stream`,

  // chat
  chat: (payload) => request("/api/chat", { method: "POST", body: JSON.stringify(payload) }),
  chatHistory: (id, opts) => request(`/api/chat/history/${id}`, opts),

  // insights + wellness
  getInsights: (id, opts) => request(`/api/insights/${id}`, opts),
  getWellness: (id, opts) => request(`/api/wellness/${id}`, opts),

  // nudges
  listNudges: (status, opts) =>
    request(`/api/nudges${status ? `?status=${status}` : ""}`, opts),
  customerNudges: (id, opts) => request(`/api/nudges/${id}`, opts),
  approveNudge: (id) => request(`/api/nudges/${id}/approve`, { method: "PUT" }),
  rejectNudge: (id) => request(`/api/nudges/${id}/reject`, { method: "PUT" }),
  sendNudge: (id) => request(`/api/nudges/${id}/send`, { method: "PUT" }),
  nudgeDeliveries: (id, opts) => request(`/api/nudges/${id}/deliveries`, opts),

  // consent (DPDP)
  getConsent: (id, opts) => request(`/api/consent/${id}`, opts),
  grantConsent: (id, body = {}) =>
    request(`/api/consent/${id}/grant`, { method: "POST", body: JSON.stringify(body) }),
  revokeConsent: (id, body = {}) =>
    request(`/api/consent/${id}/revoke`, { method: "POST", body: JSON.stringify(body) }),

  // proactive engagement
  engagementEvents: (id, opts) => request(`/api/engagement/events/${id}`, opts),
  allEngagementEvents: (limit = 50, opts) =>
    request(`/api/engagement/events?limit=${limit}`, opts),
  runScan: () => request("/api/engagement/scan", { method: "POST" }),
  processCustomer: (id, body = {}) =>
    request(`/api/engagement/process/${id}`, { method: "POST", body: JSON.stringify(body) }),
  auditLog: (id, opts) =>
    request(`/api/engagement/audit${id ? `?customer_id=${id}` : ""}`, opts),

  // health
  health: (opts) => request("/api/health", opts),

  // dashboard
  dashboardStats: (opts) => request("/api/dashboard/stats", opts),
  dashboardActivity: (opts) => request("/api/dashboard/activity", opts),
  dashboardAnalytics: (opts) => request("/api/dashboard/analytics", opts),
};
