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

- `NNN-episode.yml` — canonical metadata (title, status, dates, hosts/guests, media links)
- `NNN-shownotes.md` — full public article (same order/shape as on the website)
- `NNN-transcript.md` / `NNN-readable.md` / `NNN-shorts.md` / `NNN-raw.srt` — optional
- Every file name in the folder carries the episode number `NNN`
- No `depth` field; richness = which files exist
- `status`: `draft` | `ready` (`ready` = include in the public site build)

Person — `content/people/<slug>.md`

- Hosts and guests share one type
- Slugs are chosen manually; ASCII `a-z0-9` with hyphens; unique
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

links:
  audio: https://…
  youtube: https://…
```

Billed roles: `hosts` / `guests` match how the episode credits people (intro/title),
not a permanent staff roster. Zero guests allowed.

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

## Checker (planned)

- Filename episode number matches folder and `episode:` in `NNN-episode.yml`
- Show-notes first line equals `title`
- `title` starts with `ББ-{N}:`
- Appearance slugs resolve under `people/` / `organizations/`
- Implication rules (e.g. readable implies transcript)

## Prototype

`content/episodes/222/` is a fake structure sample (lorem ipsum), not a real publish package.
See `content/episodes/222/STRUCTURE.md`.
