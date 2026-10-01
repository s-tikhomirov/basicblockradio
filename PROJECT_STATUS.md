# Project status

Current episode processing workflow.
Repository layout and step-by-step instructions are in README.md.
Per-skill rules live only under `.agents/skills/*/SKILL.md`.

## Pipeline

1. Whisper (`medium`, Russian) → `NNN-raw.srt`
1a. When a separate diarized TXT exists: `diarize-srt` promotes Format B into `NNN-raw.srt` (Format A kept as `NNN-raw-undiaried.srt`)
2. `srt-to-transcript` → `NNN-transcript.md` (always from `NNN-raw.srt`)
3. Human transcript review (`expand-transcript-placeholders` for initials, empty `()`, and duplicate times) → `status: transcript-reviewed`
4. `transcript-to-readable` → `NNN-readable.md`. Long episodes: `scripts/` split → per-chunk skill pass → merge.
5. Human readable review → `status: readable-reviewed`
6. `readable-to-shownotes` → `NNN-shownotes.md` (user URL list for `Ссылки:`; sponsors from `content/sponsorships/`)
   Human review of show notes → `status: ready`
7. Optional: `transcript-to-shorts` → `NNN-shorts.md` (after step 3; can run in parallel with 4–6). Segment format and `Диапазон в выпуске` rules are in the shorts skill only.

## Batch runs

Multi-episode coordinator flow: `pipeline-launch.md` (pre-flight, worker layout).
When `NNN-raw-diarized.txt` exists, run `diarize-srt` before `srt-to-transcript` and pass `speaker_map` for export labels.

## Agent skills

One-line pointers only — invoke the matching `SKILL.md` for scope, inputs, and checklists.

- `diarize-srt` — merge Format A SRT + diarized TXT; promote Format B into `NNN-raw.srt`
- `srt-to-transcript` — SRT to transcript; structure and spelling; no readable rewrite
- `expand-transcript-placeholders` — expand speaker initials, fill empty `()`, and spread duplicate timestamps during transcript review
- `transcript-to-readable` — one line per transcript line; in-block copy-edit; chunked mode uses `scripts/`
- `readable-to-shownotes` — title, intro, timecodes, user URL list for `Ссылки:`, sponsors
- `transcript-to-shorts` — verbatim clip map from transcript; not from readable

## Reference files

- `.agents/dictionary.md`
- `.agents/editing-standards.md`
- `podcast-info.md`
- `docs/content-model.md`
- `content/episodes/templates/episode-template.yml`
- `content/episodes/templates/transcript-template.md`
- `content/episodes/templates/shownotes-template.md`
- `content/sponsorships/*.md`
- `content/people/`, `content/organizations/`

## In repo today

- Episodes 200–223: all `status: ready` with transcript, readable,
  shownotes, `url`, `youtube_url`, and publication dates.
- `NNN-shorts.md` present for 200, 211, 219, 220, 221, 223 (older files may predate current `Диапазон в выпуске` rules; regenerate or fix when re-editing clips).
- Website v0.1: Zola build over the full catalog (see `docs/website.md`).
  Other bake-off stacks retired; only `site/bakeoff/zola/` remains.

Open and parked work lives in `_tasks/tasks.md`.
