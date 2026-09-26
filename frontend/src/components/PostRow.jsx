import { Link } from "react-router-dom";
import Highlight from "./Highlight";
import { postPath } from "../lib/highlight";

function formatDate(iso) {
  const date = new Date(iso);
  return {
    month: date.toLocaleDateString(undefined, { month: "short" }),
    day: date.toLocaleDateString(undefined, { day: "numeric" }),
    year: date.toLocaleDateString(undefined, { year: "numeric" }),
  };
}

export default function PostRow({ post, query = "" }) {
  const date = formatDate(post.created_at);
  const tags = (post.tags || "").split(",").map((t) => t.trim()).filter(Boolean);

  return (
    <article className="post-row">
      <time className="post-row__date" dateTime={post.created_at}>
        <span>{date.month}</span>
        <strong>{date.day}</strong>
        <span>{date.year}</span>
      </time>
      <div className="post-row__body">
        <h2 className="post-row__title">
          <Link to={postPath(post.slug, query)}>
            <Highlight text={post.title} query={query} />
          </Link>
        </h2>
        {post.excerpt && (
          <p className="post-row__excerpt">
            <Highlight text={post.excerpt} query={query} />
          </p>
        )}
        <div className="post-row__meta">
          <span>{post.author?.name}</span>
          <span>·</span>
          <span>{post.like_count} {post.like_count === 1 ? "like" : "likes"}</span>
          <span>·</span>
          <span>{post.comment_count} {post.comment_count === 1 ? "comment" : "comments"}</span>
          {post.status === "draft" && <span className="status-pill status-pill--draft">Draft</span>}
        </div>
        {tags.length > 0 && (
          <div className="tag-row">
            {tags.map((t) => (
              <Link className="tag-chip" key={t} to={`/?tag=${encodeURIComponent(t)}`}>
                <Highlight text={t} query={query} />
              </Link>
            ))}
          </div>
        )}
      </div>
      {post.cover_image_url && (
        <img className="post-row__cover" src={post.cover_image_url} alt="" />
      )}
    </article>
  );
}
