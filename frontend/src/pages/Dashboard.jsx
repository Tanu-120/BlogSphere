import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";

function formatDate(iso) {
  return new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

export default function Dashboard() {
  const { user } = useAuth();
  const [posts, setPosts] = useState(null);
  const [error, setError] = useState("");
  const [leavingId, setLeavingId] = useState(null);

  const load = () => {
    api.get("/users/me/posts").then(({ data }) => setPosts(data)).catch((err) => setError(err.message));
  };

  useEffect(() => { load(); }, []);

  const exportCsv = async () => {
    const res = await api.get("/users/me/posts/export", { responseType: "blob" });
    const url = URL.createObjectURL(res.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = "my_posts.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  const deletePost = async (id) => {
    if (!confirm("Delete this post? This cannot be undone.")) return;
    setLeavingId(id);
    await api.delete(`/posts/${id}`);
    window.setTimeout(() => {
      setPosts((list) => list.filter((item) => item.id !== id));
      setLeavingId(null);
    }, 280);
  };

  return (
    <div className="shell page">
      <div className="page-head page-head--row">
        <div>
          <p className="eyebrow">Your desk</p>
          <h1>My blogs</h1>
          <p>Signed in as {user?.name}. Drafts stay here until you publish them.</p>
        </div>
        <div className="page-head__actions">
          <button className="btn btn--ghost" onClick={exportCsv}>Export as CSV</button>
          <Link to="/new" className="btn">Write a new post</Link>
        </div>
      </div>

      {error && <div className="banner banner--error">{error}</div>}

      {!posts ? (
        <div className="skeleton-line" style={{ width: "50%", marginTop: 24 }} />
      ) : posts.length === 0 ? (
        <div className="empty-state">
          <h3>You haven't written anything yet.</h3>
          <p>Your first post doesn't have to be perfect — you can always edit it later.</p>
          <Link to="/new" className="btn" style={{ marginTop: 12 }}>Write your first post</Link>
        </div>
      ) : (
        posts.map((post) => (
          <div className={`post-row post-row--plain${post.id === leavingId ? " is-leaving" : ""}`} key={post.id}>
            <div className="post-row__body">
              <h2 className="post-row__title"><Link to={`/posts/${post.slug}`}>{post.title}</Link></h2>
              <div className="post-row__meta">
                <span className={`status-pill status-pill--${post.status}`}>{post.status}</span>
                <span>{formatDate(post.created_at)}</span>
                <span>·</span>
                <span>{post.like_count} likes</span>
                <span>·</span>
                <span>{post.comment_count} comments</span>
              </div>
              <div style={{ marginTop: 12, display: "flex", gap: 10 }}>
                <Link to={`/posts/${post.slug}/edit`} className="btn btn--ghost btn--sm">Edit</Link>
                <button className="btn btn--danger btn--sm" onClick={() => deletePost(post.id)}>Delete</button>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
}
