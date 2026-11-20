import { useEffect, useState } from "react";
import { api } from "../api.js";

const EMPTY = { name: "", email: "" };

export default function Contacts() {
  const [contacts, setContacts] = useState([]);
  const [form, setForm] = useState(EMPTY);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");

  const load = async () => {
    try { setContacts(await api.listContacts()); setError(""); } catch (e) { setError(e.message); }
  };
  useEffect(() => { load(); }, []);

  const save = async (event) => {
    event.preventDefault();
    try {
      if (editingId) await api.updateContact(editingId, form);
      else await api.createContact(form);
      setForm(EMPTY);
      setEditingId(null);
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  const remove = async (id) => {
    try { await api.deleteContact(id); load(); } catch (e) { setError(e.message); }
  };

  return (
    <section>
      {error && <p className="error">{error}</p>}
      <form className="card form inline" onSubmit={save}>
        <input required placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <input required type="email" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <button className="primary" type="submit">{editingId ? "Save" : "Add contact"}</button>
        {editingId && <button type="button" onClick={() => { setEditingId(null); setForm(EMPTY); }}>Cancel</button>}
      </form>
      <table>
        <thead><tr><th>Name</th><th>Email</th><th></th></tr></thead>
        <tbody>
          {contacts.map((c) => (
            <tr key={c.id}>
              <td>{c.name}</td>
              <td>{c.email}</td>
              <td className="actions">
                <button onClick={() => { setEditingId(c.id); setForm({ name: c.name, email: c.email }); }}>Edit</button>
                <button className="danger" onClick={() => remove(c.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
