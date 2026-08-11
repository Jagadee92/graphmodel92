import { useEffect, useState } from "react";
import { api } from "../services/api";

export default function Applications() {
  const [items, setItems] = useState([]);
  useEffect(() => { api.applications().then(setItems).catch(() => setItems([])); }, []);

  return (
    <main className="container">
      <span className="eyebrow">APPLICATION TRACKING</span>
      <h1>My applications</h1>
      <div className="grid">
        {items.map(a => (
          <div className="card" key={a.id}>
            <div className="job-top">
              <div><h3>{a.job_title}</h3><p className="muted">{a.company}</p></div>
              <span className="badge">{a.status}</span>
            </div>
            <p>Submitted: {a.submitted_at || "—"}</p>
            <p>Email notification: <strong>{a.email_notification}</strong></p>
          </div>
        ))}
      </div>
      {!items.length && <div className="card empty">No applications yet.</div>}
    </main>
  );
}
