export default function JobCard({ job, onApply, canApply = true }) {
  return (
    <article className="card job-card">
      <div className="job-top">
        <div>
          <h3>{job.title}</h3>
          <p className="muted">{job.company} · {job.location}</p>
        </div>
        {job.match_score !== undefined && (
          <span className="score">{job.match_score}% match</span>
        )}
      </div>

      {job.description && <p>{job.description}</p>}

      <div className="chips">
        {(job.skills || job.matched_skills || []).map((skill) => (
          <span className="chip" key={skill}>{skill}</span>
        ))}
      </div>

      {onApply && canApply && (
        <button className="primary" onClick={() => onApply(job)}>
          Apply
        </button>
      )}
    </article>
  );
}
