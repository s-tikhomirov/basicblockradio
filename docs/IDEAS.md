# Ideas

Things to try, implement, or explore.
One-liners only; product decisions for the public site live in `docs/website.md`.

License: how to license repository with content and code (scripts)?
CC-BY is not well suited for code?
Add a separate license for scripts if needed.

Scripts: clarify if runs must start from a fixed directory.
Prefer invocations from repo root or any cwd with repo root resolved in one place.

Shorts: optional `content/episodes/templates/shorts-template.md`
mirroring the skill frontmatter if editors want a file scaffold beside shownotes.

Website search (Ctrl+K): after the public archive launches,
add an in-site command palette (Epicenter-style)
to search episodes, people, and later topics.
Build-time index over repo content is enough;
not required for the first website iteration.

Topics: after v1, add a curated topic vocabulary and episode filters
(subject labels, not old format rubrics or auto tag clouds).
Omit from the first website schema on purpose.

Episode file naming: every file in an episode folder carries the episode number
in its name (e.g. `222-shownotes.md`, `222-episode.yml`).
Deterministic checker must validate that the number is present and well-formed,
matches the parent directory name, and matches `episode:` inside `NNN-episode.yml`.

Title canon: full string `title` in `NNN-episode.yml` is authoritative for the site.
Checker should require show-notes first line to equal `title`,
and `title` to start with `ББ-{N}:` for that episode number.

People bios auto-injected into show notes or about pages: rejected for v1 as too rigid;
keep episode- and podcast-level prose hand-written.

Related episodes (`related_episodes` field or derived “also appeared in”): postpone past v1;
person pages can still list episodes by scanning appearances later.

Website track (separate projects if ever, not this brief’s design work):
internal CMS or multi-platform publisher;
finance or sponsor accounting;
manager control plane.

Dogfood decentralized tech for the podcast itself (explore later, not v1 website):
host the static site on IPFS (or similar) with a normal domain gateway in front;
mirror episode audio or full archive blobs on decentralized storage
(IPFS, Arweave, or similar) while keeping conventional hosting as the reliable path;
test whether RSS or listen links can point at content-addressed URLs in practice.

Decentralized social presence (explore later):
evaluate Mastodon, Bluesky (AT Protocol), or similar
for announcements and community alongside Telegram;
feasibility, reach for a Russian technical audience, and ops cost vs benefit.
