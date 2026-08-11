import { useEffect, useState } from "react";
import { api } from "../services/api";

export default function Profile({ profile, refresh }) {
  const [form, setForm] = useState(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (profile) {
      setForm({
        name: profile.candidate.name,
        location: profile.candidate.location,
        bio: profile.candidate.bio || "",
        skills: profile.skills.join(", ")
      });
    }
  }, [profile]);

  async function save(e) {
    e.preventDefault();
    const updated = await api.updateMe({
      name: form.name,
      location: form.location,
      bio: form.bio,
      skills: form.skills.split(",").map(x => x.trim()).filter(Boolean)
    });
    refresh(updated);
    setMessage("Profile updated successfully.");
  }

  if (!form) return <main className="container"><div className="card">Loading...</div></main>;

  return (
    <main className="container">
      <span className="eyebrow">CANDIDATE PROFILE</span>
      <h1>{profile.candidate.name}</h1>

      <div className="two-col">
        <form className="card" onSubmit={save}>
          <h2>Profile details</h2>
          {message && <div className="alert success">{message}</div>}
          <label>Name<input value={form.name} onChange={e => setForm({...form,name:e.target.value})}/></label>
          <label>Email<input disabled value={profile.candidate.email}/></label>
          <label>Location<input value={form.location} onChange={e => setForm({...form,location:e.target.value})}/></label>
          <label>Skills<input value={form.skills} onChange={e => setForm({...form,skills:e.target.value})}/></label>
          <label>Bio<textarea value={form.bio} onChange={e => setForm({...form,bio:e.target.value})}/></label>
          <button className="primary">Save changes</button>
        </form>

        <div>
          <div className="card">
            <h2>Projects</h2>
            {profile.projects.map(p => (
              <div className="list-item" key={p.id}>
                <strong>{p.name}</strong><p>{p.description}</p>
              </div>
            ))}
            {!profile.projects.length && <p className="muted">No projects yet.</p>}
          </div>

          <div className="card">
            <h2>Application history</h2>
            {profile.applications.map(a => (
              <div className="list-item" key={a.id}>
                <strong>{a.job_title}</strong>
                <p>{a.company} · {a.status} · Email: {a.email_notification}</p>
              </div>
            ))}
            {!profile.applications.length && <p className="muted">No applications yet.</p>}
          </div>
        </div>
      </div>
    </main>
  );
}
