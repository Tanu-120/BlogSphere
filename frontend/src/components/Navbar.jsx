import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const initials = user?.name?.split(" ").map((n) => n[0]).slice(0, 2).join("").toUpperCase();

  return (
    <header className="masthead">
      <div className="shell masthead__row">
        <Link to="/">
          <span className="masthead__title">BlogSphere</span>
          <span className="masthead__tag">write, publish, discuss</span>
        </Link>

        <nav className="masthead__nav">
          <NavLink to="/" end>Journal</NavLink>
          {user && <NavLink to="/dashboard">My blogs</NavLink>}
          {user && <NavLink to="/new">Write</NavLink>}

          {user ? (
            <div className="masthead__user">
              <Link to="/dashboard" title={user.email}>
                <span className="avatar-badge">{initials || "U"}</span>
              </Link>
              <button
                className="btn btn--ghost btn--sm"
                onClick={() => {
                  logout();
                  navigate("/");
                }}
              >
                Log out
              </button>
            </div>
          ) : (
            <div className="masthead__user">
              <Link to="/login">Log in</Link>
              <Link to="/register" className="btn btn--sm">Start writing</Link>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
}
