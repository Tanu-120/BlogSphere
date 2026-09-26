"""Sample posts loaded on an empty database so the journal is not blank."""
from datetime import datetime, timedelta, timezone

AUTHOR_EMAIL = "tanu@example.com"
READER_EMAIL = "abc@botconsulting.io"
ADMIN_EMAIL = "tanu@botconsulting.io"
DEMO_PASSWORD = "northwindow42"

_START = datetime(2026, 9, 18, 10, 30, tzinfo=timezone.utc)


def _at(days: int, hours: int = 0) -> datetime:
    return _START + timedelta(days=days, hours=hours)


POSTS = [
    {
        "slug": "the-lane-after-rain",
        "title": "The lane after rain",
        "excerpt": "Wet stone, one bicycle, and the few minutes before the lane dries.",
        "tags": "photography, streets",
        "cover": "cover-lane.png",
        "status": "published",
        "created_at": datetime(2026, 9, 27, 12, 30, tzinfo=timezone.utc),
        "view_count": 0,
        "ai_summary": None,
        "ai_tags": None,
        "content": """The lane was empty except for the bicycle. I liked that it had been left unlocked, or that I could not tell. I did not wait for a person to walk through the frame.

The rain had stopped a few minutes earlier. The stone was still dark, almost black between the slabs, and the bicycle read as a silhouette against it. That darkness does not last. Once the lane dries, the stone goes back to a dull grey and the bicycle becomes an ordinary object parked against a wall. I had a short window, and I knew it while I was standing there.

## Why the lane, and not a portrait

A street after rain is an easy picture. Someone walking through it would have been an easier one, and the wrong one. A person becomes the subject. The bicycle would have turned into a prop, and the lane into a background. I wanted the opposite. The bicycle had been stood there carefully, which is a different fact from being abandoned, and the picture cannot quite prove which. That uncertainty is the interesting part. A face would have settled it.

I left the shop signs out of the frame. They would have dated the lane, and they would have asked to be read. The lane did not need a name. It needed the sheen on the stone and the one machine someone had trusted to the weather.

## Two frames, and the pedal

I took two pictures. The first was tidier. The bicycle sat square to the wall, the lane ran out cleanly to the right, and nothing stuck into the foreground. It looked like a photograph of a bicycle.

The second one had the pedal turned out toward the lane. A small thing, and it broke the tidy outline. It also made the bicycle look recently used. Someone had got off and not bothered to square the pedal. Or they had, and the chain had slipped it back. I cannot know. I kept the second frame because the first one had already decided what the picture was about, and the second one had not.

## What the rain actually changed

Before the rain the lane is a shortcut. After it, for those few minutes, it is a surface. Water sits in the joints. The wall opposite goes darker at the bottom, where the splash reached, and stays dry above the brick line. You can see how hard it rained by that line, better than by any puddle.

I did not wait for the sun. Sun on a wet lane is a postcard. Flat cloud keeps the stone dark and the bicycle black, which is the picture I had stopped for. By the time I reached the end of the lane the colour was already lifting. The bicycle, if it was still there, would have been just a bicycle again.
""",
    },
    {
        "slug": "rain-on-the-glass",
        "title": "Rain on the glass",
        "excerpt": "The drops stayed sharp. The garden behind them went soft.",
        "tags": "photography, weather",
        "cover": "cover-rain.png",
        "status": "published",
        "created_at": datetime(2026, 9, 26, 10, 30, tzinfo=timezone.utc),
        "view_count": 0,
        "ai_summary": None,
        "ai_tags": None,
        "content": """I stood at the glass longer than I meant to. The garden went soft, and the drops on the pane were the only sharp thing left.

The rain was not heavy yet. It was the kind that beads and stays, each drop holding its shape until another one joins it and both run. From inside, that is two pictures at once. The garden is the far one. The glass is the near one. You cannot have both in focus, and choosing is the whole decision.

## What the rain did to the picture

The garden was already out of focus before I touched the lens. I focused on the outside of the pane. The drops went sharp. The hedge became a green wash, and the path disappeared into it. That is the photograph. There is no subject beyond the water and the fact of being indoors.

I left the dark edge of the window in the frame. Without it, the picture could be a soft lens pointed at a wet hedge. The edge says the camera is in a room. You are looking out, not standing in the garden getting wet. I care about that difference. Rain from inside is a different weather from rain on your coat.

I did not add contrast afterwards. The grey was already right. Brightening it would have made a cleaner picture and a less honest one. The hour was dim. The photograph should be dim.

## The frame I did not keep

I waited for a heavier minute so the drops would streak, then wished I had not. The streaks looked like a filter someone had laid over a window. The still drops looked like weather. I kept the still frame.

There was another one, from the same hour, with my reflection in the glass. A shoulder, and the dark shape of the camera. It was a true picture of standing there. It was also a picture of me, and I did not want to be in it. The rain was the subject. A reflection would have split that in two, the way a person walking into the lane would have split the bicycle from the stone.

I will not replace this later with a brighter version from a sunnier shower. The grey is the point. If the garden had been sharp, I would have been photographing the garden, and I already know what the garden looks like.
""",
    },
    {
        "slug": "morning-on-the-desk",
        "title": "Morning on the desk",
        "excerpt": "A blank notebook, a half-finished cup, and ten minutes of light from the left.",
        "tags": "photography, journal",
        "cover": "cover-desk.png",
        "status": "published",
        "created_at": datetime(2026, 9, 25, 11, 30, tzinfo=timezone.utc),
        "view_count": 0,
        "ai_summary": None,
        "ai_tags": None,
        "content": """The notebook was blank when I took this. That is the point of the picture. The page had not been started, and the light was already leaving.

I took it before the coffee was finished. You can tell from the cup, if you look at the rim: a tide line, not an empty cup and not a full one. The morning was in the middle of itself. A finished cup would have meant I had sat there long enough for the light to go. A full one would have meant I had only just arrived. The rim is the clock.

## The light, and how long it stayed

It came from the left, through the gap in the curtain I never quite close. For about ten minutes it laid a hard edge across the notebook and left the rest of the desk in a softer shade. Then the sun moved off that gap and the desk went flat. The same objects were there. The picture was gone.

I have learned to take the frame when the room looks briefly like a room, and not to wait for a better arrangement of objects. Moving the cup closer to the notebook would have made a neater composition. It would also have made the photograph about me tidying. The light was doing the work. I left the cup where I had put it down.

## Why the page is empty

A filled page would have been someone else's reading, or mine from another day. Either way the cover of this morning would have contained words that were not about the morning. The blank page is the subject because nothing on it competes with the light. You can see the grain of the paper. You can see that nothing has been decided yet.

I did not straighten the notebook. One corner sits closer to the camera than the other, which is how it was when I opened it. Straightening it would have been the same mistake as moving the cup. The desk in the picture is the desk I was actually using, for the few minutes the light agreed to stay.
""",
    },
    {
        "slug": "a-summary-is-allowed-to-fail",
        "title": "A summary is allowed to fail",
        "excerpt": "If the model is slow or the key is missing, the article should still be there. The summary is optional.",
        "tags": "ai, apis, publishing",
        "cover": "cover-summary.jpg",
        "status": "published",
        "created_at": _at(0),
        "view_count": 0,
        "ai_summary": "An AI summary on a post should time out and fall back, instead of blocking publish. The article is the source of truth; the summary is a convenience.",
        "ai_tags": "ai, timeouts, fallbacks",
        "content": """I added a button that asks a model for two sentences and a few tags. It is useful when I am skimming my own archive. It is also the least important part of the post. The essay is the thing a reader came for. A summary that never arrives should not keep them from it.

The first time I wired the button up, a slow response held the whole page. The save had already succeeded. The reader was staring at a spinner because a second, optional request had not come back. That is the wrong failure. Publishing and summarizing are different jobs, and only one of them is required.

## What I actually depend on

The provider key stays in the environment, next to the database URL and the signing secret. The request has a timeout, so a quiet network cannot pin a worker forever. If the key is empty, the call errors, or the body is not the JSON I asked for, I keep a plain extract of the opening lines and say so. The button still finishes. The client is told whether the text came from the provider or from that local extract.

I would rather show a slightly dull summary than a spinner that never ends. Readers can ignore a dull paragraph. They cannot ignore a page that refuses to settle.

Retries are tempting and usually wrong on a click. The person is waiting in front of the form. One attempt, then the fallback, is enough. If this ever needs to be fancier, a background job can try again after the page has already moved on. Doing that work inside the click teaches the wrong lesson: that the model is part of the critical path.

## What I do not send

I do not send the password, the token, or anyone's email. The model sees the title and the body, because that is the text being summarized. Nothing else on the account is relevant to a two-sentence gloss. The response is stored on the post as `ai_summary` and `ai_tags`. It can be replaced the next time I press the button. It is not a second copy of the essay, and it is not locked in place if I edit the article later.

## Leaving the key blank

If you are reading this on a laptop with no API key, the fallback is what you get when you press the button. That is a feature, not a degraded mode I forgot to hide. A journal should boot with nothing but Python, a database file, and the site. A model is an addition. The article should still be there when the addition is absent, slow, or simply wrong.

I keep the prompt short on purpose. Two sentences, a handful of tags, JSON only. A longer prompt invites the model to rewrite the piece in a voice that is not mine. I want a label on the box, not a second author.
""",
    },
    {
        "slug": "drafts-are-the-point",
        "title": "Drafts are the point",
        "excerpt": "A published post is public. A draft is mine. The product is mostly that distinction.",
        "tags": "writing, product",
        "cover": "cover-drafts.jpg",
        "status": "published",
        "created_at": _at(1, 2),
        "view_count": 0,
        "ai_summary": "Guests can read published posts. Drafts stay with the author. Likes and comments require a login, because those actions should have a name attached.",
        "ai_tags": "drafts, publishing, access",
        "content": """Most of the writing I care about is not ready. A sentence I liked on Tuesday often looks thin on Thursday, and the paragraph I was sure about usually needs a cut. If the only status a post can have is "live", I either publish too early or I keep the file on my laptop, where nobody else will ever see the finished version either.

So a post here is a draft until I say otherwise. Drafts show up on my own list, with the rest of my work, so I can find them again. They do not show up on the public journal. They do not show up in search. They do not show up if you guess the link while logged out. The response in that last case is the same not-found a missing slug would get. I do not want a stranger to learn that an unfinished note exists just because they tried a plausible URL.

## Who can do what

Anyone can read what is published, including the comments under it. You do not need an account for that. Search, tags, and the cover photos are all part of that public surface. The journal is meant to be readable before anyone is asked to sign up.

Writing is different. Creating a post, editing it, deleting it, liking it, or leaving a comment all require a login. Editing and deleting are tighter than that: they belong to the author. Another logged-in reader can argue in the comments and can take a like back. They cannot rewrite the essay, change the cover, or move it between draft and published.

I kept one note in my account as a draft on purpose, so the split is visible without a second app. If you are not me, you will not see that note. An admin does not get a copy of it either. Log in as the author and it is sitting on the dashboard, marked as a draft, waiting.

## Why the line is worth the trouble

The temptation is to treat a draft as a published post with a quieter link. That leaks. A preview URL gets forwarded. A list endpoint forgets the status filter. A search index includes the body because it was easier to index everything. Each of those is a small bug that adds up to "my unfinished piece is public."

The rule I kept is dull and easy to test. The public list query requires the published status. The detail route checks the status before it increments the view count. Search ranks only the rows that list already loaded. A draft can be as long as I like, with a cover photo attached, and none of that reaches a guest.

Publishing is then a small edit: change the status, save, and the same row becomes readable. I do not copy the text into a second table. There is one post. Its status is the product.
""",
    },
    {
        "slug": "do-not-store-the-password",
        "title": "Do not store the password you were given",
        "excerpt": "Hash it, sign a token, and check ownership on the server. The login form is not the security boundary.",
        "tags": "security, auth",
        "cover": "cover-password.jpg",
        "status": "published",
        "created_at": _at(2, 1),
        "view_count": 0,
        "ai_summary": "Passwords are stored as bcrypt hashes. A JWT proves who is calling on later requests. Authorization is a separate check: the author, or an admin.",
        "ai_tags": "bcrypt, jwt, authorization",
        "content": """Login feels like a form. It is a storage decision. The box on the page is the easy part. The question that matters is what remains in the database after the person has closed the tab, and what a later request is allowed to believe about them.

I never write the password into the database. Registration runs it through bcrypt and stores the hash. On the next login I hash what was typed and compare the hashes. If someone copies the database file, they still do not have the passwords. They have strings that are expensive to guess and useless as the original secret. I do not log the password either. A request log that includes the body of a login is a second copy of the thing I just refused to store.

## The token is not the permission

A successful login returns a signed JWT. Later requests send it in the Authorization header. The site keeps that token in local storage under a single key and attaches it on the way out. That answers "who is this?" It does not answer "may they delete this post?"

Those are different checks, and they fail differently. A missing or bad token is 401. A valid token for the wrong person is 403. I test them separately, because hiding the Edit button only stops people who stay on the page and never open the network panel. The route still has to refuse the call.

The role on the token is not trusted by itself for the interesting decisions. Each request loads the user from the database using the id in the token. If an account was promoted to admin, or demoted, the next request sees the row as it is now. The React app, though, keeps the profile it loaded at login. After a role change you log out and back in, so the buttons match the server.

## What stays off the page

The signing key lives in the environment, next to the database URL and the model key. None of those belong in the repository. The example env file lists the names and leaves the secrets blank. A fresh clone boots. It does not boot with my key.

Sessions here are the token itself, with an expiry. I did not add refresh tokens. Twenty-four hours is a long life for an access token, and I would shorten it if this were holding anything more sensitive than drafts and comments. For a journal, the trade is that you are not sent back to the login form every hour while you are writing.

Ownership is checked again on the way out of an edit. The author can change their own post. An admin can remove a post, and that removal is written down. A second member, logged in and perfectly valid, gets a refusal if they try to save over someone else's essay. The form never gets a chance to be the boundary. The server is the boundary.
""",
    },
    {
        "slug": "the-feed-should-stay-small",
        "title": "The feed should stay small",
        "excerpt": "List pages should not ship the full essay, and they should not ask the database once per row.",
        "tags": "performance, sql",
        "cover": "cover-feed.jpg",
        "status": "published",
        "created_at": _at(4),
        "view_count": 0,
        "ai_summary": "The public list is paginated, omits the full body, and loads like and comment counts in grouped queries. A composite index matches the published-and-newest sort.",
        "ai_tags": "pagination, indexes, caching",
        "content": """The home page looks simple. A title, a short extract, a cover, a few counts. It is still the query I will get wrong first, because it runs on every visit and it grows with the archive.

If I load every published essay, body included, and then count likes one post at a time, the page gets slower in a way I will not notice with five rows. I noticed it as soon as I sketched the loop on paper: two extra queries per post, plus another for the author. Ten posts is already a pile of round trips. A hundred is a different product.

## What the list returns

A page of posts, not the whole table. The page size is capped on the server, so a client cannot ask for an unbounded page by editing the query string. The list item has the title, the excerpt, the cover, the tags, and the counts. The body waits for the article page. Opening a post is the request that increments the view count. Merely appearing in the feed does not.

Authors are loaded with the posts, in the same query, instead of one lookup per row. Like counts and comment counts are each one grouped query for the ids on that page. The shape of the page stays the same as the archive grows. The cost stays tied to the page, not to the history.

Tag filters stay in SQL, because a tag is a column on the row. Search is a different job: it has to read the essay. I keep that work off the list query. The feed stays a page of small records. The ranking can be slower, because nobody asks for it until they type.

## Indexes, and a short memory

The common filter is published posts, newest first, so those two columns share an index. I checked the query plan rather than assuming the index was in use. An index that the planner ignores is a comment, not a speedup. Database indexes keep the feed fast only when the query is the one the index was built for.

There is also a short cache on that public list, dropped when someone publishes, comments, or likes. It lives in the API process. Fine for one server. Wrong for two, which is why it sits in one small module I can replace without touching the route. Thirty seconds is long enough to absorb a refresh storm and short enough that I am not embarrassed if an invalidation is missed.

The cover photos ride along as a URL, not as bytes in the JSON. The image is a separate request to the upload folder. The feed stays a list of small records. The photographs can be large without making the first response large too.
""",
    },
    {
        "slug": "two-roles-and-a-log",
        "title": "Two roles, and a log when an admin steps in",
        "excerpt": "Readers own their posts. Admins can remove a post that should not stay up, and that action is recorded.",
        "tags": "moderation, roles",
        "cover": "cover-roles.jpg",
        "status": "published",
        "created_at": _at(5, 3),
        "view_count": 0,
        "ai_summary": "New accounts are ordinary users. Admins can delete any post or comment, and each of those actions is written to an audit log. Ownership still applies to everyday edits.",
        "ai_tags": "roles, audit, moderation",
        "content": """I did not want a permissions screen. I wanted one extra question: who is allowed to take down someone else's post, and how would I explain that removal a week later?

Everyone who registers is a user. They can write, edit their own work, like, and comment. They can delete their own comments. They cannot open the moderation routes, and they cannot see a draft that is not theirs. The registration form does not offer a role. There is no checkbox for "make me an admin." If there were, it would be a joke that someone would eventually take seriously.

Admin is assigned on purpose, in the database, not in the interface. An admin can delete a post or a comment they do not own. That delete writes a row: who did it, what they removed, and when. If I have to explain a removal next week, I want that row more than I want a memory of the click. The audit log is readable from the admin API. It is not a decoration on the profile page.

## What admin does not mean

Admin does not mean "edit anyone's draft as if it were yours." Everyday changes stay with the author. The person who wrote the essay is the person who should change the wording, the cover, and the moment it becomes public. Moderation is for content that should not remain published, not for quiet rewrites no one asked for.

A guest is simply someone with no token. There is no guest account to assign and nothing to promote them from except registration. They can read the journal, search it, and open a post. The like control and the comment box ask them to sign in. After they do, they are a member, same as anyone else who registered.

Two of the sample accounts share a display name and do not share an email. The address is the identity. The name is what the byline shows. Promoting a member is an update to the role column for that email, followed by a fresh login so the site reloads the profile.

## Two roles are enough until a third job appears

I would add another role only when a real job shows up that is neither "this is my post" nor "this should come down." An editor who may change wording, but may not delete. A moderator who may hide a comment, but may not remove the essay. I do not have those jobs yet. Inventing the role before the job means a screen full of checkboxes and no one who can say what each box is for.

Until then, two roles and a log are enough. The author owns the draft and the wording. The admin may take down what is already public, and must leave a record of having done it. Everything else is a person reading, or a person writing under their own name.
""",
    },
]


DRAFT = {
    "slug": "notes-on-cover-images",
    "title": "Notes on cover images, not ready",
    "excerpt": "Still drafting. The filename from the browser is not a path I should trust.",
    "tags": "uploads, drafts",
    "cover": None,
    "status": "draft",
    "created_at": _at(6),
    "view_count": 0,
    "ai_summary": None,
    "ai_tags": None,
    "content": """A cover image arrives as multipart form data, next to the title and the essay. I check the type against a short allow-list, stream the bytes to disk in chunks, and stop if the file crosses the size limit. A file that fails the check is deleted, including the partial one I had already started writing. The post is not saved with a broken path.

I store the image under a random name. The original filename is whatever the person's computer sent, and I do not use it as a path. A name with directories in it, or a name that collides with a file already on disk, should not be able to choose where the bytes land. The URL the journal remembers is the random name, served from the uploads folder. The browser's name is discarded.

The photographs on the published posts in this journal were added with the sample data, as files the API copies into that same folder on startup. They are ordinary cover URLs after that. Uploading your own, from the editor, goes through the same checks. Type, size, random name.

Leaving this note as a draft until I have decided how large a cover should be on the article page, and whether a missing cover should leave a blank band or simply no band at all. The list already does the second: if there is no image, the row is just the title and the extract. I like that better than a placeholder that pretends a photo exists.

The public journal will not show this piece. It is here so the dashboard has something unfinished, and so the rule about drafts is something you can see rather than only read about.

## What I still want to decide

A wide photograph looks right at the top of an essay and awkward in a narrow list. The home page currently uses the full width for the first result and a small frame for the rows under it. That split feels honest: the lead is the thing you might open, and the rest are titles you can scan. I do not want every row to become a banner.

There is also the question of what the image is for. A cover can illustrate the piece, or it can just make the page less like a wall of type. The sample photographs are quiet on purpose. They are desks, paper, a key, a room. None of them try to explain the essay. If a cover has to carry a caption to make sense, it is doing the title's job and doing it worse.

I will keep the type check strict. JPEG, PNG, WebP, and GIF are enough. A file that claims to be an image and is not should fail before it is written, which is what the content-type allow-list is for. The size cap is five megabytes. That is large for a cover and small enough that one upload cannot fill the disk by accident.

Until those choices feel settled, this stays a draft. The published essays already have their photographs. This note can wait.
""",
}
