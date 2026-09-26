"""
Rank published posts with four models, then an optional LLM expansion.

BM25 and TF-IDF are retrieval scores. Naive Bayes is a multinomial
query-likelihood model. LSA projects posts and the query into a smaller
space with a singular-value decomposition. A configured Claude or GPT
model can add a few related words before those scores are computed.
Close spellings are corrected against the vocabulary first, so a typo
still reaches the models.
"""
import math
import re
from difflib import SequenceMatcher

from app.models.post import Post
from app.services.ai_service import expand_search_terms

_TOKEN = re.compile(r"[a-z0-9]{2,}")
_MODEL_NAMES = ["BM25", "TF-IDF", "Naive Bayes", "LSA"]


def _tokens(text: str) -> list[str]:
    return _TOKEN.findall((text or "").lower())


def _document(post: Post) -> list[str]:
    title = post.title or ""
    return _tokens(f"{title} {title} {title} {post.excerpt or ''} {(post.content or '')[:1800]}")


def _closest(term: str, vocab: set[str]) -> str | None:
    if term in vocab:
        return term
    if len(term) < 4:
        return None
    best_word = None
    best_score = 0.0
    for word in vocab:
        if abs(len(word) - len(term)) > 2:
            continue
        score = SequenceMatcher(None, term, word).ratio()
        if score > best_score:
            best_word, best_score = word, score
    return best_word if best_score >= 0.78 else None


def _correct(query: str, vocab: set[str]) -> list[str]:
    corrected = []
    for term in _tokens(query):
        match = _closest(term, vocab)
        corrected.append(match or term)
    return corrected


def _minmax(values: list[float]) -> list[float]:
    if not values:
        return []
    low, high = min(values), max(values)
    if high - low < 1e-9:
        return [0.0 for _ in values]
    return [(value - low) / (high - low) for value in values]


def _bm25(docs: list[list[str]], query: list[str]) -> list[float]:
    total = len(docs) or 1
    avg = sum(len(doc) for doc in docs) / total
    df: dict[str, int] = {}
    for doc in docs:
        for token in set(doc):
            df[token] = df.get(token, 0) + 1
    scores = []
    for doc in docs:
        counts: dict[str, int] = {}
        for token in doc:
            counts[token] = counts.get(token, 0) + 1
        length = len(doc) or 1
        score = 0.0
        for term in query:
            tf = counts.get(term, 0)
            if not tf:
                continue
            idf = math.log((total - df.get(term, 0) + 0.5) / (df.get(term, 0) + 0.5) + 1)
            denom = tf + 1.5 * (1 - 0.75 + 0.75 * length / (avg or 1))
            score += idf * (tf * 2.5) / denom
        scores.append(score)
    return scores


def _tfidf_vectors(docs: list[list[str]], query: list[str]) -> tuple[list[dict[str, float]], dict[str, float]]:
    df: dict[str, int] = {}
    for doc in docs:
        for token in set(doc):
            df[token] = df.get(token, 0) + 1
    total = max(len(docs), 1)

    def vector(tokens: list[str]) -> dict[str, float]:
        if not tokens:
            return {}
        counts: dict[str, int] = {}
        for token in tokens:
            counts[token] = counts.get(token, 0) + 1
        weights = {}
        for token, count in counts.items():
            idf = math.log((total + 1) / (df.get(token, 0) + 1)) + 1
            weights[token] = (count / len(tokens)) * idf
        return weights

    return [vector(doc) for doc in docs], vector(query)


def _cosine(left: dict[str, float], right: dict[str, float]) -> float:
    if not left or not right:
        return 0.0
    dot = sum(weight * right.get(token, 0.0) for token, weight in left.items())
    left_norm = math.sqrt(sum(weight * weight for weight in left.values())) or 1
    right_norm = math.sqrt(sum(weight * weight for weight in right.values())) or 1
    return dot / (left_norm * right_norm)


def _naive_bayes(docs: list[list[str]], query: list[str]) -> list[float]:
    vocab_size = max(len({token for doc in docs for token in doc}), 1)
    scores = []
    for doc in docs:
        counts: dict[str, int] = {}
        for token in doc:
            counts[token] = counts.get(token, 0) + 1
        length = max(len(doc), 1)
        log_prob = 0.0
        for term in query:
            log_prob += math.log((counts.get(term, 0) + 1) / (length + vocab_size))
        scores.append(log_prob)
    return scores


def _jacobi(matrix: list[list[float]]) -> tuple[list[float], list[list[float]]]:
    """Eigenvalues and column eigenvectors of a small symmetric matrix."""
    size = len(matrix)
    values = [row[:] for row in matrix]
    vectors = [[1.0 if row == col else 0.0 for col in range(size)] for row in range(size)]
    for _ in range(40):
        pivot_row, pivot_col, largest = 0, 1, 0.0
        for row in range(size):
            for col in range(row + 1, size):
                if abs(values[row][col]) > largest:
                    largest = abs(values[row][col])
                    pivot_row, pivot_col = row, col
        if largest < 1e-12 or size < 2:
            break
        diag_left = values[pivot_row][pivot_row]
        diag_right = values[pivot_col][pivot_col]
        off = values[pivot_row][pivot_col]
        angle = 0.5 * math.atan2(2 * off, diag_right - diag_left)
        cos, sin = math.cos(angle), math.sin(angle)
        for index in range(size):
            if index in (pivot_row, pivot_col):
                continue
            left = values[index][pivot_row]
            right = values[index][pivot_col]
            values[index][pivot_row] = values[pivot_row][index] = cos * left - sin * right
            values[index][pivot_col] = values[pivot_col][index] = sin * left + cos * right
        values[pivot_row][pivot_row] = cos * cos * diag_left - 2 * sin * cos * off + sin * sin * diag_right
        values[pivot_col][pivot_col] = sin * sin * diag_left + 2 * sin * cos * off + cos * cos * diag_right
        values[pivot_row][pivot_col] = values[pivot_col][pivot_row] = 0.0
        for index in range(size):
            left = vectors[index][pivot_row]
            right = vectors[index][pivot_col]
            vectors[index][pivot_row] = cos * left - sin * right
            vectors[index][pivot_col] = sin * left + cos * right
    return [values[index][index] for index in range(size)], vectors


def _lsa(docs: list[list[str]], query: list[str]) -> list[float]:
    vocab = sorted({token for doc in docs for token in doc})
    if not vocab or not docs:
        return [0.0 for _ in docs]
    doc_vectors, query_vector = _tfidf_vectors(docs, query)
    width = len(vocab)
    matrix = []
    for vector in doc_vectors:
        matrix.append([vector.get(token, 0.0) for token in vocab])
    count = len(docs)
    gram = [
        [sum(matrix[row][col] * matrix[other][col] for col in range(width)) for other in range(count)]
        for row in range(count)
    ]
    eigenvalues, vectors = _jacobi(gram)
    kept = [position for position in sorted(range(count), key=lambda item: eigenvalues[item], reverse=True) if eigenvalues[position] > 1e-8][:4]
    if not kept:
        return [0.0 for _ in docs]
    projected = []
    for doc_index in range(count):
        dotted = sum(matrix[doc_index][col] * query_vector.get(vocab[col], 0.0) for col in range(width))
        projected.append(dotted)
    query_latent = []
    for component in kept:
        scale = math.sqrt(eigenvalues[component]) or 1.0
        query_latent.append(sum(projected[doc_index] * vectors[doc_index][component] for doc_index in range(count)) / scale)
    query_norm = math.sqrt(sum(value * value for value in query_latent)) or 1.0
    scores = []
    for doc_index in range(count):
        row = [vectors[doc_index][component] * math.sqrt(max(eigenvalues[component], 0.0)) for component in kept]
        row_norm = math.sqrt(sum(value * value for value in row)) or 1.0
        scores.append(sum(left * right for left, right in zip(query_latent, row)) / (query_norm * row_norm))
    return scores


def _contains(post: Post, terms: list[str]) -> bool:
    haystack = set(_tokens(f"{post.title} {post.excerpt or ''} {post.content or ''}"))
    return any(term in haystack for term in terms)


def rank_posts(posts: list[Post], query: str) -> tuple[list[Post], list[str], str | None]:
    """Return matching posts, the models that scored them, and the LLM name if one ran."""
    cleaned = (query or "").strip()
    if not cleaned or not posts:
        return posts if not cleaned else [], [], None

    vocab = {token for post in posts for token in _document(post)}
    corrected = _correct(cleaned, vocab)
    related, llm_name = expand_search_terms(cleaned)
    expanded = corrected + _tokens(related)
    documents = [_document(post) for post in posts]
    bm25 = _minmax(_bm25(documents, expanded))
    doc_vectors, query_vector = _tfidf_vectors(documents, expanded)
    tfidf = [_cosine(vector, query_vector) for vector in doc_vectors]
    bayes = _minmax(_naive_bayes(documents, expanded))
    latent = _lsa(documents, expanded)
    related_terms = _tokens(related)

    scored: list[tuple[float, int, Post]] = []
    for index, post in enumerate(posts):
        useful = [term for term in corrected if len(term) >= 4] or corrected
        typed_hit = _contains(post, useful) or cleaned.lower() in f"{post.title}\n{post.content}".lower()
        related_hit = bool(related_terms) and _contains(post, related_terms)
        if not typed_hit and not related_hit:
            continue
        score = (0.34 * bm25[index]) + (0.22 * tfidf[index]) + (0.22 * bayes[index]) + (0.22 * latent[index])
        scored.append((score, index, post))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [post for _, _, post in scored], list(_MODEL_NAMES), llm_name
