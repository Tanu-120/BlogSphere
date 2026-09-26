import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await login(email, password);
      navigate(location.state?.from?.pathname || "/dashboard", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="shell">
      <form className="form-card" onSubmit={submit}>
        <h2>Welcome back</h2>
        <p style={{ marginBottom: 24 }}>Log in to write, like, and comment.</p>
        {error && <div className="banner banner--error">{error}</div>}
        <div className="field">
          <label>Email</label>
          <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div className="field">
          <label>Password</label>
          <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <button className="btn btn--full" disabled={submitting}>{submitting ? "Logging in…" : "Log in"}</button>
        <p style={{ marginTop: 18, fontSize: "0.88rem" }}>
          New here? <Link to="/register" style={{ textDecoration: "underline" }}>Create an account</Link>
        </p>
      </form>
    </div>
  );
}
