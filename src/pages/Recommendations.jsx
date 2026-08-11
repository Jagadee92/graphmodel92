import { useEffect, useState } from "react";
import { api } from "../services/api";
import JobCard from "../components/JobCard";

export default function Recommendations() {
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.recommendations().then(setJobs).catch(e => setError(e.message));
  }, []);

  return (
    <main className="container">
      <span className="eyebrow">GRAPH TRAVERSAL</span>
      <h1>Recommended for you</h1>
      <p className="muted">
        Candidate → Skill → Job → Company
      </p>
      {error && <div className="alert error">{error}</div>}
      <div className="grid">
        {jobs.map(job => <JobCard key={job.id} job={job} />)}
      </div>
    </main>
  );
}
