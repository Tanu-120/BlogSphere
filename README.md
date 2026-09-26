# BlogSphere

BlogSphere is a journal with accounts, drafts, and a public reading list.

Anyone can read a published post, search the journal, and read comments. A member can write, keep drafts, upload a cover photograph, like a post, and comment. An admin can remove a published post or a comment that should not stay up, and that action is written to an audit log.

A draft belongs to the person who wrote it. It does not appear in the journal or in search. Guests, other members, and admins all receive the same not-found response as a missing page.

The API is FastAPI and SQLAlchemy. The site is React, built with Vite. Local development uses SQLite. Docker Compose runs the same code against Postgres.

Likes, comments, and view counts start at zero. They change only when someone uses the site. A published post counts one view per person. The author opening their own post does not count, and refreshing the page does not count again.

## What each person can do

A guest is anyone who is not logged in. There is no guest account to assign. Registration always creates a member. Admin is a role stored on the user row. The signup form does not offer it.

| Action | Guest | Member | Admin |
|---|---|---|---|
| Read published posts, search, filter by tag | Yes | Yes | Yes |
| Read comments | Yes | Yes | Yes |
| Register and log in | Yes | — | — |
| Create, edit, and delete their own posts | No | Yes | Yes, for their own posts |
| See or edit someone else's draft | No | No | No |
| Upload a cover image | No | Yes | Yes, on their own post |
| Like a post, comment, delete their own comment | No | Yes | Yes |
| Generate a summary for their own post | No | Yes | Yes, for their own post |
| Export their own posts as CSV | No | Yes | Yes |
| Delete a published post or any comment, and read the audit log | No | No | Yes |

Editing and deleting are checked on the server. Hiding a button is not the rule. A missing or invalid token returns `401`. A valid token for the wrong person returns `403`. A draft the caller is not allowed to see returns `404`.

## Writing

The editor sits above the essay. Select text and use the buttons for bold, italic, a heading, a quotation, a bullet list, a numbered list, or a link. Each line becomes its own paragraph when the post is shown. A blank line is extra space, not a lost break.

A new post is a draft until its status is set to published. Publishing does not copy the text. It changes the status of the same row. Cover photographs are optional. The API accepts JPEG, PNG, WebP, and GIF up to 5MB, stores the file under a random name, and never uses the original filename as a path.

## Search

The search field sits on the top edge of the journal. Matching words are marked on the list and, after you open a result, inside the essay. The page moves to the first mark in the body.

Only published posts are ranked. A close spelling still matches: `sumary` finds “summary”, and `indxes` finds “indexes”.

Before scoring, a query word of four letters or more is corrected against the journal’s own vocabulary when the spelling is close. Four models then score each candidate. The list is ordered by a blend of those scores: 0.34 BM25, 0.22 TF-IDF, 0.22 Naive Bayes, and 0.22 LSA.

| Model | Role in the ranking |
|---|---|
| BM25 | How distinctive the query words are in each essay. |
| TF-IDF | Cosine similarity between the query and the post as weighted word vectors. |
| Naive Bayes | A multinomial query-likelihood model: how likely this post is, given the words typed. |
| LSA | The same vectors projected into a smaller space, so related wording can still rank. |

The response includes `search_models`, and the page shows those names. If `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` is set, Claude or GPT may add a few related words before the scores are computed, and the page names that model. With both keys empty, that call is skipped. Search still runs on the four local models.

The same keys power **Generate AI summary** on a post the member owns. If the key is missing, the call fails, or the response is unusable, the summary is a short extract of the essay and the API reports `source: fallback`.

New posts and comments are screened before they are saved. With a key, the provider returns allow or block. Without a key, a local weighted-phrase model does the same job: threats, slurs, and insults such as “bastard” score above the block line. A blocked text returns `422` and is not stored. Ordinary criticism stays under the line.

## Views

Opening a published essay is what can count a view. The journal list does not.

Each person counts once. A logged-in member is remembered by their account. A guest is remembered by a reader id kept in the browser, so a refresh is not a second view. The author does not count. A draft does not count.

## Security

Passwords are hashed with bcrypt and are never stored or logged. Login returns a signed JWT. Later requests send it as `Authorization: Bearer …`. The API loads the user from the database on each request, so a role change is visible on the next call. The site reloads the profile at login, so after a role change the person signs out and back in.

The signing key, the database URL, and any model key live in the environment. They are not committed. `.env` is gitignored. `.env.example` lists the names and leaves the secrets blank.

An admin deletion of a published post or a comment writes an audit row: who did it, what was removed, and when. Read that log with `GET /api/admin/audit-logs` while signed in as an admin.

The public list is limited to a page, omits the full essay, and loads authors and counts without one query per row. Requests are limited to 120 per minute per address.

## Run it locally

Use two terminals.

### API

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Database file: `backend/blogsphere.db`

### Site

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The site is at http://localhost:5173. Vite forwards `/api` and `/uploads` to port 8000.

On startup the API copies the sample cover photographs into the uploads folder and refreshes the sample essays. View counts, likes, and comments already stored are left as they are.

## Run with Docker

```bash
docker compose up --build
```

Postgres starts first. The API waits until the database accepts connections. The site, the docs, and the health check use the same addresses as the local run.

To let Claude write summaries and expand search, place a key next to `docker-compose.yml` before you start:

```bash
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

Leave the key unset if you do not have one. The journal, search, likes, comments, and the summary button still work. The summary is then a local extract.

## Sample accounts

The password for all three is `northwindow42`.

| Name on the byline | Email | Role |
|---|---|---|
| Tanu Sharma | `tanu@example.com` | Member. Author of the sample essays, and of one draft, “Notes on cover images, not ready”. |
| ABC | `abc@botconsulting.io` | Member. No sample posts. This account is for likes, comments, and any draft ABC writes. |
| Tanu Sharma | `tanu@botconsulting.io` | Admin. Same display name as the author, different email. |

Set `SEED_DEMO_DATA=false` before the first boot if you want an empty database.

To promote an account you registered yourself, then sign out and back in:

```bash
sqlite3 backend/blogsphere.db "UPDATE users SET role = 'admin' WHERE email = 'you@example.com';"
```

With Docker, run the same update against the Postgres database named `blogsphere`.

## How to verify it

1. Open http://localhost:5173 logged out. Read a published post. Confirm you cannot like or comment, and that the draft “Notes on cover images, not ready” is not on the journal.
2. Search `sumary`. The summary essay should lead, with the word marked in the title and in the body.
3. Sign in as `abc@botconsulting.io`. Like a published post, turn the like off with the same button, then leave a comment. Open **My blogs**. A draft created here is visible to ABC and not to anyone else.
4. Sign out. Sign in as `tanu@example.com`. **My blogs** lists Tanu’s published essays and Tanu’s draft. ABC’s draft is not on this list. On a post Tanu owns, **Generate AI summary** still returns a summary when no model key is set.
5. Sign in as `tanu@botconsulting.io`. The public journal is the same. ABC’s draft is not listed and cannot be opened. Deleting someone else’s comment on a published post is allowed, and `GET /api/admin/audit-logs` records it.

Automated checks:

```bash
cd backend
pytest -v
```

```bash
cd frontend
npm run build
```

The tests cover registration, a wrong password, a guest reading a published post, an edit by someone who does not own the post, likes and comments that require a login, a misspelled search, one view per person, a draft hidden from other members and from an admin, a blocked comment, and the summary fallback when no model is configured. GitHub Actions runs the test suite and the frontend build on push and on pull requests.

## Configuration

Copy `backend/.env.example` to `backend/.env`.

| Variable | Purpose | Default |
|---|---|---|
| `SECRET_KEY` | Signs login tokens. Outside this laptop, set a long random value (`openssl rand -hex 32`). | a development placeholder |
| `DATABASE_URL` | SQLAlchemy URL | `sqlite:///./blogsphere.db` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | How long a login lasts | `1440` (24 hours) |
| `CORS_ORIGINS` | Browser origins allowed to call the API | `http://localhost:5173,http://localhost:3000` |
| `AI_PROVIDER` | `anthropic`, `openai`, or `none` | `anthropic` |
| `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` | Optional. Blank uses the local summary, the local ranker, and the local safety check. | blank |
| `MAX_UPLOAD_SIZE_MB` | Cover image limit | `5` |
| `RATE_LIMIT_PER_MINUTE` | Requests per address per minute | `120` |
| `SEED_DEMO_DATA` | Load and refresh the sample accounts, essays, and covers | `true` |

The site reads `VITE_API_URL` from `frontend/.env`. During development the Vite server proxies `/api` and does not need that value.

## Repository layout

```
blog-platform/
├── backend/
│   ├── app/
│   │   ├── models/            # users, posts, comments, likes, views, audit log
│   │   ├── schemas/           # request and response shapes
│   │   ├── repositories/      # SQL
│   │   ├── services/          # posts, search, safety, summaries
│   │   ├── routers/           # HTTP routes
│   │   ├── core/              # passwords, tokens, who may see a draft
│   │   ├── sample_covers/     # photographs copied into uploads on startup
│   │   ├── sample_content.py
│   │   ├── seed.py
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   └── src/
│       ├── api/               # HTTP client: token and reader id
│       ├── context/           # who is logged in
│       ├── components/        # essay body, likes, comments, opening
│       ├── pages/             # journal, post, editor, dashboard
│       └── styles/global.css
├── docker-compose.yml
└── .github/workflows/ci.yml
```

A route checks the token, calls a service, and returns a status code. Services hold the rules. Repositories hold the queries. The React app never talks to the database or to a model provider directly.

While the API is running, the same routes are documented at http://localhost:8000/docs and http://localhost:8000/redoc.
