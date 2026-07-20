# Episode 420 structure prototype

Fake content for discussing folder layout only.
Not a real ББ-420 publish package.
See `docs/content-model.md` for the full model.

## Entities

- Episode — this folder (`420-episode.yml` + narrative/speech files)
- Person — `content/people/<slug>.md`
- Organization — `content/organizations/<slug>.yml`
- Sponsorship — `content/sponsorships/`
- Topic — omitted in v1

## Files in this folder

`420-episode.yml` — episode attributes and billed `hosts:` / `guests:`.
Canonical full-string `title`. `status`: `draft` | `ready`.

`420-shownotes.md` — full public article document (no YAML frontmatter).
First line matches `title`.

`420-transcript.md` / `420-readable.md` / `420-shorts.md` — speech artifacts.
Minimal frontmatter: `episode: 420` (+ `source` on shorts).

## Related fake records

- `content/people/sergei-tikhomirov.md`
- `content/people/alexander-seleznev.md`
- `content/people/ivan-primerskiy.md`
- `content/organizations/example-protocol.yml`
