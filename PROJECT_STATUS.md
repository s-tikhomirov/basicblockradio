# Project status

Current episode processing workflow.
Repository layout is in README.md.

## Pipeline

1. Whisper (`medium`, Russian) → `NNN-raw.srt`
2. `srt-to-transcript` → `NNN-transcript.md`
3. Human transcript review
4. `transcript-to-readable` → `NNN-readable.md`. Long episodes: `scripts/` split → per-chunk skill pass → merge.
5. Human readable review
6. `readable-to-shownotes` → `NNN-shownotes.md` (user URL list for `Ссылки:`; sponsors from `sponsors/current/`)
7. Optional: `transcript-to-shorts` → `NNN-shorts.md` (after step 3; can run in parallel with 4–6)

## Agent skills

- `srt-to-transcript` — SRT to transcript; structure and spelling; no readable rewrite
- `transcript-to-readable` — one line per transcript line; in-block copy-edit; chunked mode uses `scripts/`
- `readable-to-shownotes` — title, intro, timecodes, links, sponsors
- `transcript-to-shorts` — clip segments from transcript; frontmatter from transcript plus `source`

## Reference files

- `.agents/dictionary.md`
- `.agents/editing-standards.md`
- `podcast-info.md`
- `episodes/templates/transcript-template.md`
- `episodes/templates/shownotes-template.md`
- `sponsors/current/sponsor-*.md`

## In repo today

- Episodes with full long-form chain through show notes include 220 (and earlier pipeline work as committed).
- `transcript-to-shorts` used for 219 and 220 (`NNN-shorts.md`).

## Planned

- License split for content vs scripts (see IDEAS.md)
- Scripts runnable from any working directory with stable repo-root resolution
