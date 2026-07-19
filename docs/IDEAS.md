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

RSS: after the archive site exists, generate a podcast RSS feed from repo content
(episode metadata + enclosure URLs) so the textual site and the feed share one source.
Not required for the first website iteration.

Privacy-preserving metrics (only if ever needed): server log aggregates or a
self-hosted, cookieless counter — never third-party analytics on the public pages.
Default remains no metrics (see `docs/website.md`).

Self-hosted audio (explore later): store MP3s on our own object storage / CDN
and point RSS enclosures there, reducing or dropping reliance on Libsyn.
Feasible technically; trade-offs are bandwidth, CDN cost, Apple/Spotify/etc. directory
updates, and keeping analytics/redirects that a host like Libsyn provides today.

Episode artwork automation (sibling track, not the site generator): today a human
makes wide YouTube and square podcast covers from a template + guest photo + title;
square art is embedded in the MP3 for Spotify/Libsyn/etc. Later: scripts or agent
skills to speed that pipeline. Keep out of `site/` static HTML build.

Topics: after v1, add a curated topic vocabulary and episode filters
(subject labels, not old format rubrics or auto tag clouds).
Omit from the first website schema on purpose.

Episode file naming and title canon: enforced by `scripts/check_content.py`
(see `docs/content-model.md`).

People bios auto-injected into show notes or about pages: rejected for v1 as too rigid;
keep episode- and podcast-level prose hand-written.

Related episodes (`related_episodes` field or derived “also appeared in”): postpone past v1;
person pages can still list episodes by scanning appearances later.

WordPress historical import and domain cutover: after the new site MVP is agreed;
until then WP and this repo’s site track run in parallel (see `docs/website.md`).

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
