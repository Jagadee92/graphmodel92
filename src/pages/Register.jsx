import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../services/api";

export default function Register({ onLogin }) {
  const [form, setForm] = useState({
    name: "", email: "", password: "", location: "", bio: "", skills: ""
  });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      const result = await api.register({
        ...form,
        skills: form.skills.split(",").map(x => x.trim()).filter(Boolean)
      });
      localStorage.setItem("talentgraph_token", result.access_token);
      onLogin();
      navigate("/");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="auth-shell">
      <form className="card auth-card wide" onSubmit={submit}>
        <h1>Create candidate account</h1>
        <p className="muted">Your password is hashed before storage.</p>
        {error && <div className="alert error">{error}</div>}
        <label>Name<input required value={form.name} onChange={e => setForm({...form,name:e.target.value})}/></label>
        <label>Email<input type="email" required value={form.email} onChange={e => setForm({...form,email:e.target.value})}/></label>
        <label>Password<input type="password" minLength="8" required value={form.password} onChange={e => setForm({...form,password:e.target.value})}/></label>
        <label>Location<input required value={form.location} onChange={e => setForm({...form,location:e.target.value})}/></label>
        <label>Skills <span className="muted">(comma separated)</span><input value={form.skills} onChange={e => setForm({...form,skills:e.target.value})}/></label>
        <label>Bio<textarea value={form.bio} onChange={e => setForm({...form,bio:e.target.value})}/></label>
        <button className="primary">Register</button>
        <p>Already registered? <Link to="/login">Login</Link></p>
      </form>
    </div>
  );
}
