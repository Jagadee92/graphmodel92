import { useEffect, useState } from "react";
import { api } from "../services/api";

export default function Dashboard({ profile }) {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    api.stats().then(setStats).catch(() => {});
  }, []);

  return (
    <main className="container">
      <section className="hero">
        <div>
          <span className="eyebrow">GRAPH-POWERED TALENT DISCOVERY</span>
          <h1>Welcome, {profile?.candidate?.name || "Candidate"}.</h1>
          <p>
            Discover jobs through connections between your skills, projects,
            technologies, jobs and companies.
          </p>
        </div>
      </section>

      <section className="stats">
        {[
          ["Candidates", stats?.candidates],
          ["Jobs", stats?.jobs],
          ["Companies", stats?.companies],
          ["Skills", stats?.skills],
          ["Relationships", stats?.relationships],
        ].map(([label, value]) => (
          <div className="card stat" key={label}>
            <span>{label}</span>
            <strong>{value ?? "—"}</strong>
          </div>
        ))}
      </section>

      <section className="card">
        <h2>How the graph works</h2>
        <div className="graph-flow">
          <span>Candidate</span><b>→ HAS_SKILL →</b><span>Skill</span>
          <b>→ REQUIRES_SKILL →</b><span>Job</span>
          <b>→ POSTED_BY →</b><span>Company</span>
        </div>
        <p className="muted">
          Recommendations traverse these relationships rather than relying only
          on flat field matching.
        </p>
      </section>
    </main>
  );
}
