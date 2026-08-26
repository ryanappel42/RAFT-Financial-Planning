const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const ACCESS_CODE = import.meta.env.VITE_ACCESS_CODE || null;

function headers() {
  const h = { "Content-Type": "application/json" };
  if (ACCESS_CODE) h["x-access-code"] = ACCESS_CODE;
  return h;
}

export async function sendMessage({ sessionId, message, mode, clientId }) {
  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({
      session_id: sessionId,
      message,
      mode,
      client_id: clientId || null,
    }),
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }

  return res.json(); // { session_id, reply }
}

export async function fetchClients() {
  const res = await fetch(`${API_URL}/clients`, { headers: headers() });
  if (!res.ok) throw new Error(`Failed to load clients (${res.status})`);
  return res.json(); // { client_id: name }
}