const WORD = /[A-Za-z0-9]+/g;
const TOKEN = /[a-z0-9]{2,}/g;
const SKIP = new Set([
  "the", "and", "for", "with", "that", "this", "from", "your", "are", "was",
  "were", "but", "not", "you", "have", "has", "its", "into", "about",
]);

function similarity(left, right) {
  const width = right.length + 1;
  let previous = Array.from({ length: width }, (_, index) => index);
  for (let i = 1; i <= left.length; i += 1) {
    const current = [i];
    for (let j = 1; j <= right.length; j += 1) {
      const cost = left[i - 1] === right[j - 1] ? 0 : 1;
      current[j] = Math.min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + cost);
    }
    previous = current;
  }
  return 1 - previous[right.length] / Math.max(left.length, right.length);
}

export function queryTerms(query) {
  const terms = (query || "").toLowerCase().match(TOKEN) || [];
  const kept = terms.filter((term) => !SKIP.has(term));
  return kept.length ? kept : terms;
}

export function wordHits(word, terms) {
  const core = word.toLowerCase();
  return terms.some((term) => {
    if (core === term) return true;
    if (term.length >= 3 && (core.startsWith(term) || (term.length >= 4 && core.includes(term)))) {
      return true;
    }
    if (term.length >= 4 && core.length >= 4 && similarity(term, core) >= 0.78) {
      return true;
    }
    return false;
  });
}

export function splitHighlights(text, query) {
  const source = text || "";
  const terms = queryTerms(query);
  if (!source || !terms.length) return [{ text: source, hit: false }];

  const pieces = [];
  let last = 0;
  for (const match of source.matchAll(WORD)) {
    const start = match.index ?? 0;
    if (start > last) pieces.push({ text: source.slice(last, start), hit: false });
    pieces.push({ text: match[0], hit: wordHits(match[0], terms) });
    last = start + match[0].length;
  }
  if (last < source.length) pieces.push({ text: source.slice(last), hit: false });
  return pieces.length ? pieces : [{ text: source, hit: false }];
}

export function postPath(slug, search) {
  const trimmed = (search || "").trim();
  if (!trimmed) return `/posts/${slug}`;
  return `/posts/${slug}?search=${encodeURIComponent(trimmed)}`;
}
