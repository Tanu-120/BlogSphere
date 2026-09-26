import { useEffect, useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";
import LikeButton from "../components/LikeButton";
import CommentSection from "../components/CommentSection";
import ArticleBody from "../components/ArticleBody";
import Highlight from "../components/Highlight";

function formatDate(iso) {
  return new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" });
}

export default function PostDetail() {
  const { slug } = useParams();
  const [params] = useSearchParams();
  const search = params.get("search") || "";
  const { user } = useAuth();
  const navigate = useNavigate();
  const [post, setPost] = useState(null);
  const [error, setError] = useState("");
  const [generating, setGenerating] = useState(false);

  const load = () => {
    api.get(`/posts/${slug}`).then(({ data }) => setPost(data)).catch((err) => setError(err.message));
  };

  useEffect(() => { load(); }, [slug]);

  useEffect(() => {
    if (!post || !search) return;
    const hit = document.querySelector(".article__body mark.search-hit");
    if (!hit) return;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    hit.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "center" });
  }, [post, search]);

  const isAuthor = user && post && user.id === post.author.id;
  const isOwner = isAuthor || (user && post && user.role === "admin" && post.status !== "draft");

  const generateAI = async () => {
    setGenerating(true);
    try {
      await api.post(`/posts/${post.id}/ai/generate`);
      load();
    } finally {
      setGenerating(false);
    }
  };

  const deletePost = async () => {
    if (!confirm("Delete this post? This cannot be undone.")) return;
    await api.delete(`/posts/${post.id}`);
    navigate("/dashboard");
  };

  if (error) return <div className="shell"><div className="banner banner--error" style={{ marginTop: 32 }}>{error}</div></div>;
  if (!post) return <div className="shell"><div className="article"><div className="skeleton-line" style={{ width: "40%" }} /></div></div>;

  const minutes = Math.max(1, Math.round(post.content.split(/\s+/).length / 220));

  return (
    <div className="shell">
      <article className="article">
        {post.cover_image_url && <img className="article__cover" src={post.cover_image_url} alt="" />}
        <h1 className="article__title">
          <Highlight text={post.title} query={search} />
        </h1>
        <div className="byline">
          <span className="avatar-badge" aria-hidden="true">
            {post.author.name?.split(" ").map((n) => n[0]).slice(0, 2).join("").toUpperCase()}
          </span>
          <div>
            <strong>{post.author.name}</strong>
            <div className="article__meta">
              <span>{formatDate(post.created_at)}</span>
              <span>·</span>
              <span>{minutes} min read</span>
              <span>·</span>
              <span>{post.view_count} views</span>
              {post.status === "draft" && <span className="status-pill status-pill--draft">Draft</span>}
            </div>
          </div>
        </div>

        {post.tags && (
          <div style={{ marginBottom: 8 }}>
            {post.tags.split(",").map((t) => t.trim()).filter(Boolean).map((t) => (
              <Link key={t} to={`/?tag=${encodeURIComponent(t)}`} className="tag-chip">{t}</Link>
            ))}
          </div>
        )}

        {isOwner && (
          <div className="article__actions">
            <Link to={`/posts/${post.slug}/edit`} className="btn btn--ghost btn--sm">Edit</Link>
            <button className="btn btn--danger btn--sm" onClick={deletePost}>Delete</button>
            <button className="btn btn--ghost btn--sm" onClick={generateAI} disabled={generating}>
              {generating ? "Thinking…" : post.ai_summary ? "Regenerate AI summary" : "Generate AI summary"}
            </button>
          </div>
        )}

        {post.ai_summary && (
          <aside className="article__ai-box">
            <p className="eyebrow">Summary</p>
            <p><Highlight text={post.ai_summary} query={search} /></p>
            {post.ai_tags && <div className="field-hint">Suggested tags: {post.ai_tags}</div>}
          </aside>
        )}

        <ArticleBody text={post.content} query={search} />

        <div className="article__actions">
          <LikeButton postId={post.id} initialLiked={post.liked_by_me} initialCount={post.like_count} />
        </div>

        <CommentSection postId={post.id} />
      </article>
    </div>
  );
}
