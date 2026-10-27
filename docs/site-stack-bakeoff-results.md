# Site stack bake-off results

Last updated: 2026-10-27

> Concluded 2026-10-01: Zola selected (see `docs/website.md` for rationale).
> Hugo, Pelican, and custom retired as candidates.
> Measurements below describe the July four-episode fixture.

Outcome of the four-stack spike against the recipe in `docs/site-stack-bakeoff.md`.
This records process metrics and parity checks from the July fixture.
The stack decision is in `docs/website.md`.

## How it was run

Coordinator chat spawned four parallel Grok sub-agents
(`cursor-grok-4.5-high-fast`), one per stack.
Each owned only `site/bakeoff/<stack>/` and read the shared recipe plus
`site/bakeoff/custom/` as the reference.

Inputs: episodes 221, 220, 219, 200 (reverse numeric sort).
Public allowlist: episode YAML, shownotes, readable.
Never published: shorts, raw SRT.

Tools used from local isolation only
(`site/bakeoff/.tools/hugo`, `site/bakeoff/.tools/zola`, `site/bakeoff/.venv/`).

## Per-stack outcome

All four reached recipe URL-map parity and passed smoke checks
(feed, page 2, one episode with embeds and readable details,
guests, person, about, donate, for-sponsors, listen sidebar).

| Stack | Status | Role | Build entrypoint |
| --- | --- | --- | --- |
| custom | done | reference (rebuild and verify) | `site/bakeoff/.venv/bin/python site/bakeoff/custom/build.py` |
| hugo | done | Hugo + thin Python adapter | `site/bakeoff/.venv/bin/python site/bakeoff/hugo/adapt.py` |
| zola | done | Zola + thin Python adapter | `site/bakeoff/.venv/bin/python site/bakeoff/zola/adapt.py` |
| pelican | done | Pelican + custom reader or plugin | `site/bakeoff/.venv/bin/python site/bakeoff/pelican/build.py` |

Each stack had its own README next to the code.
Those trees are removed.

## Agent wall time

Time for each sub-agent to implement or verify and finish
(Cursor `turnDurationMs`, matches transcript birth to mtime).

| Stack | Agent wall time | Notes |
| --- | --- | --- |
| custom | 32 s | Reference already matched; regenerated `public/` only |
| pelican | 1 m 54 s | New stack |
| zola | 3 m 25 s | New stack |
| hugo | 4 m 4 s | New stack |

Parallel calendar time from first launch to last finish: about 4 m 9 s.

## Generator rebuild time

Wall time of the site build command alone (re-timed after the spike):

| Stack | Rebuild wall time |
| --- | --- |
| zola | 0.18 s |
| custom | 0.23 s |
| hugo | 0.27 s |
| pelican | 0.29 s |

All are sub-second for this four-episode fixture.
Generator speed is not a differentiator at current scale.

## Approx token cost

Cursor did not persist cumulative billed input or output tokens for these
Grok sub-agent runs (`usageData` empty; bubble `tokenCount` all zero).

What is available is peak context window size at end of each run
(not billable total across turns):

| Stack | Peak context tokens | Share of 256k limit |
| --- | --- | --- |
| custom | 37,052 | 14.5% |
| pelican | 65,697 | 25.7% |
| zola | 74,920 | 29.3% |
| hugo | 85,428 | 33.4% |

Rough effort ranking from wall time and peak context
(same order either way): custom ≪ pelican < zola < hugo.

Treat peak context as a lower-bound proxy for prompt weight, not spend.
A fair token-cost comparison would need Cursor or provider billing export
for the four composer IDs.

## Resulting websites (`public/`)

Route trees match.
Each site has 17 files (16 HTML + shared CSS) and 19 directories
(including root). Max directory nesting is 2
(`people/{slug}/`, `page/2/`).

| Stack | Files | Total size |
| --- | --- | --- |
| custom | 17 | 564,295 B (~551 KiB) |
| hugo | 17 | 564,078 B (~551 KiB) |
| zola | 17 | 562,159 B (~549 KiB) |
| pelican | 17 | 560,985 B (~548 KiB) |

Spread between largest and smallest is about 3.3 KiB (0.6%).
Differences are HTML whitespace and minor renderer markup
(for example Hugo heading ids or generator meta), not IA.

`public/css/site.css` is byte-identical to `site/bakeoff/shared/site.css`
in all four trees.

## Implementation complexity

Source trees only (excluding `public/` and `.build/`):

| Stack | Source files | Source dirs | Source bytes | Max nesting |
| --- | --- | --- | --- | --- |
| custom | 10 | 3 | 22,018 | 1 |
| zola | 10 | 2 | 22,105 | 1 |
| hugo | 11 | 7 | 21,876 | 2 |
| pelican | 13 | 7 | 22,072 | 3 |

Pelican is deepest (plugin plus theme layouts).
Hugo next (layouts tree).
Custom and Zola stay flatter.
Source byte counts are close; nesting and file count carry more signal
than size.

## Glue and quirks worth remembering

- Hugo and Zola emit extra routes (`/page/1/`, Zola also `404.html`).
  Adapters delete those after build so `public/` matches the recipe map.
- Hugo 0.164 ignored root path keys declared after a `[pagination]` table;
  path keys must come first in `hugo.toml`.
- Relative `…/index.html` links (needed for `file://`) required extra care
  in Hugo and Zola (`get_url` / RelPermalink alone are not enough).
- Zola pre-renders shownotes, readable, and static Markdown in the Python
  adapter (same extensions as custom) to avoid renderer drift.
- Pelican HTML matches IA; whitespace differs via Jinja trim settings.
- Chrome Markdown under `site/bakeoff/custom/pages/` links people as
  `../people/{slug}/` without `index.html` (inherited by all stacks).

## After the spike

The stack decision is in `docs/website.md`.
The bake-off trees are removed.
The site is `site/zola/`.
The stylesheet is `site/shared/site.css`.
