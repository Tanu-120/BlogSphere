import { useState } from "react";
import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import OpeningSplash from "./components/OpeningSplash";
import ProtectedRoute from "./components/ProtectedRoute";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import PostDetail from "./pages/PostDetail";
import PostEditor from "./pages/PostEditor";
import Dashboard from "./pages/Dashboard";

export default function App() {
  const [intro, setIntro] = useState(true);

  return (
    <>
      {intro && <OpeningSplash onDone={() => setIntro(false)} />}
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/posts/:slug" element={<PostDetail />} />
          <Route path="/posts/:slug/edit" element={<ProtectedRoute><PostEditor /></ProtectedRoute>} />
          <Route path="/new" element={<ProtectedRoute><PostEditor /></ProtectedRoute>} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="*" element={<div className="shell" style={{ paddingTop: 60 }}><h1>Page not found</h1></div>} />
        </Routes>
      </main>
      <footer className="footer">
        <div className="shell footer__grid">
          <div>
            <strong>BlogSphere</strong>
            <p>A journal you can read in the open, and write once you have an account.</p>
          </div>
          <div>
            <span>Guests</span>
            <p>Browse published posts and read comments.</p>
          </div>
          <div>
            <span>Members</span>
            <p>Publish your own posts. Like and comment on others.</p>
          </div>
        </div>
      </footer>
    </>
  );
}
