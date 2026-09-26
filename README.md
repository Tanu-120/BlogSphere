# BlogSphere

A journal you can read without an account, and write once you have one.

Guests can browse published posts, search them, and read comments. A member can publish their own posts, upload a cover photo, like, and comment. An admin can remove someone else's post or comment, and that action is written to an audit log. Drafts stay off the public list and out of search.

The API is FastAPI and SQLAlchemy. The site is React, built with Vite. Local development uses SQLite. Docker Compose runs the same code on Postgres.

Each published sample post has a cover photograph and an essay of ordinary length. Likes, comments, and view counts start at zero and change only when someone actually uses the site. A published post counts one view per person. The author opening their own post does not count, and refreshing the page does not count again.

## What each person can do

| Action | Guest | Member | Admin |
|---|---|---|---|
| Read published posts, search, filter by tag | Yes | Yes | Yes |
| Read comments | Yes | Yes | Yes |
| Register and log in | Yes | — | — |
| Create, edit, and delete their own posts | No | Yes | Yes |
| Upload a cover image | No | Yes | Yes |
| Like a post, comment, delete their own comment | No | Yes | Yes |
| Generate a summary for their own post | No | Yes | Yes |
| Export their own posts as CSV | No | Yes | Yes |
| Delete any post or comment, read the audit log | No | No | Yes |

A guest is anyone without a token. There is no guest account to assign. New registrations are always members (`user`). Admin is a role on the user row, set in the database, not chosen on the signup form.

A draft is visible only to the member who wrote it. Guests, other members, and admins all get the same not-found response as a missing post. An admin can still remove a published post or a comment.

## Search

The field sits on the top edge of the journal. Submit it from the button inside the field. Matching words are marked on the list and, if you open a result, inside the essay. The page scrolls to the first mark in the body. Close spellings count: `sumary` finds "summary", and `indxes` finds "indexes".

Published posts only. Drafts are not in the ranking.

Four models score every search, then the list is ordered by a blend of those scores:

| Model | What it does |
|---|---|
| BM25 | Ranks posts by how distinctive the query words are in each essay. |
| TF-IDF | Compares the query and the post as weighted word vectors. |
| Naive Bayes | A multinomial query-likelihood model: how likely this post is, given the words you typed. |
| LSA | Projects posts and the query into a smaller space (a singular-value decomposition) so related wording can still rank. |

Before those scores run, each query word of four letters or more is corrected against the journal's own vocabulary when the spelling is close. The response includes `search_models` so the page can show which models ran.

If `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` is set, Claude or GPT is asked for a few related words and those words join the query. The chip on the page names the model. With both keys empty, that call is skipped and the four local models do the ranking. Summaries use the same keys, and fall back to a short extract of the essay when no model is reachable.

New posts and comments are screened before they are saved. With a key, the screen is the same provider, asked to allow or block the text. Without a key, a local weighted-phrase scorer does it. A blocked text returns `422`.

## Run it locally

### API

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

The API listens on http://localhost:8000. Swagger UI is at `/docs`. The database file is `backend/blogsphere.db`.

### Site

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The site listens on http://localhost:5173. Vite forwards `/api` and `/uploads` to port 8000.

On startup the API copies the sample cover photos into the uploads folder and refreshes the sample essays. View counts, likes, and comments already in the database are left alone.

## Run with Docker

```bash
docker compose up --build
```

- Site: http://localhost:5173
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

Postgres starts first. The API waits until the database accepts connections.

To let Claude write summaries and expand search, put a key beside `docker-compose.yml` before you start:

```bash
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

Leave it unset if you do not have a key. The journal, search, and the summary button still work.

## Sample accounts

| Name on the byline | Email | Role |
|---|---|---|
| Tanu Sharma | `tanu@example.com` | Member. Author of the sample essays, including one draft. |
| ABC | `abc@botconsulting.io` | Member. No posts yet. Use this account to like and comment. |
| Tanu Sharma | `tanu@botconsulting.io` | Admin. |

Set `SEED_DEMO_DATA=false` before the first boot if you want an empty database.

To promote an account you created yourself:

```bash
sqlite3 backend/blogsphere.db "UPDATE users SET role = 'admin' WHERE email = 'you@example.com';"
```

Log out and back in afterwards. The site loads the role at login. With Docker, run the same `UPDATE` against the Postgres database named `blogsphere`.

## How to try it

1. Open http://localhost:5173. The opening animation plays once. Skip or enter. You are a guest: you can read, and you cannot like or comment.
2. Search `sumary`. The summary essay should be first, with **summary** marked. Open it and confirm the marks in the body and the cover photo.
3. Search `indxes`. The feed essay mentions database indexes and should appear.
4. Log in as `abc@botconsulting.io`. Like a post and leave a comment. The heart and the new comment animate. A comment containing a threat is refused.
5. Log out. Log in as `tanu@example.com`. The dashboard lists the published essays and one draft. The draft is absent from the public journal. Edit a post, or create one with a cover image.
6. On a post you own, use **Generate AI summary**. With no key, the summary is an extract of the essay and the API reports `source: fallback`.
7. Log in as `tanu@botconsulting.io`. Delete someone else's comment or post if you need to show moderation. `GET /api/admin/audit-logs` (with that token) lists the action.

Automated checks:

```bash
cd backend
pytest -v
```

```bash
cd frontend
npm run build
```

The tests cover registration, a wrong password, a guest reading, an edit by someone who does not own the post (`403`), likes and comments that require a login, a misspelled search, a blocked comment, and the summary fallback when no model is configured. GitHub Actions runs both commands on push and on pull requests.

## Configuration

Backend values live in `backend/.env`, copied from `backend/.env.example`.

| Variable | What it does | Default |
|---|---|---|
| `SECRET_KEY` | Signs login tokens. Use a long random value outside your laptop (`openssl rand -hex 32`). | a dev placeholder |
| `DATABASE_URL` | SQLAlchemy URL | `sqlite:///./blogsphere.db` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | How long a login lasts | `1440` (24 hours) |
| `CORS_ORIGINS` | Which browser origins may call the API | `http://localhost:5173,http://localhost:3000` |
| `AI_PROVIDER` | `anthropic`, `openai`, or `none` | `anthropic` |
| `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` | Leave blank to use the local summary, ranker, and safety scorer | blank |
| `MAX_UPLOAD_SIZE_MB` | Cover image limit | `5` |
| `RATE_LIMIT_PER_MINUTE` | Requests per IP per minute | `120` |
| `SEED_DEMO_DATA` | Refresh sample users, essays, and covers on startup | `true` |

The site only needs `VITE_API_URL` in `frontend/.env`. The Vite dev server ignores it and proxies `/api` instead.

`.env` is gitignored. `.env.example` is the list of names, with no secrets.

## Repository layout

```
blog-platform/
├── backend/                  # FastAPI
│   ├── app/
│   │   ├── models/           # tables
│   │   ├── schemas/          # request and response shapes
│   │   ├── repositories/     # queries
│   │   ├── services/         # rules: posts, search, safety, summaries
│   │   ├── routers/          # HTTP routes
│   │   ├── core/             # passwords, tokens, permissions
│   │   ├── sample_covers/    # photographs copied into uploads on startup
│   │   ├── sample_content.py
│   │   ├── seed.py
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # React
│   └── src/
│       ├── api/              # HTTP client, attaches the token
│       ├── context/          # who is logged in
│       ├── components/
│       ├── pages/
│       ├── lib/highlight.js  # which words to mark after a search
│       └── styles/global.css
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API_CONTRACTS.md
│   ├── USAGE.md
│   └── DEMO.md
├── docker-compose.yml
└── .github/workflows/ci.yml
```

A route checks the token, calls a service, and returns a status code. Services hold the rules. Repositories hold the SQL. Ownership is checked on the server, not only by hiding a button.

## Further reading

| Topic | Where |
|---|---|
| Request path, data model, security | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| Each route, status code, and body | [docs/API_CONTRACTS.md](docs/API_CONTRACTS.md) |
| Everyday use of the site | [docs/USAGE.md](docs/USAGE.md) |
| Two-minute demo to record | [docs/DEMO.md](docs/DEMO.md) |

Interactive API docs are generated from the routes while the API is running: http://localhost:8000/docs and http://localhost:8000/redoc.
