import { useState } from "react";
import Inbox from "./pages/Inbox.jsx";
import ConversationView from "./pages/ConversationView.jsx";
import Contacts from "./pages/Contacts.jsx";
import Metrics from "./pages/Metrics.jsx";

const TABS = [
  ["inbox", "Inbox"],
  ["contacts", "Contacts"],
  ["metrics", "Metrics"],
];

export default function App() {
  const [page, setPage] = useState("inbox");
  const [openId, setOpenId] = useState(null);

  const go = (next) => { setOpenId(null); setPage(next); };

  return (
    <div className="app">
      <header>
        <h1>Nebula Desk · Support</h1>
        <nav>
          {TABS.map(([key, label]) => (
            <button key={key} className={page === key && !openId ? "active" : ""} onClick={() => go(key)}>
              {label}
            </button>
          ))}
        </nav>
        <span className="user">Signed in as Demo Agent</span>
      </header>
      <main>
        {openId ? (
          <ConversationView id={openId} onBack={() => setOpenId(null)} />
        ) : page === "inbox" ? (
          <Inbox onOpen={setOpenId} />
        ) : page === "contacts" ? (
          <Contacts />
        ) : (
          <Metrics />
        )}
      </main>
    </div>
  );
}
