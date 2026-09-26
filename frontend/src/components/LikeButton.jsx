import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import api from "../api/client";

export default function LikeButton({ postId, initialLiked, initialCount }) {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [liked, setLiked] = useState(initialLiked);
  const [count, setCount] = useState(initialCount);
  const [busy, setBusy] = useState(false);
  const [pop, setPop] = useState(0);

  const toggle = async () => {
    if (!user) {
      navigate("/login");
      return;
    }
    setBusy(true);
    // optimistic update
    const prevLiked = liked, prevCount = count;
    if (!liked) setPop((n) => n + 1);
    setLiked(!liked);
    setCount(liked ? count - 1 : count + 1);
    try {
      const { data } = await api.post(`/posts/${postId}/like`);
      setLiked(data.liked);
      setCount(data.like_count);
    } catch {
      setLiked(prevLiked);
      setCount(prevCount);
    } finally {
      setBusy(false);
    }
  };

  return (
    <button className={`like-btn${liked ? " is-liked" : ""}`} data-liked={liked} onClick={toggle} disabled={busy}>
      <span className="like-btn__heart" key={pop}>{liked ? "♥" : "♡"}</span>
      {pop > 0 && liked && (
        <span className="like-burst" key={`burst-${pop}`} aria-hidden="true">
          <i /><i /><i /><i /><i />
        </span>
      )}
      <span className="like-count" key={count}>{count}</span>
      {count === 1 ? "like" : "likes"}
    </button>
  );
}
