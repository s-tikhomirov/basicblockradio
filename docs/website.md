# Website product brief

Last updated: 2026-11-16

Status key: decided means build against this until explicitly changed.
Open means safe to refine later.
Later means parked, not in the first website iteration.

This file is the living product contract for the public archive site.
It is for website and product work.
Transcript and show-notes skills do not need to load it for routine editorial tasks.

## Purpose

The site is a historical archive and learning resource for Basic Block Radio
(«Базовый Блок»), not only a mirror of the podcast feed.

Primary bet: people come for navigation, readable depth, and cross-episode
exploration that isolated episodes on Telegram, YouTube, or a podcast app
do not provide well.

Secondary goal: own the textual record under our control so the archive
stays portable if a third-party platform or host goes away.

Today most community activity lives in Telegram and players.
The site does not need to replace that hangout.
It should win on explore and read, with clear listen and watch links.

Trust and simplicity (decided attitude)

- No tracking pixels, analytics SDKs, or marketing cookies on the public site for v1.
  We do not need them for the archive job; omit rather than “consent banner then track.”
- Prefer static HTML with little or no client-side JavaScript.
- Prefer fewer build-time dependencies and third-party runtime includes
  (fonts, embeds, tag managers) so maintenance and supply-chain risk stay low.
- This matches an audience that cares about privacy and decentralization;
  it is also plain operational hygiene for a small long-lived archive.

## Scope

In scope for the website track in this repository:

- Historical episode archive
- Readable material (show notes, and deeper text when available)
- Person pages (`people/`) and episode ↔ person links
- Public site built from repo content files (no content database required for v1)

Out of scope for this track (do not design here; separate projects if ever):

- Internal CMS or admin login for publishing
- Finance or sponsor accounting
- Multi-platform publisher or manager control plane

Later evolution is allowed in principle (for example events or jobs, ZK-style)
but must not shape the v1 content model.

Parked product ideas that might return after launch live in `_tasks/tasks.md`.

## Content objects

Episode (primary)

- One show, identity includes number in the public URL
- Episode page is the main public source of truth for that episode
- Reverse-chronological feed of episodes
- Canonical title is the full string `title` in `NNN-episode.yml`
  (usual shape: `ББ-{N}: {Guest} ({Organization}) …`)
- Webpage title and headings use that string
- Show-notes first line should match `title` (enforced by checker later)
- Title is authored; number/guest/org are not auto-assembled into the title in v1
- `status`: `draft` | `transcript-reviewed` | `readable-reviewed` | `ready` | `catalog`
  (`ready` and `catalog` are included in the public site build; earlier values stay in the repo)
- No `depth` field; richness follows which files and fields exist

Person (first-class records; hosts and guests share one type)

- Stored under `content/people/`; referenced from episodes by slug
- Episode appearances use billed roles in `NNN-episode.yml`:
  `hosts:` and `guests:` lists (slug each; optional `organization` on a guest)
- Billed = how this episode credits them (intro/title), not the permanent host roster
- Zero guests allowed; one or many hosts/guests allowed
- Person bios are not auto-injected into show notes or about pages in v1
  (episode- and podcast-level prose stays hand-written for flexibility)

Topic

- Omitted from v1
- Add later as a controlled vocabulary and episode filters (see `_tasks/tasks.md`)

Organization (company, protocol, foundation, project, …)

- Stored as `content/organizations/<slug>.yml` with name and URL
- Appearances on an episode may reference `organization` slug at recording time
- Show notes may duplicate org/person URLs; person/org records remain the structured home

## Episode completeness

Two contracts.

Source completeness (repo)

- Canonical metadata in `NNN-episode.yml`; public narrative in show notes
- Identity: episode number, full-string `title`, guests, hosts, recording date
- Body: intro or summary, timecodes, links, usual CTAs and sponsors as today
- Canonical episode page `url` in episode metadata
- Transcript and readable are deeper artifacts from the editorial pipeline;
  they complete the deep archive but are not required for every catalog stub

Public episode page

- Article body comes from `NNN-shownotes.md` (same order/shape as the public article;
  may duplicate person/org/sponsor/CTA lines already known elsewhere — that is OK)
- Page chrome and structured data come from `NNN-episode.yml`
  (title, status, url, appearances → person/org pages)
- Optional extra section from `NNN-readable.md` (and/or transcript) when present
- Never publish `NNN-shorts.md`, `NNN-raw.srt`, `NNN-raw-undiaried.srt`, or `NNN-raw-diarized.txt` (editorial / pipeline only)
- Compose/fill of repeatable show-notes blocks is a content-side step
  (`scripts/` or editorial workflow), not the website generator’s job to invent prose
  by joining many sources at HTML build time

Build projection

- Accept thin glue: select public-facing episode files (and people/orgs) into a
  gitignored staging area or an in-memory model, then run the static generator
- Canonical files remain only under `content/`; staging is disposable

Layout and widget mapping are not fixed in this brief.

## Catalog richness and site inclusion

Launch without waiting for every historical episode to have full text artifacts.

Site inclusion

- Public build includes episodes with `status: ready` or `status: catalog`
- `draft`, `transcript-reviewed`, and `readable-reviewed` stay out of the public build
  (optional local/preview flag may include them)
- `ready` requires `NNN-readable.md`, `NNN-shownotes.md`, and `url` (enforced by the checker)
- `catalog` requires `NNN-shownotes.md`
  A catalog episode is a historical page published from its show notes.
  `url` is the canonical page address when the episode has one.
  It becomes `ready` after a transcript and a readable file are reviewed.

Richness (no stored depth level)

- Whatever files exist are what the page can show
  (show notes, transcript, readable, shorts, …)
- Checker uses implication rules (e.g. readable implies transcript), not a level matrix
- Newer episodes add deeper artifacts over time; person cross-links work across catalog and full pages
- Prefer quiet absence of missing sections over undated «coming soon» on many pages

## Homepage

Job of the first screen (decided)

- Make clear what this place is
- Offer paths into recent or deep episodes and into the archive / people
- Avoid feeling like only a blog post dump with a sidebar

Exact composition

- Start with a simple layout (positioning + recent episodes + paths into archive/people)
- Refine against real episode content during design iterations; no need to freeze ZK- vs Epicenter-like up front

## Browse model (v1)

- Episode pages with episode number in the URL
- Reverse-chronological episode feed
- Person pages with bidirectional links to episodes

Not in v1 browse

- Topics / tag filters
- Organization pages (org YAML is data for guest joins only; no public org routes in v1)
- Format rubrics as the main map
- In-site command palette search (see `_tasks/tasks.md`)

## Repository role

Domain data lives under `content/`. The public site project lives under `site/`.
Layout details: `docs/content-model.md`.

Website direction docs live under `docs/`.
Agent skills and pipeline docs stay where they are;
they are author tooling, not public site pages.

## Episode `url` (v1)

One field: the canonical public webpage for the episode.

```yaml
url: https://basicblockradio.com/e221/
```

The live pages use `https://basicblockradio.com/eNNN/`.
Optional `youtube_url` holds the episode's YouTube watch URL; the site build
derives the player embed from it. Other platform listen links stay in show
notes when needed.
Required when `status: ready`; optional before that.

## Public site

Decided 2026-10-26.
The site has been served this way since the domain cutover.
Checked 2026-11-16.

The public site is the Zola build under `site/zola/`,
at https://basicblockradio.com.
HTTPS answers with the static archive.
The certificate is for `basicblockradio.com`.
Preview the same build locally.
Publishing steps are in `site/README.md`.

GitHub Pages serves the site from this public repository.
The Pages source is GitHub Actions.
DNS is published by Yandex (`dns1.yandex.net`, `dns2.yandex.net`).
Moving that DNS host is listed in `_tasks/tasks.md`.

The site keeps its current fonts and colors (`site/shared/site.css`).

Listening stays on the Libsyn RSS.
The sidebar links Apple Podcasts, Google Podcasts, Spotify,
Яндекс Музыка, YouTube, and that RSS.
The build also writes `/rss.xml`.

The header menu is Все выпуски, Гости, Чат, Статьи, О подкасте, and Для спонсоров.
Чат links to `https://t.me/basicblockradio_chat`.
«Статьи» is `/articles/`.
Article files are described in `docs/content-model.md`.

Every page links to Patreon and Boosty.
The donate page keeps Patreon, Boosty, and the BTC and ETH addresses.
Sponsor lines inside show notes stay in the episode body.
The sponsor logo on each page follows the rule in `docs/content-model.md`.

### Addresses

The build writes a page for each old address.
That page refreshes to the current one.

- `/for-sponsors-and-advertisers/` refreshes to `/for-sponsors/`
- `/ep099/` refreshes to `/e099/`
- `/ep212/` refreshes to `/e212/`
- `/https-basicblockradio-com-e214/` refreshes to `/e214/`
- `/https-basicblockradio-com-e215/` refreshes to `/e215/`
- `/best-of-basic-block-1/` refreshes to `/best-of-2020/`
- `/базовый-блок-лучшее-часть-2-из-4/` refreshes to `/best-of-2020/`
- `/базовый-блок-лучшее-часть-3-из-4/` refreshes to `/best-of-2020/`
- `/flash-attacks/` refreshes to `/articles/flash-attacks/`
- `/51-percent-attack/` refreshes to `/articles/51-percent-attack/`
- `/bitcoin-reformation/` refreshes to `/articles/bitcoin-reformation/`

`/all-episodes/` lists every published episode title, newest first.
`/e106b/`, `/e107b/`, and `/e119b/` stay at those addresses.

A missing address is the 404 page:
«Страница не найдена.» and a link to the main page.

### Kept pages

The about page shows the listener-review screenshot
saved at `content/pages/about-screenshot.png`.

`/best-of-2020/` is one page made from the three published parts of «Лучшее» (2020).
The old addresses refresh to that page.

`/bb-bonus-rms/` and `/ep100an/` stay at those addresses.
The two Stallman video files stay out of git.
Publishing those files is listed in `_tasks/tasks.md`.

## Site stack (decided 2026-10-01: Zola + thin Python adapter)

Selected: Zola with a thin Python adapter that projects `content/` into a
gitignored staging tree, then runs the pinned Zola binary.
Work tree: `site/zola/`.

Why Zola: all four bakeoff stacks reached full URL-map and visual parity
(`docs/site-stack-bakeoff-results.md`), so the choice came down to maintenance
burden. Zola's Tera templates mirror the reference implementation almost line
for line, its nested sections needed no config workarounds, and its slow
upstream cadence suits a build touched a few times a year. No strong reason
against it surfaced while building the full 24-episode catalog with it.

Retired as candidates: Hugo, Pelican, and custom Python + Jinja
(their bakeoff trees are removed; custom remains in git history only).
Full-site iteration continues on the Zola tree.

Bake-off record (concluded)

The July fixture is recorded in `docs/site-stack-bakeoff.md`.
The four-stack spike and its scoring are in
`docs/site-stack-bakeoff-results.md`.
The site implementation is `site/zola/`.

Decision criteria (unchanged): content-layout fit, static/privacy, OSS/non-commercial,
small supply-chain surface, local preview, glue vs batteries.

Episode artwork stays outside the site build (see below).

## v0.1 (2026-10-01)

First running version: Zola build over all 24 `ready` episodes (200–223),
previewed locally. Implemented beyond the July fixture:

- Full catalog, 8 episodes per feed page, pager «Позже» / «Раньше»
- Feed rows label `Гость:` then `Ведущий:` (singular/plural from count)
- Guests page lists episode titles; sort switch by first vs last name
  (two pre-rendered pages, no JavaScript)
- Episode players: Libsyn audio for all 24 (IDs mined from the Libsyn RSS),
  YouTube for all 24 via `youtube_url` in episode YAML
  (IDs matched against the channel RSS and title search;
  embeds use `youtube-nocookie.com`)
- AI transcript disclaimer on episode pages
- Static pages copied verbatim from basicblockradio.com
  (about, donate, for-sponsors)
- Site RSS (`/rss.xml`, enclosures with byte sizes), sitemap, robots.txt,
  kept `404.html`
- Meta descriptions and Open Graph tags (per-episode excerpts)
- Backfilled RSS publication dates into episodes lacking any date

Implementation notes for future agents

- Build entrypoint: `site/zola/adapt.py --out <dir>`;
  preview with `python3 -m http.server --directory <dir>`.
- The adapter hardcodes feed-derived maps (`_LIBYSN_IDS`, `_AUDIO`,
  `_PUBDATES`); refresh them from the Libsyn RSS if episodes are added.
- `youtube_url` in episode YAML is the home for video links;
  the adapter derives the embed URL. Never guess IDs, match channel titles.
- Standalone pages live in `content/pages/`.
  The adapter reads the `#` title and publishes each named file at `/<name>/`.
- The Zola project is `site/zola/`.
  `site/shared/` holds the stylesheet and logo.
  Tool binary, venv, staging, and output stay gitignored.

## Open for Phase B

- Content-side compose helper for repeatable show-notes blocks (optional)
- Public organization pages after v1 (records stay data-only until then)