import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await register(name, email, password);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="shell">
      <form className="form-card" onSubmit={submit}>
        <h2>Start writing</h2>
        <p style={{ marginBottom: 24 }}>Create an account to publish, like, and comment.</p>
        {error && <div className="banner banner--error">{error}</div>}
        <div className="field">
          <label>Name</label>
          <input required minLength={2} value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div className="field">
          <label>Email</label>
          <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div className="field">
          <label>Password</label>
          <input type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} />
          <div className="field-hint">At least 8 characters.</div>
        </div>
        <button className="btn btn--full" disabled={submitting}>{submitting ? "Creating account…" : "Create account"}</button>
        <p style={{ marginTop: 18, fontSize: "0.88rem" }}>
          Already have an account? <Link to="/login" style={{ textDecoration: "underline" }}>Log in</Link>
        </p>
      </form>
    </div>
  );
}
