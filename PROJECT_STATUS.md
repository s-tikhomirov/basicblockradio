# Project Status

Current episode processing workflow.
Full layout and status fields are in README.md.

## Pipeline

1. Generate SRT with Whisper (`medium`, Russian) → `NNN-raw.srt`
2. Pass 1: `srt-to-transcript` on SRT → `NNN-transcript.md` (paragraph boundaries, fillers, spelling; `status: raw`)
3. Human review of transcript → `status: edited`
4. Pass 2: `transcript-to-readable` on same blocks → `NNN-readable.md` (prose only, no merge/split; `status: readable`). Long episodes: `scripts/` split → per-chunk pass → merge.
5. Human review of readable → `status: reviewed`
6. Show notes from readable (manual today; `generate-shownotes` skill planned)

## Agent skills

- `srt-to-transcript` — pass 1: SRT to transcript; topic-based blocks; fillers and spelling; structure is final
- `transcript-to-readable` — pass 2: one line per transcript line; assertive within-block copy-edit; no merge or split

## Reference files for agents

- `.agents/dictionary.md` — terms and names
- `.agents/editing-standards.md` — shared rules
- `podcast-info.md` — hosts, format, tone

## Planned

- `generate-shownotes` skill
