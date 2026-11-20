import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function ConversationView({ id, onBack }) {
  const [conversation, setConversation] = useState(null);
  const [agents, setAgents] = useState([]);
  const [reply, setReply] = useState("");
  const [error, setError] = useState("");

  const load = async () => {
    try {
      setConversation(await api.getConversation(id));
      setAgents(await api.listAgents());
      setError("");
    } catch (e) {
      setError(e.message);
    }
  };

  useEffect(() => { load(); }, [id]); // eslint-disable-line react-hooks/exhaustive-deps

  const update = async (data) => {
    try { setConversation(await api.updateConversation(id, data)); } catch (e) { setError(e.message); }
  };

  const send = async (event) => {
    event.preventDefault();
    try {
      await api.addMessage(id, { sender: "agent", body: reply });
      setReply("");
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  const remove = async () => {
    if (!window.confirm("Delete this conversation?")) return;
    try { await api.deleteConversation(id); onBack(); } catch (e) { setError(e.message); }
  };

  if (!conversation) return <p className="muted">{error || "Loading…"}</p>;

  return (
    <section className="detail">
      <button onClick={onBack}>← Back to inbox</button>
      {error && <p className="error">{error}</p>}
      <div className="columns">
        <div>
          <h2>{conversation.subject}</h2>
          <p className="muted">
            {conversation.contact.name} · {conversation.contact.email} · via {conversation.channel}
          </p>
          <div className="toolbar">
            <label>Status{" "}
              <select value={conversation.status} onChange={(e) => update({ status: e.target.value })}>
                <option value="open">Open</option>
                <option value="pending">Pending</option>
                <option value="resolved">Resolved</option>
              </select>
            </label>
            <label>Agent{" "}
              <select
                value={conversation.assigned_agent_id ?? ""}
                onChange={(e) => update(e.target.value ? { assigned_agent_id: Number(e.target.value) } : { unassign: true })}
              >
                <option value="">Unassigned</option>
                {agents.map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
              </select>
            </label>
            <button className="danger" onClick={remove}>Delete</button>
          </div>

          <div className="thread">
            {conversation.messages.map((m) => (
              <div key={m.id} className={`message ${m.sender}`}>
                <small>{m.sender}</small>
                <p>{m.body}</p>
              </div>
            ))}
          </div>

          <form className="card form" onSubmit={send}>
            <textarea required placeholder="Write a reply…" value={reply}
              onChange={(e) => { setReply(e.target.value); }} />
            <button className="primary" type="submit">Send reply</button>
          </form>
        </div>
      </div>
    </section>
  );
}
