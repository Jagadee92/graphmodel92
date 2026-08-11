import { useState } from "react";
import { api } from "../services/api";

export default function ApplyModal({ job, close }) {
  const [note, setNote] = useState("");
  const [result, setResult] = useState("");
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      const data = await api.apply(job.id, { cover_note: note });
      setResult(`${data.message}. Email: ${data.email_notification}`);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="modal-backdrop">
      <div className="modal card">
        <button className="close" onClick={close}>×</button>
        <h2>Apply to {job.title}</h2>
        <p className="muted">{job.company}</p>
        {error && <div className="alert error">{error}</div>}
        {result && <div className="alert success">{result}</div>}
        {!result && (
          <form onSubmit={submit}>
            <label>Cover note<textarea value={note} onChange={e => setNote(e.target.value)} placeholder="Tell the company why you are interested."/></label>
            <button className="primary">Submit application</button>
          </form>
        )}
      </div>
    </div>
  );
}
