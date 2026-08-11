import { useEffect, useState } from "react";
import { api } from "../services/api";
import JobCard from "../components/JobCard";
import ApplyModal from "../components/ApplyModal";

export default function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [search, setSearch] = useState("");
  const [skill, setSkill] = useState("");
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState("");

  async function load() {
    try {
      setError("");
      setJobs(await api.jobs(search, skill));
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => { load(); }, []);

  return (
    <main className="container">
      <div className="page-heading">
        <div><span className="eyebrow">OPPORTUNITIES</span><h1>Explore jobs</h1></div>
      </div>

      <div className="filters card">
        <input placeholder="Search title..." value={search} onChange={e => setSearch(e.target.value)} />
        <input placeholder="Exact skill..." value={skill} onChange={e => setSkill(e.target.value)} />
        <button className="primary" onClick={load}>Search</button>
      </div>

      {error && <div className="alert error">{error}</div>}
      <div className="grid">
        {jobs.map(job => (
          <JobCard key={job.id} job={job} onApply={setSelected} />
        ))}
      </div>
      {!jobs.length && <div className="card empty">No jobs found.</div>}
      {selected && <ApplyModal job={selected} close={() => setSelected(null)} />}
    </main>
  );
}
