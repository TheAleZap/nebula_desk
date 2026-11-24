import { useEffect, useState } from "react";
import { api } from "../api.js";

const percent = (value) => (value == null ? "–" : `${Math.round(value * 100)}%`);

export default function Metrics() {
  const [support, setSupport] = useState(null);
  const [ai, setAi] = useState(null);
  const [error, setError] = useState("");
  const [aiError, setAiError] = useState("");

  useEffect(() => {
    api.supportMetrics().then(setSupport).catch((e) => setError(e.message));
    // Called on the Intelligence API directly: if it is down, only this panel degrades.
    api.aiStats().then(setAi).catch(() => setAiError("AI statistics are unavailable right now."));
  }, []);

  return (
    <section>
      {error && <p className="error">{error}</p>}
      {support && (
        <div className="cards">
          <div className="card stat"><span>{support.total_conversations}</span>Conversations</div>
          <div className="card stat"><span>{support.by_status.open}</span>Open</div>
          <div className="card stat"><span>{support.by_status.pending}</span>Pending</div>
          <div className="card stat"><span>{support.by_status.resolved}</span>Resolved</div>
          <div className="card stat"><span>{support.by_priority.high}</span>High priority</div>
          <div className="card stat">
            <span>{support.avg_first_response_minutes ?? "–"}</span>Avg first response (min)
          </div>
          <div className="card stat">
            <span>{percent(support.ai_suggestion_acceptance_rate)}</span>AI suggestion acceptance
          </div>
        </div>
      )}
      <h3>AI analysis</h3>
      {aiError && <p className="error">{aiError}</p>}
      {ai && (
        <div className="cards">
          <div className="card stat"><span>{ai.total_analyses}</span>Messages analyzed</div>
          {Object.entries(ai.by_intent).map(([intent, count]) => (
            <div key={intent} className="card stat"><span>{count}</span>{intent}</div>
          ))}
          <div className="card stat"><span>{ai.llm_enabled ? "On" : "Off"}</span>LLM replies</div>
        </div>
      )}
    </section>
  );
}
