import { useEffect, useState } from "react";

export default function OpeningSplash({ onDone }) {
  const [phase, setPhase] = useState("roll");

  useEffect(() => {
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced) {
      setPhase("ask");
      return undefined;
    }
    const openTimer = setTimeout(() => setPhase("open"), 1700);
    const askTimer = setTimeout(() => setPhase("ask"), 3000);
    return () => {
      clearTimeout(openTimer);
      clearTimeout(askTimer);
    };
  }, []);

  return (
    <div className={`splash splash--${phase}`} role="dialog" aria-label="Welcome to BlogSphere">
      <button type="button" className="splash__skip" onClick={onDone}>Skip</button>
      <div className="splash__stage">
        <div className="sphere" aria-hidden="true">
          <span className="sphere__shine" />
          <span className="sphere__eye sphere__eye--left" />
          <span className="sphere__eye sphere__eye--right" />
          <span className="sphere__smile" />
        </div>
        <div className="book" aria-hidden="true">
          <div className="book__page book__page--left">
            <span />
            <span />
            <span />
          </div>
          <div className="book__spine" />
          <div className="book__page book__page--right">
            <span />
            <span />
            <span />
            <i />
          </div>
        </div>
      </div>
      <div className="splash__ask">
        <p className="eyebrow">The journal is open</p>
        <h2>If a post is worth your time, give it a like.</h2>
        <p>Open a post and tap the heart if you enjoyed it.</p>
        <button type="button" className="btn" onClick={onDone}>Enter the journal</button>
      </div>
    </div>
  );
}
