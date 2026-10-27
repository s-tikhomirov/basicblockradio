# Site stack bake-off (concluded 2026-10-01: Zola selected)

Last updated: 2026-10-27

Zola and a thin Python adapter were selected
(decision in `docs/website.md`).
Hugo, Pelican, and custom were retired and their trees removed.
The site lives at `site/zola/`.
The stylesheet lives at `site/shared/site.css`.

Below is the July fixture recipe, kept as a historical record.
It describes 4 episodes, page size 2, and «Новее»/«Старее» labels.
v0.1 (see `docs/website.md`) builds the `ready` episodes with evolved chrome.
Every `site/bakeoff/` path below is that July layout.
Those directories are gone.

Product contract: `docs/website.md`.
Content layout: `docs/content-model.md`.
Parked ideas: `_tasks/tasks.md`.

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
- Public allowlist: episode YAML, shownotes, optional readable
- Never publish shorts or raw SRT (or transcript unless needed to derive readable;
  public episode page uses readable, not raw transcript)

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

### Inputs from content

Episodes (all `status: ready`, with shownotes + readable + `url`):

- 221, 220, 219, 200

Sort: reverse episode number (221 → 200).

People: only those who appear in these four episodes (hosts or guests).
Person pages at `people/{slug}/`.
Guests index lists only people with at least one guest appearance in this set.
No organization pages.

Do not publish: `NNN-shorts.md`, `NNN-raw.srt`, `NNN-raw-undiaried.srt`, `NNN-raw-diarized.txt`, or other non-public artifacts.

### Output URL map

Every stack must emit this tree (directory + `index.html` each):

```text
public/
  index.html                 # feed page 1
  page/2/index.html          # feed page 2
  e200/index.html
  e219/index.html
  e220/index.html
  e221/index.html
  guests/index.html
  people/{slug}/index.html   # one per appearing person
  about/index.html
  donate/index.html
  for-sponsors/index.html
  css/site.css               # copy of site/bakeoff/shared/site.css
```

Canonical path shapes (trailing-slash form; files are `…/index.html`):

| Path | Page |
| --- | --- |
| `/` | Episode feed, page 1 (221, 220) |
| `/page/2/` | Episode feed, page 2 (219, 200) |
| `/eNNN/` | Episode |
| `/guests/` | Guests index |
| `/people/{slug}/` | Person |
| `/about/` | О подкасте |
| `/donate/` | Поддержать |
| `/for-sponsors/` | Для спонсоров |

Pagination size = 2.
No separate `/episodes/` index; home is the feed.
No RSS in this spike.

### Site-wide chrome

Same on every page.

Header

- Brand title link: «Базовый блок» → home
- Tagline: «Подкаст про блокчейн» (exact; no extra archive subtitle)
- Top menu, this order and these labels:

  1. Выпуски → `/`
  2. Гости → `/guests/`
  3. О подкасте → `/about/`
  4. Поддержать → `/donate/`
  5. Для спонсоров → `/for-sponsors/`

Layout

- Main column + right sidebar (stack sidebar under main on narrow viewports)
- Shared CSS is frozen first: `site/bakeoff/shared/site.css`
  Every stack copies that file to `public/css/site.css`.
  Do not invent a second look; change the shared file only when this recipe changes.
  Required class names and chrome skeleton are listed at the top of that CSS file
  and in “Shared HTML skeleton” below.

Sidebar (every page)

- Heading: `Слушать подкаст`
- Text buttons (platform name as label), show-level URLs from the live homepage
  (not episode-specific):

  - Apple Podcasts → `https://podcasts.apple.com/ru/podcast/id1289965366`
  - Google Podcasts → `https://podcasts.google.com/?feed=aHR0cDovL2Jhc2ljYmxvY2tyYWRpby5saWJzeW4uY29tL3Jzcw`
  - Spotify → `https://open.spotify.com/show/4flYcruRigqZVPYBZRtMHa`
  - Яндекс Музыка → `https://music.yandex.ru/album/7638583`
  - YouTube → `https://www.youtube.com/channel/UC95bSmaFa7R33GOyi6VfyGQ`
  - RSS → `https://basicblockradio.libsyn.com/rss`

- Short note under buttons: «…и вообще везде, где вы слушаете что-то ещё»

Footer

- May note which bake-off stack built the page (e.g. `Bake-off: custom Python + Jinja`)

### Shared HTML skeleton

All stacks must emit this chrome (or equivalent with the same classes) so the
shared CSS applies without per-stack style forks:

```html
<div class="wrap">
  <header class="site">
    <h1><a href="…">Базовый блок</a></h1>
    <p>Подкаст про блокчейн</p>
    <nav class="menu" aria-label="Основное меню">
      <ul>
        <li><a href="…">Выпуски</a></li>
        <!-- Гости, О подкасте, Поддержать, Для спонсоров -->
      </ul>
    </nav>
  </header>
  <div class="layout">
    <main class="main"><!-- page body --></main>
    <aside class="sidebar" aria-label="Слушать подкаст">
      <h2>Слушать подкаст</h2>
      <ul class="listen">
        <li><a class="listen-btn" href="…">Apple Podcasts</a></li>
        <!-- remaining platforms -->
      </ul>
      <p class="listen-note">…и вообще везде, где вы слушаете что-то ещё</p>
    </aside>
  </div>
  <footer class="site">Bake-off: …</footer>
</div>
```

Body hooks: `nav.trail`, `ul.episode-list` / `.title` / `.meta`, `nav.pager`,
`.credits`, `section.embeds` / `.embed-youtube` / `.embed-libsyn`,
`article.shownotes`, `details.transcript` / `.readable`.

### Feed pages

- List episodes for that page only, newest first within the global sort
- Each row: full `title` (linked to `/eNNN/`), optional date
  (`publish_date` if set, else `recording_date` if not `unknown`),
  then linked people in appearance order (hosts then guests)
- Pager: «Новее» / «Старее» between `/` and `/page/2/` as appropriate

### Episode page

Top to bottom, fixed order:

1. Trail link back to feed («← Выпуски»)
2. Credits block:
   - First: `Гость:` or `Гости:` + linked guest name(s)
   - Then: `Ведущий:` or `Ведущие:` + linked host name(s)
   - Singular vs plural from count; names link to `/people/{slug}/`
3. Embeds section (bake-off fixture only; not yet in content model YAML):
   - YouTube iframe, then Libsyn audio iframe
   - Use the real episode embed IDs already wired in
     `site/bakeoff/custom/build.py` (`EMBEDS`) so all stacks look the same
   - Libsyn embed URL must keep empty `width//` (a literal `%` in the path breaks
     the player). Size the iframe with CSS.
4. Show notes HTML from `NNN-shownotes.md`
   - Markdown links must render as `<a>` (including podcast footer URLs)
5. `<details>` / `<summary>` with exact label `Полная расшифровка`
6. Inside details: HTML from `NNN-readable.md`, timestamps kept
7. No extra JS for the reveal

### Guests index

- Heading «Гости»
- One entry per guest in the bake-off set (not hosts-only people)
- Name → person page; list guest episode numbers linked to `/eNNN/`

### Person page

- Person `name` as heading
- Optional `links` from person frontmatter if present
- List of episodes they appear in (title linked), with role `ведущий` or `гость`

### Static chrome pages

Short Russian example copy lives in `site/bakeoff/custom/pages/`.
Other stacks should reuse the same Markdown (or identical HTML):

- `about.md` → `/about/`
- `donate.md` → `/donate/`
  (Patreon + Boosty real links; crypto as placeholders
  `YOUR_BTC_ADDRESS_HERE` / `YOUR_ETH_ADDRESS_HERE` — do not paste live wallet addresses)
- `for-sponsors.md` → `/for-sponsors/`

### Presentation and linking rules

- `lang="ru"` on `<html>`
- One shared minimal CSS; system fonts; deliberately plain
- No tracking; no third-party font or analytics CDNs
- Internal hrefs should end with `index.html` (e.g. `e221/index.html`, not only
  `e221/`) so Chrome `file://` navigation works; HTTP preview may also be used
- Relative links between pages (no absolute site origin required for local preview)
- Episode and show-note body links in Markdown must be real markdown links
  where clickability matters (podcast footer is markdown links, not bare URLs)

### Preview

Prefer `python3 -m http.server` from each stack’s `public/` when judging embeds
(YouTube / Libsyn iframes are unreliable under `file://`).
Opening `index.html` via `file://` should still navigate internal pages.

### Layout on disk (repo)

```text
site/bakeoff/
  README.md           # how to fetch tools, build each stack, wipe tools
  shared/
    site.css          # shared look for all stacks
  .tools/             # gitignored: Hugo and Zola release binaries
  .venv/              # gitignored: Pelican + Jinja Python env
  custom/             # reference stack (Python + Jinja) — already matches this recipe
  hugo/               # to implement against this recipe
  zola/
  pelican/
```

Each stack writes its own `public/` (gitignored).

### Closed

The four stacks were built from this recipe in July 2026.
Measurements are in `docs/site-stack-bakeoff-results.md`.
Zola was selected on 2026-10-01.
The bake-off directories were removed after that.
