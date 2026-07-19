# Site stack bake-off

Last updated: 2026-07-19

Living recipe for choosing the static site generator for the public archive.
Product contract: `docs/website.md`.
Content layout: `docs/content-model.md`.
Parked ideas: `docs/IDEAS.md`.

If this experiment is inconclusive, edit this file and re-run.
Do not delete `site/bakeoff/` trees unless explicitly asked.

## Task

Pick a tool (or small custom build) that turns file-backed `content/` into a
static public archive site for Basic Block Radio — browsable episodes and people,
readable depth, no CMS/database for v1.

WordPress stays live in parallel until later.
Design and compare against real episodes already in the repo.

## Considerations and constraints

Must weigh

- Fit to sibling episode YAML + Markdown under `content/` (not a CMS-shaped tree)
- Static HTML; deploy by publishing a folder
- Little or no client-side JavaScript; no analytics, tracking, or cookies
- Prefer self-hosted assets; no third-party runtime includes
- Minimize long-term dependency and CVE maintenance for a small team
- Prefer open source with broad community support; avoid single-vendor lock-in
  and paid “Pro” tiers for core workflow
- Comfortable local preview
- Episode cover art (YouTube / podcast square) stays outside the site build

Explicitly out of scope for this choice

- Node-based SSGs as the primary path (Eleventy, Astro, Next-style)
- Dynamic app architectures for the archive itself
- Build-time image resize/crop pipelines
- WordPress historical import driving the generator choice
- Rewriting existing Python editorial scripts into another language
  only to unify runtimes

Accepted glue

- Gitignored staging or in-memory projection from canonical `content/`
  into whatever shape the generator wants
- Public allowlist: episode YAML, shownotes, optional readable/transcript
- Never publish shorts or raw SRT

## Shortlist (four options)

1. Hugo + thin Python adapter (gitignored staging) — batteries, single binary,
   large community, Apache-2.0; Go templates; adapter for sibling YAML
2. Zola + thin Python adapter — single binary, Tera (Jinja-like) templates;
   smaller community than Hugo; same staging pattern
3. Pelican + custom reader — Python SSG; Jinja; custom reader for sibling layout;
   thinner community and quieter recent activity; AGPL
4. Custom Python + Jinja — read `content/` directly; smallest repo dependency set;
   own pagination and later RSS

Tools for the experiment must stay isolated under `site/bakeoff/`
(e.g. gitignored `.tools/` binaries and `.venv/`), not installed as lasting
system packages, so unused stacks can be wiped without contaminating the machine.

## Experiment

Goal: generate four comparable static sites from the same content and compare
them visually and ergonomically (setup friction, templates, willingness to maintain).
Scoring criteria are decided after seeing the outputs.

### Inputs

Episodes (all `status: ready`, with shownotes + readable + `url`):

- 221, 220, 219, 200

Sort: reverse episode number (221 → 200).

People: only those who appear in these episodes; link hosts/guests to person pages.
No organization pages.

### Information architecture

- Home `/` — feed of the two latest episodes (221, 220)
- `/page/2/` — next two (219, 200); pagination size = 2
- Episode pages `/eNNN/` (e.g. `/e220/`)
- Person pages for appearing people only
- No RSS in this spike

### Episode page shape

1. Show notes (HTML from `NNN-shownotes.md`)
2. Native `<details>` / `<summary>` with label `Полная расшифровка`
3. Revealed body = `NNN-readable.md` with timestamps kept
4. No full page reload; no extra JS if `<details>` is enough

### Presentation defaults

- One shared minimal CSS for all four stacks (system fonts; deliberately plain)
- `lang="ru"`
- No tracking; no third-party font or analytics CDNs
- Relative links so opening `public/index.html` via `file://` can work;
  optional `python3 -m http.server` in `public/` if needed

### Layout on disk

```text
site/bakeoff/
  README.md           # how to fetch tools, build each stack, wipe tools
  shared/             # shared CSS (and any shared copy)
  .tools/             # gitignored: Hugo and Zola release binaries
  .venv/              # gitignored: Pelican + Jinja Python env
  hugo/
  zola/
  pelican/
  custom/
```

Each stack writes its own `public/` (or equivalent) output directory.

### Procedure

1. Ensure bake-off tool isolation (binaries + venv under `site/bakeoff/`, gitignored).
2. Implement a thin shared content load or per-stack adapter/reader that
   selects only the four episodes and public-facing files.
3. Build all four sites with the IA and page shape above.
4. Open each `public/index.html` (or local static server) and compare.
5. Record the decision in `docs/website.md` (site stack section) when chosen.
6. Optionally delete only `.tools/` and `.venv/` to drop unused toolchains;
   keep bake-off project trees until explicitly asked to remove them.

### Re-run

Change this recipe first (episodes, pagination, URLs, stacks), then rebuild.
Treat `site/bakeoff/` as disposable experiment code until a winner is promoted
to the real `site/` project.
