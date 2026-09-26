import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../api/client";

export default function PostEditor() {
  const { slug } = useParams(); // present only when editing, via route /posts/:slug/edit
  const navigate = useNavigate();
  const isEdit = Boolean(slug);

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [excerpt, setExcerpt] = useState("");
  const [tags, setTags] = useState("");
  const [status, setStatus] = useState("draft");
  const [coverImage, setCoverImage] = useState(null);
  const [existingCover, setExistingCover] = useState(null);
  const [postId, setPostId] = useState(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(isEdit);
  const contentRef = useRef(null);

  const replaceContent = (next, selectFrom, selectTo) => {
    setContent(next);
    requestAnimationFrame(() => {
      const field = contentRef.current;
      if (!field) return;
      field.focus();
      field.setSelectionRange(selectFrom, selectTo);
    });
  };

  const wrapSelection = (before, after, fallback) => {
    const field = contentRef.current;
    const start = field ? field.selectionStart : content.length;
    const end = field ? field.selectionEnd : content.length;
    const selected = content.slice(start, end) || fallback;
    const next = `${content.slice(0, start)}${before}${selected}${after}${content.slice(end)}`;
    replaceContent(next, start + before.length, start + before.length + selected.length);
  };

  const prefixLines = (prefix) => {
    const field = contentRef.current;
    const start = field ? field.selectionStart : content.length;
    const end = field ? field.selectionEnd : content.length;
    const lineStart = content.lastIndexOf("\n", Math.max(0, start - 1)) + 1;
    const lineBreak = content.indexOf("\n", end);
    const lineEnd = lineBreak === -1 ? content.length : lineBreak;
    const chunk = content.slice(lineStart, lineEnd) || "Text";
    const nextChunk = chunk.split("\n").map((line) => (line.startsWith(prefix) ? line : `${prefix}${line}`)).join("\n");
    const next = `${content.slice(0, lineStart)}${nextChunk}${content.slice(lineEnd)}`;
    replaceContent(next, lineStart, lineStart + nextChunk.length);
  };

  useEffect(() => {
    if (!isEdit) return;
    api.get(`/posts/${slug}`).then(({ data }) => {
      setTitle(data.title);
      setContent(data.content);
      setExcerpt(data.excerpt || "");
      setTags(data.tags || "");
      setStatus(data.status);
      setExistingCover(data.cover_image_url);
      setPostId(data.id);
      setLoading(false);
    });
  }, [slug, isEdit]);

  const submit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      if (isEdit) {
        const { data } = await api.put(`/posts/${postId}`, { title, content, excerpt, tags, status });
        navigate(`/posts/${data.slug}`);
      } else {
        const form = new FormData();
        form.append("title", title);
        form.append("content", content);
        form.append("excerpt", excerpt);
        form.append("tags", tags);
        form.append("status", status);
        if (coverImage) form.append("cover_image", coverImage);
        const { data } = await api.post("/posts", form, { headers: { "Content-Type": "multipart/form-data" } });
        navigate(`/posts/${data.slug}`);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="shell"><div className="skeleton-line" style={{ width: "40%", marginTop: 32 }} /></div>;

  return (
    <div className="shell page">
      <div className="form-card editor-card">
        <p className="eyebrow">{isEdit ? "Editing" : "New post"}</p>
        <h2>{isEdit ? "Edit post" : "Write a new post"}</h2>
        {error && <div className="banner banner--error">{error}</div>}
        <form onSubmit={submit}>
          <div className="field">
            <label>Title</label>
            <input required minLength={3} value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Give your post a clear, specific title" />
          </div>
          <div className="field">
            <label>Excerpt (optional)</label>
            <input value={excerpt} onChange={(e) => setExcerpt(e.target.value)} maxLength={300} placeholder="A one-line teaser shown in the feed" />
          </div>
          <div className="field">
            <label>Content</label>
            <div className="format-bar" role="toolbar" aria-label="Formatting">
              <button type="button" onClick={() => wrapSelection("**", "**", "bold text")} aria-label="Bold"><strong>B</strong></button>
              <button type="button" onClick={() => wrapSelection("*", "*", "italic text")} aria-label="Italic"><em>I</em></button>
              <button type="button" onClick={() => prefixLines("## ")} aria-label="Heading">H</button>
              <button type="button" onClick={() => prefixLines("> ")} aria-label="Quote">“”</button>
              <button type="button" onClick={() => prefixLines("- ")} aria-label="Bullet list">• List</button>
              <button type="button" onClick={() => prefixLines("1. ")} aria-label="Numbered list">1. List</button>
              <button type="button" onClick={() => wrapSelection("[", "](https://)", "link text")} aria-label="Link">Link</button>
            </div>
            <textarea
              ref={contentRef}
              required
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Write your post. Press Enter for a new paragraph."
            />
            <p className="field-hint">Select words, then use the buttons. Each line you type becomes its own paragraph when the post is published.</p>
          </div>
          <div className="field">
            <label>Tags (comma-separated, optional)</label>
            <input value={tags} onChange={(e) => setTags(e.target.value)} placeholder="engineering, ai, career" />
          </div>
          {!isEdit && (
            <div className="field">
              <label>Cover image (optional)</label>
              <input type="file" accept="image/*" onChange={(e) => setCoverImage(e.target.files[0])} />
              <div className="field-hint">JPEG, PNG, WebP or GIF, up to 5MB.</div>
            </div>
          )}
          {isEdit && existingCover && (
            <div className="field-hint" style={{ marginBottom: 18 }}>Cover images can currently only be set when creating a post.</div>
          )}
          <div className="field">
            <label>Status</label>
            <select value={status} onChange={(e) => setStatus(e.target.value)}>
              <option value="draft">Draft — only visible to you</option>
              <option value="published">Published — visible to everyone</option>
            </select>
          </div>
          <button className={`btn btn--full${submitting ? " is-busy" : ""}`} disabled={submitting}>
            {submitting ? "Saving…" : isEdit ? "Save changes" : "Publish"}
          </button>
        </form>
      </div>
    </div>
  );
}
