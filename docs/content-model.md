# Content model and repository layout

Last updated: 2026-07-19

Living description of how domain data is stored in this repository.
Product goals for the public site: `docs/website.md`.
Parked ideas: `docs/IDEAS.md`.

## Root layout

```text
content/                 # domain data (file-backed model)
  episodes/
  people/
  organizations/
  sponsorships/
site/                    # website project (build reads content/)
docs/                    # product and project writing
scripts/                 # deterministic tooling
.agents/                 # agent skills and editorial refs
README.md
podcast-info.md
```

## Entities

Episode — `content/episodes/NNN/`

Keep one episode folder (do not split into `public/` vs `internal/` subfolders).
Classify artifacts by role; the site build selects what may go live.

Public-facing (eligible for the site when `status: ready`)

- `NNN-episode.yml` — canonical metadata (title, status, dates, hosts/guests, url)
- `NNN-shownotes.md` — full public article (required for `ready`)
- `NNN-transcript.md` / `NNN-readable.md` — optional deep archive on the episode page

Editorial / non-public (stay in git; never copied into the public site output)

- `NNN-shorts.md` — editor map for Shorts/Reels (not a public page)
- `NNN-raw.srt` — Whisper input
- `.chunks/` — temporary readable-pipeline chunks (gitignored)

Every file name in the folder carries the episode number `NNN`.
No `depth` field; richness = which files exist.
`status`: `draft` | `ready` (`ready` = include in the public site build;
requires `NNN-shownotes.md` and `url`).

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
- Not a separate “sponsor org” tree

Topic / `related_episodes` — omitted in v1 (see `docs/IDEAS.md`).

## Episode YAML (v1)

```yaml
episode: 221
title: "ББ-221: …"          # full-string canon for the webpage
status: ready                 # draft | ready

recording_date: 2026-05-22
publish_date: 2026-07-03      # optional

hosts:
  - slug: sergei-tikhomirov
guests:
  - slug: mikhail-kudinov
    organization: blockstream # optional

url: https://basicblockradio.com/e221/   # canonical episode webpage
```

`url` is the only publication link in episode YAML (see `docs/website.md`).
When `status: ready`: `url` and `NNN-shownotes.md` are required; both optional while `draft`.

Billed roles: `hosts` / `guests` match how the episode credits people (intro/title),
not a permanent staff roster. Zero guests allowed.
Optional `organization` only on guest entries.

Organization records exist for joins; public org pages are not in v1 browse.

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
- `url` is an http(s) page URL; required when `status: ready`
- `NNN-shownotes.md` required when `status: ready`
- Implication rules (e.g. readable implies transcript)

## Prototype

`content/episodes/222/` is a fake structure sample (lorem ipsum), not a real publish package.
`status: draft` so it stays out of the public site build.
See `content/episodes/222/STRUCTURE.md`.

Golden real packages (full YAML + show notes + `url`, `status: ready`):
`content/episodes/220/`, `content/episodes/221/`.
