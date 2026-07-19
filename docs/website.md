# Website product brief

Last updated: 2026-07-19

Status key: decided means build against this until explicitly changed.
Open means safe to refine later.
Later means parked, not in the first website iteration.

This file is the living product contract for the public archive site.
It is for website and product work.
Transcript and show-notes skills do not need to load it for routine editorial tasks.

## Purpose

The site is a historical archive and learning resource for Basic Block Radio
(«Базовый блок»), not only a mirror of the podcast feed.

Primary bet: people come for navigation, readable depth, and cross-episode
exploration that isolated episodes on Telegram, YouTube, or a podcast app
do not provide well.

Secondary goal: own the textual record under our control so the archive
stays portable if a third-party platform or host goes away.

Today most community activity lives in Telegram and players.
The site does not need to replace that hangout.
It should win on explore and read, with clear listen and watch links.

## Scope

In scope for the website track in this repository:

- Historical episode archive
- Readable material (show notes, and deeper text when available)
- Topic-based filtering and guest pages
- Public site built from repo content files (no content database required for v1)

Out of scope for this track (do not design here; separate projects if ever):

- Internal CMS or admin login for publishing
- Finance or sponsor accounting
- Multi-platform publisher or manager control plane

Later evolution is allowed in principle (for example events or jobs, ZK-style)
but must not shape the v1 content model.

Parked product ideas that might return after launch live in `docs/IDEAS.md`.

## Content objects

Episode (primary)

- One show, identity includes number in the public URL
- Episode page is the main public source of truth for that episode
- Reverse-chronological feed of episodes

Guest (first-class pages)

- Dedicated page with short bio, personal or social links, and episodes appeared in
- Episode pages link to guests; guest pages link back to episodes
- Guests are worth visiting on their own

Topic (filter, not a rich object in v1)

- Curated labels on episodes (small set; not large auto-generated tag clouds)
- Clicking a topic shows a filtered episode list
- No maintained topic essay pages in v1
- Subject themes, not old format «рубрики» (livestream, paper, conference, …)

Company or project

- Optional later
- If used, treat affiliation as historical (as of recording), not a live org chart
- Do not promise up-to-date employment or rebrand tracking in v1

## Episode completeness

Two contracts.

Source completeness (repo)

- Canonical public description is the show-notes file plus frontmatter
- Identity: episode number, title, guest(s), hosts, recording date
- Body: intro or summary, timecodes, links, usual CTAs and sponsors as today
- Listen and watch URLs stored in a stable place (exact field layout is Phase B)
- Topics when the curated vocabulary exists
- Transcript and readable are deeper artifacts from the editorial pipeline;
  they complete the deep archive but are not required for every catalog stub

Public episode page

- Shows identity, show-notes intro, listen and watch, timecodes, links
- Shows hosts and guest links
- Shows topics when present
- Links into readable or transcript when those artifacts exist
- May present the same substance more cleanly than a raw paste of the Markdown file

Layout and widget mapping are not fixed in this brief.

## Depth policy

Launch without waiting for the full historical catalog to be deep.

Tier 1 (deep)

- New episodes going forward, plus a starter set of recent episodes
  (about 10–20 as resources allow)
- Full public checklist, including deeper text when the pipeline has produced it

Tier 2 (thin but real)

- Rest of the migrated catalog
- Number, title, date, guest(s) when known, listen and watch when known
- Optional short existing blurb; no transcript required
- Prefer a quiet absence of deep notes over loud undated «coming soon» on hundreds of pages

Tier 3 (upgrade)

- Thin episodes promoted to deep over time
- Cross-links by guest (and topic) work across deep and thin pages
  (for example a deep episode notes that the guest also appears in an older thin episode)

## Homepage

Job of the first screen (decided)

- Make clear what this place is
- Offer paths into recent or deep episodes and into browse
- Avoid feeling like only a blog post dump with a sidebar

Exact composition (open)

- Both a short positioning block then recent episodes (ZK-like)
  and a hero latest episode then recent then about (Epicenter-like) are acceptable
- Refine during actual design iterations

## Browse model (v1)

- Episode pages with episode number in the URL
- Reverse-chronological episode feed
- Guest pages with bidirectional links to episodes
- Topics as filters over the episode feed

Not in v1 browse

- Company pages
- Format rubrics as the main map
- In-site command palette search (see `docs/IDEAS.md`)

## Repository role

This private repository remains the home of editorial content and, later,
the public site project beside it (for example a `site/` directory).

Website direction docs live under `docs/`.
Agent skills and pipeline docs stay where they are;
they are author tooling, not public site pages.

## Open for Phase B

- Exact frontmatter and file layout for listen and watch URLs
- Guest as structured files or pages source
- Curated topic vocabulary and how topics are stored on episodes
- How thin historical stubs are imported from the current site
