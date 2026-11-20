import { useEffect, useState } from "react";
import { api } from "../api.js";

const EMPTY_FORM = { contact_id: "", subject: "", channel: "chat", first_message: "" };

export default function Inbox({ onOpen }) {
  const [conversations, setConversations] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [filters, setFilters] = useState({ status: "", q: "" });
  const [form, setForm] = useState(EMPTY_FORM);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      setConversations(await api.listConversations(filters));
      setContacts(await api.listContacts());
      setError("");
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [filters.status]); // eslint-disable-line react-hooks/exhaustive-deps

  const simulate = async () => {
    try {
      const result = await api.simulate();
      setNotice(`New ${result.conversation.channel} message from ${result.conversation.contact.name}.`);
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  const create = async (event) => {
    event.preventDefault();
    try {
      await api.createConversation({ ...form, contact_id: Number(form.contact_id) });
      setForm(EMPTY_FORM);
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <section>
      <div className="toolbar">
        <select value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
          <option value="">All statuses</option>
          <option value="open">Open</option>
          <option value="pending">Pending</option>
          <option value="resolved">Resolved</option>
        </select>
        <input
          placeholder="Search subject…"
          value={filters.q}
          onChange={(e) => setFilters({ ...filters, q: e.target.value })}
          onKeyDown={(e) => e.key === "Enter" && load()}
        />
        <button onClick={load}>Search</button>
        <button className="primary" onClick={simulate}>Simulate incoming message</button>
      </div>

      {error && <p className="error">{error}</p>}
      {notice && <p className="notice">{notice}</p>}
      {loading && <p className="muted">Loading…</p>}

      <table>
        <thead>
          <tr><th>Subject</th><th>Contact</th><th>Channel</th><th>Status</th><th>Agent</th></tr>
        </thead>
        <tbody>
          {conversations.map((c) => (
            <tr key={c.id} onClick={() => onOpen(c.id)} className="clickable">
              <td>{c.subject}</td>
              <td>{c.contact.name}</td>
              <td>{c.channel}</td>
              <td><span className={`badge ${c.status}`}>{c.status}</span></td>
              <td>{c.agent?.name || "Unassigned"}</td>
            </tr>
          ))}
          {!loading && conversations.length === 0 && (
            <tr><td colSpan="5" className="muted">No conversations yet. Click "Simulate incoming message".</td></tr>
          )}
        </tbody>
      </table>

      <h3>New conversation</h3>
      <form className="card form" onSubmit={create}>
        <select required value={form.contact_id} onChange={(e) => setForm({ ...form, contact_id: e.target.value })}>
          <option value="">Choose contact…</option>
          {contacts.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <input required placeholder="Subject" value={form.subject} onChange={(e) => setForm({ ...form, subject: e.target.value })} />
        <select value={form.channel} onChange={(e) => setForm({ ...form, channel: e.target.value })}>
          <option value="chat">Chat</option>
          <option value="email">Email</option>
          <option value="whatsapp">WhatsApp</option>
        </select>
        <textarea placeholder="First customer message (optional)" value={form.first_message} onChange={(e) => setForm({ ...form, first_message: e.target.value })} />
        <button className="primary" type="submit">Create</button>
      </form>
    </section>
  );
}
