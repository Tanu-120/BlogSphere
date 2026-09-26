import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../api/client";

function formatDate(iso) {
  return new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

export default function CommentSection({ postId }) {
  const { user } = useAuth();
  const [comments, setComments] = useState([]);
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [freshId, setFreshId] = useState(null);
  const [leavingId, setLeavingId] = useState(null);
  const [sent, setSent] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const { data } = await api.get(`/posts/${postId}/comments`);
      setComments(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [postId]);

  const submit = async (e) => {
    e.preventDefault();
    if (!content.trim()) return;
    setSubmitting(true);
    setError("");
    try {
      const { data } = await api.post(`/posts/${postId}/comments`, { content });
      setContent("");
      setComments((list) => [...list, data]);
      setFreshId(data.id);
      setSent(true);
      window.setTimeout(() => setSent(false), 900);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const remove = async (id) => {
    if (!confirm("Delete this comment?")) return;
    setLeavingId(id);
    try {
      await api.delete(`/comments/${id}`);
      window.setTimeout(() => {
        setComments((list) => list.filter((item) => item.id !== id));
        setLeavingId(null);
      }, 280);
    } catch (err) {
      setLeavingId(null);
      setError(err.message);
    }
  };

  return (
    <section className="comments">
      <h3>{comments.length} {comments.length === 1 ? "comment" : "comments"}</h3>

      {user ? (
        <form className={`comment-form${submitting ? " is-sending" : ""}${sent ? " is-sent" : ""}`} onSubmit={submit} style={{ margin: "18px 0 28px" }}>
          <div className="field">
            <textarea
              placeholder="Add to the discussion…"
              value={content}
              onChange={(e) => setContent(e.target.value)}
            />
          </div>
          {error && <div className="banner banner--error">{error}</div>}
          <button className={`btn${submitting ? " is-busy" : ""}`} disabled={submitting}>
            {submitting ? "Posting…" : sent ? "Posted" : "Post comment"}
          </button>
        </form>
      ) : (
        <p style={{ margin: "12px 0 28px" }}>
          <Link to="/login" style={{ textDecoration: "underline" }}>Log in</Link> to join the discussion.
        </p>
      )}

      {loading ? (
        <div className="skeleton-line" style={{ width: "60%" }} />
      ) : comments.length === 0 ? (
        <p>No comments yet — be the first to respond.</p>
      ) : (
        comments.map((c) => (
          <div
            className={`comment${c.id === freshId ? " comment--fresh" : ""}${c.id === leavingId ? " comment--leaving" : ""}`}
            key={c.id}
          >
            <div className="comment__meta">
              <span className="avatar-badge avatar-badge--sm" aria-hidden="true">
                {c.author.name?.slice(0, 1).toUpperCase()}
              </span>
              <strong>{c.author.name}</strong>
              <span>{formatDate(c.created_at)}</span>
              {user && (user.id === c.author.id || user.role === "admin") && (
                <button className="btn btn--ghost btn--sm" onClick={() => remove(c.id)}>Delete</button>
              )}
            </div>
            <div className="comment__body">{c.content}</div>
          </div>
        ))
      )}
    </section>
  );
}
