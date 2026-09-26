import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import api from "../api/client";
import Highlight from "../components/Highlight";
import PostRow from "../components/PostRow";
import { postPath } from "../lib/highlight";

function formatDate(iso) {
  return new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" });
}

export default function Home() {
  const [params, setParams] = useSearchParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState(params.get("search") || "");

  const page = parseInt(params.get("page") || "1", 10);
  const tag = params.get("tag") || "";

  useEffect(() => {
    setLoading(true);
    const query = { page, page_size: 8 };
    if (params.get("search")) query.search = params.get("search");
    if (tag) query.tag = tag;
    api.get("/posts", { params: query }).then(({ data }) => setData(data)).finally(() => setLoading(false));
  }, [page, tag, params]);

  const submitSearch = (e) => {
    e.preventDefault();
    const next = new URLSearchParams();
    if (search.trim()) next.set("search", search.trim());
    if (tag) next.set("tag", tag);
    setParams(next);
  };

  const lead = data?.items?.[0];
  const rest = data?.items?.slice(1) || [];
  const activeSearch = params.get("search") || "";

  return (
    <div className="shell two-col page">
      <div>
        <header className="page-head">
          <p className="eyebrow">{tag ? `Tagged ${tag}` : "Published writing"}</p>
          <h1>{tag ? tag : "The journal"}</h1>
          <p className="lede">
            Published posts are open to anyone. Sign in when you want to write, like, or reply.
          </p>
          {tag && (
            <button className="btn btn--ghost btn--sm" type="button" onClick={() => setParams(activeSearch ? { search: activeSearch } : {})}>
              Clear tag
            </button>
          )}
        </header>

        <div className="journal-panel">
        <form className="journal-search" onSubmit={submitSearch}>
          <input
            placeholder="Search the journal"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search posts"
          />
          <button type="submit" aria-label="Search">
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <circle cx="11" cy="11" r="6.5" />
              <path d="M16 16.5 20 20.5" />
            </svg>
          </button>
        </form>
        {activeSearch && !loading && (
          <p className="model-row">
            {(data?.search_models || []).map((name) => (
              <span className="model-chip" key={name}>{name}</span>
            ))}
            {data?.llm && <span className="model-chip model-chip--llm">{data.llm}</span>}
          </p>
        )}

        {loading ? (
          <div className="lead lead--loading">
            <div className="skeleton-line" style={{ width: "30%" }} />
            <div className="skeleton-line" style={{ width: "80%", height: 22 }} />
            <div className="skeleton-line" style={{ width: "60%" }} />
          </div>
        ) : data.items.length === 0 ? (
          <div className="empty-state">
            <h3>
              {activeSearch
                ? `Nothing matches “${activeSearch}”.`
                : `Nothing published yet${tag ? ` for “${tag}”` : ""}.`}
            </h3>
            <p>
              {activeSearch
                ? "Try a title, a keyword, or a close spelling."
                : "Be the first to publish something worth reading."}
            </p>
          </div>
        ) : (
          <>
            <article className="lead">
              {lead.cover_image_url && (
                <Link to={postPath(lead.slug, activeSearch)}>
                  <img className="lead__cover" src={lead.cover_image_url} alt="" />
                </Link>
              )}
              <p className="eyebrow">{activeSearch ? "Best match" : "Latest"}</p>
              <h2>
                <Link to={postPath(lead.slug, activeSearch)}>
                  <Highlight text={lead.title} query={activeSearch} />
                </Link>
              </h2>
              {lead.excerpt && (
                <p className="lead__excerpt">
                  <Highlight text={lead.excerpt} query={activeSearch} />
                </p>
              )}
              <div className="post-row__meta">
                <span>{lead.author?.name}</span>
                <span>·</span>
                <span>{formatDate(lead.created_at)}</span>
                <span>·</span>
                <span>{lead.like_count} {lead.like_count === 1 ? "like" : "likes"}</span>
                <span>·</span>
                <span>{lead.comment_count} {lead.comment_count === 1 ? "comment" : "comments"}</span>
              </div>
              <Link className="text-link" to={postPath(lead.slug, activeSearch)}>Read the post</Link>
            </article>
            {rest.map((post) => <PostRow key={post.id} post={post} query={activeSearch} />)}
          </>
        )}
        </div>

        {data && data.total_pages > 1 && (
          <div className="pagination">
            <button
              className="btn btn--ghost btn--sm"
              disabled={page <= 1}
              onClick={() => setParams({ ...Object.fromEntries(params), page: String(page - 1) })}
            >
              Previous
            </button>
            <span style={{ alignSelf: "center", fontSize: "0.85rem", color: "var(--ink-faint)" }}>
              Page {page} of {data.total_pages}
            </span>
            <button
              className="btn btn--ghost btn--sm"
              disabled={page >= data.total_pages}
              onClick={() => setParams({ ...Object.fromEntries(params), page: String(page + 1) })}
            >
              Next
            </button>
          </div>
        )}
      </div>

      <aside className="sidebar">
        <div className="sidebar-box">
          <h3>Who can do what</h3>
          <ul className="rule-list">
            <li><strong>Read</strong> any published post, with no account.</li>
            <li><strong>Write</strong> once you sign in. You can edit only your own posts.</li>
            <li><strong>Like and comment</strong> when you are logged in. Guests can still read the thread.</li>
          </ul>
        </div>
      </aside>
    </div>
  );
}
