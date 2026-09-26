import { splitHighlights } from "../lib/highlight";

export default function Highlight({ text, query }) {
  const pieces = splitHighlights(text, query);
  if (pieces.length === 1 && !pieces[0].hit) return text || null;
  return pieces.map((piece, index) => (
    piece.hit
      ? <mark className="search-hit" key={index}>{piece.text}</mark>
      : <span key={index}>{piece.text}</span>
  ));
}
