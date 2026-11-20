// All calls to the two services go through here.
// Cold starts: Azure may answer 503 (or not answer) while a container or a paused
// database wakes up. We retry a few times, then show a clear "starting up" message.

const config = window.NEBULA_CONFIG || {};
const CONVERSATION = config.conversationApiUrl;
const INTELLIGENCE = config.intelligenceApiUrl;

const RETRIES = 3;
const RETRY_DELAY_MS = 4000;
const TIMEOUT_MS = 35000;

export const STARTING_UP =
  "The service is starting up (it scales to zero when idle). Please try again in a few seconds.";

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function request(base, path, options = {}) {
  for (let attempt = 0; attempt <= RETRIES; attempt++) {
    let response;
    try {
      response = await fetch(base + path, {
        ...options,
        headers: { "Content-Type": "application/json" },
        signal: AbortSignal.timeout(TIMEOUT_MS),
      });
    } catch {
      if (attempt < RETRIES) { await sleep(RETRY_DELAY_MS); continue; }
      throw new Error(STARTING_UP);
    }
    if (response.status === 204) return null;
    const body = await response.json().catch(() => null);
    if (response.ok) return body;
    // A 503 with our own JSON "detail" is a designed message (e.g. AI unavailable): show it.
    if (response.status === 503 && body?.detail) throw new Error(body.detail);
    // A 503 without it is Azure's cold-start answer: retry.
    if (response.status === 503 && attempt < RETRIES) { await sleep(RETRY_DELAY_MS); continue; }
    if (response.status === 503) throw new Error(STARTING_UP);
    const detail = Array.isArray(body?.detail)
      ? body.detail.map((d) => `${d.loc?.slice(-1)[0]}: ${d.msg}`).join(", ")
      : body?.detail;
    throw new Error(detail || `Request failed (${response.status})`);
  }
}

const json = (data) => JSON.stringify(data);

export const api = {
  // Conversation API
  listConversations: (params = {}) => {
    const query = new URLSearchParams(Object.entries(params).filter(([, v]) => v !== "" && v != null));
    return request(CONVERSATION, `/conversations?${query}`);
  },
  getConversation: (id) => request(CONVERSATION, `/conversations/${id}`),
  createConversation: (data) => request(CONVERSATION, "/conversations", { method: "POST", body: json(data) }),
  updateConversation: (id, data) => request(CONVERSATION, `/conversations/${id}`, { method: "PUT", body: json(data) }),
  deleteConversation: (id) => request(CONVERSATION, `/conversations/${id}`, { method: "DELETE" }),
  addMessage: (id, data) => request(CONVERSATION, `/conversations/${id}/messages`, { method: "POST", body: json(data) }),
  analyze: (id) => request(CONVERSATION, `/conversations/${id}/analyze`, { method: "POST" }),
  simulate: () => request(CONVERSATION, "/conversations/simulate", { method: "POST" }),
  listContacts: () => request(CONVERSATION, "/contacts"),
  createContact: (data) => request(CONVERSATION, "/contacts", { method: "POST", body: json(data) }),
  updateContact: (id, data) => request(CONVERSATION, `/contacts/${id}`, { method: "PUT", body: json(data) }),
  deleteContact: (id) => request(CONVERSATION, `/contacts/${id}`, { method: "DELETE" }),
  listAgents: () => request(CONVERSATION, "/agents"),
  supportMetrics: () => request(CONVERSATION, "/metrics"),
  // Intelligence API (called directly from the browser)
  aiStats: () => request(INTELLIGENCE, "/stats"),
};
