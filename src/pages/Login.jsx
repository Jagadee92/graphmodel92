import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../services/api";

export default function Login({ onLogin }) {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      const result = await api.login(form);
      localStorage.setItem("talentgraph_token", result.access_token);
      onLogin();
      navigate("/");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="auth-shell">
      <form className="card auth-card" onSubmit={submit}>
        <h1>Welcome back</h1>
        <p className="muted">Login to explore relationship-based job matches.</p>
        {error && <div className="alert error">{error}</div>}
        <label>Email<input type="email" required value={form.email} onChange={e => setForm({...form,email:e.target.value})}/></label>
        <label>Password<input type="password" required value={form.password} onChange={e => setForm({...form,password:e.target.value})}/></label>
        <button className="primary">Login</button>
        <p>New candidate? <Link to="/register">Create an account</Link></p>
      </form>
    </div>
  );
}
