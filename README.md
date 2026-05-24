# Basic Block Radio

Knowledge base for the Basic Block Radio podcast — deep technical interviews about blockchain technologies in Russian.

## Repository Structure

```
├── README.md                          # This file
├── podcast-info.md                    # Podcast metadata
├── PROJECT_STATUS.md                  # Workflow notes and history
├── scripts/
│   ├── split_transcript_chunks.py     # Pass 2: mechanical chunk split
│   ├── merge_readable_chunks.py       # Pass 2: concatenate chunk readables
│   └── transcript_io.py               # Shared parser (structure only)
├── .agents/
│   ├── skills/
│   │   ├── srt-to-transcript/         # Convert SRT to transcript
│   │   ├── transcript-to-readable/    # Transcript → readable direct speech
│   │   └── readable-to-shownotes/     # Readable → show notes (title, intro, timecodes)
│   ├── dictionary.md                  # Technical terms and spellings
│   └── editing-standards.md           # Common editing rules (years, etc)
└── episodes/
    ├── templates/
    │   ├── transcript-template.md     # Transcript and readable frontmatter
    │   └── shownotes-template.md      # Show notes file scaffold
    └── 001/
        ├── 001-raw.srt                # Whisper output (optional in repo)
        ├── 001-transcript.md          # Edited transcript
        ├── 001-readable.md            # Readable version (canonical)
        └── NNN-shownotes.md           # Show notes (summary, timecodes, links)
```

## Workflow

### Full Pipeline

1. Generate SRT: Run Whisper on audio to get `NNN-raw.srt`
   - Model: `medium` for best speed/quality balance on CPU
   - Use VAD filter with max duration 20s for stability

2. Run `srt-to-transcript` skill on the SRT file (pass 1 — structure)
   - Builds timestamped paragraphs from SRT (topic and turn boundaries; soft duration guide, not a hard cap)
   - Speaker labels, dictionary spellings, noise filler removal
   - Does not do readable-style sentence rewriting
   - Output: `episodes/NNN/NNN-transcript.md` (frontmatter `status: raw`)

3. Review and edit the transcript
   - Verify speaker labels and block boundaries
   - Confirm technical term spellings (see `.agents/dictionary.md`)
   - Set frontmatter `status` to `edited` when the transcript is finalized

4. Run `transcript-to-readable` skill on `NNN-transcript.md` (pass 2 — prose)
   - Input should be reviewed transcript (`status: edited`)
   - One output line per input line (same timestamps and speakers; no merging or splitting blocks)
   - Copy-edit within each block (flow, grammar, leftover fillers and speech redundancy); same timestamps, no merge/split
   - Long episodes (roughly more than 50 blocks or 45 minutes span): use chunked mode — `scripts/split_transcript_chunks.py` → polish each chunk → `scripts/merge_readable_chunks.py`; no hand-picked line ranges
   - Chunk artifacts live under `episodes/NNN/.chunks/` (gitignored)
   - Output: `episodes/NNN/NNN-readable.md` (frontmatter `status: readable`)
   - Skill details: `.agents/skills/transcript-to-readable/SKILL.md`

5. Review the readable version
   - Check that meaning is preserved
   - Verify years per `.agents/editing-standards.md` (2020, not 20)
   - Set frontmatter `status` to `reviewed` when satisfied

### Show Notes Creation

1. Ensure `NNN-readable.md` is reviewed (`status: reviewed` recommended).
2. Run `readable-to-shownotes` on the readable file → `episodes/NNN/NNN-shownotes.md`
3. Human review. Pass a raw URL list into `readable-to-shownotes` for `Ссылки:` (or complete links in a follow-up run). `Спасибо нашим спонсорам!` comes from `sponsors/current/` (shuffled).
4. Skill: `.agents/skills/readable-to-shownotes/SKILL.md`

## Episodes

Each episode lives in a numbered directory. Standard artifacts:

- `NNN-raw.srt` — Whisper subtitles (optional to keep in repo)
- `NNN-transcript.md` — Transcript with timestamps and speaker labels
- `NNN-readable.md` — Canonical readable version (same blocks as transcript, cleaner prose)
- `NNN-shownotes.md` — Summary, timecodes, and links (from readable version)

Use one canonical `NNN-readable.md` per episode after review. Extra readable drafts, if kept for comparison, are outside the pipeline and not required.

## Status Key

Transcript file (`NNN-transcript.md`):

- `raw` — Produced from SRT; not yet fully reviewed
- `edited` — Human-reviewed; ready for `transcript-to-readable`

Readable file (`NNN-readable.md`):

- `readable` — Generated from transcript; awaiting review
- `reviewed` — Checked and approved for show notes and publication use
