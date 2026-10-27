# Content model and repository layout

Last updated: 2026-10-27

Living description of how domain data is stored in this repository.
Product goals for the public site: `docs/website.md`.
Parked ideas: `_tasks/tasks.md`.

## Root layout

```text
content/                 # domain data (file-backed model)
  articles/
  episodes/
  people/
  organizations/
  sponsorships/
site/                    # website project (build reads content/)
docs/                    # product and project writing
_tasks/                  # work tracking (see meta task tracking)
scripts/                 # deterministic tooling
.agents/                 # agent skills and editorial refs
README.md
podcast-info.md
```

## Entities

Episode — `content/episodes/NNN/`

Keep one episode folder (do not split into `public/` vs `internal/` subfolders).
Classify artifacts by role; the site build selects what may go live.

Public-facing (eligible for the site when `status` is `ready` or `catalog`)

- `NNN-episode.yml` — canonical metadata (title, status, dates, hosts/guests, url)
- `NNN-shownotes.md` — full public article (required for `ready` and `catalog`)
- `NNN-transcript.md` / `NNN-readable.md` — optional deep archive on the episode page

Editorial / non-public (stay in git; never copied into the public site output)

- `NNN-shorts.md` — editor map for Shorts/Reels (not a public page)
- `NNN-raw.srt` — canonical raw for `srt-to-transcript` (Whisper Format A, or Format B after `diarize-srt`)
- `NNN-raw-diarized.txt` — optional speaker-track export for `diarize-srt`
- `NNN-raw-undiaried.srt` — Format A preserved when `diarize-srt` rewrites `NNN-raw.srt`
- `.chunks/` — temporary readable-pipeline chunks (gitignored)

Every file name in the folder carries the episode number `NNN`.
No `depth` field; richness = which files exist.
`status`: `draft` | `transcript-reviewed` | `readable-reviewed` | `ready` | `catalog`.
The public site build includes `ready` and `catalog`.
`ready` requires `NNN-readable.md`, `NNN-shownotes.md`, and `url`.
`catalog` requires `NNN-shownotes.md`.
`url` is the canonical page address when the episode has one.
A `catalog` episode stays `catalog` while a transcript is added,
and becomes `ready` after that transcript and a readable file are reviewed.

Site build may use a two-stage flow: (1) project only public-facing inputs into a
gitignored staging tree shaped for the SSG, or load them in memory; (2) generate HTML.
Staging is derived output, not a second source of truth — do not maintain duplicate
readable/shownotes under `content/` for the site.

Person — `content/people/<slug>.md`

- Hosts and guests share one type
- Slugs are chosen manually; ASCII `a-z0-9` with hyphens; unique
- Frontmatter: `slug`, `name`, optional `links` (`website`, `x`, `github`, `telegram`, `linkedin`)
- Bios are not auto-injected into show notes in v1

Organization — `content/organizations/<slug>.yml`

- Companies, protocols, foundations, projects, …
- Guest appearance may set `organization:` slug (affiliation at recording)

Sponsorship — `content/sponsorships/{org}-{first}-{last}.md`

- Time-bounded contract: `organization`, `first_episode`, `last_episode`, ad copy
- `logo`: image path relative to `content/sponsorships/`
  (for example `logos/1inch.png`)
- The public site shows that logo on every page
  while the highest episode number in the build
  is inside `first_episode`..`last_episode`.
  The image links to the URL in `Shownotes line`.
  Patreon and Boosty stay on every page alongside those logos.
- Changing `first_episode` or `last_episode` leaves show notes
  already published in older episodes as they were written.
  The range decides the sidebar logo,
  and which new episode receives the sponsor line.
- Not a separate “sponsor org” tree

Topic / `related_episodes` — omitted in v1 (see `_tasks/tasks.md`).

## Episode YAML (v1)

```yaml
episode: 221
title: "ББ-221: …"          # full-string canon for the webpage
status: ready                 # draft | transcript-reviewed | readable-reviewed | ready | catalog

recording_date: 2026-05-22
publish_date: 2026-07-03      # optional

hosts:
  - slug: sergei-tikhomirov
guests:
  - slug: mikhail-kudinov
    organization: blockstream # optional

url: https://basicblockradio.com/e221/   # canonical episode webpage
```

`url` is the canonical episode webpage in episode YAML (see `docs/website.md`).
Optional `youtube_url` holds the episode's YouTube watch URL.
When `status: ready`: `url`, `NNN-readable.md`, and `NNN-shownotes.md` are required.
When `status: catalog`: `NNN-shownotes.md` is required.
`url` is the canonical page address when the episode has one.
`transcript-reviewed` requires `NNN-transcript.md`.
`readable-reviewed` requires transcript and readable.
Agents create YAML as `draft`. A human sets the next status after each review gate.

Billed roles: `hosts` / `guests` match how the episode credits people (intro/title),
not a permanent staff roster. Zero guests allowed.
Optional `organization` only on guest entries.

Organization records exist for joins; public org pages are not in v1 browse.

## Articles

`content/articles/index.md` is the «Статьи» page.
`content/articles/<slug>/article.md` is one article.
Files in `images/` are numbered in the order they appear in the article.
`images/sources.txt` records each filename, its caption, and the address the file was saved from.
Downloads that belong to an article live in `files/` next to `article.md`.
The public paths are `/articles/` and `/articles/<slug>/`.

## Show notes and the site

- `NNN-shownotes.md` is the article source of truth (may duplicate person/org/sponsor/CTA text).
- First line must match `title` in `NNN-episode.yml`.
- Site build: article ← show notes; chrome ← episode YAML (+ optional readable/transcript).
- Compose of repeatable blocks is content-side (`scripts/` / editorial), not HTML join magic.

## Speech artifacts

Minimal frontmatter only:

```yaml
---
episode: 221
---
```

Shorts may add `source: 221-transcript.md`.

## Checker

Run from repo root: `python3 scripts/check_content.py`

- Filename episode number matches folder and `episode:` in `NNN-episode.yml`
- Show-notes first line equals `title`
- `title` starts with `ББ-{N}:`
- Appearance slugs resolve under `people/` / `organizations/`
- `url` is an http(s) page URL; required when `status` is `ready`
- `youtube_url`, when present, is an http(s) URL
- `NNN-shownotes.md` and `NNN-readable.md` required when `status: ready`
- `NNN-shownotes.md` required when `status: catalog`
- `NNN-transcript.md` required when `status` is `transcript-reviewed` or later
- Implication rules (e.g. readable implies transcript)

Golden real packages (full YAML + show notes + `url`, `status: ready`):
`content/episodes/220/`, `content/episodes/221/`.
