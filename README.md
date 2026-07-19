# Basic Block Radio

Knowledge base for the Basic Block Radio podcast — deep technical interviews about blockchain technologies in Russian.

- Content model and folder layout: `docs/content-model.md`
- Public website product brief: `docs/website.md`
- Parked ideas: `docs/IDEAS.md`

## Repository structure

```
├── README.md
├── podcast-info.md
├── PROJECT_STATUS.md
├── pipeline-launch.md
├── docs/
│   ├── content-model.md            # Data model and layout (source of truth)
│   ├── website.md                  # Public archive product brief
│   └── IDEAS.md
├── content/
│   ├── episodes/
│   │   ├── templates/
│   │   │   ├── episode-template.yml
│   │   │   ├── transcript-template.md
│   │   │   └── shownotes-template.md
│   │   └── NNN/
│   │       ├── NNN-episode.yml     # Canonical episode metadata
│   │       ├── NNN-raw.srt
│   │       ├── NNN-transcript.md
│   │       ├── NNN-readable.md
│   │       ├── NNN-shownotes.md    # Full public article
│   │       ├── NNN-shorts.md
│   │       └── .chunks/
│   ├── people/
│   ├── organizations/
│   └── sponsorships/
├── site/                           # Website project (not implemented yet)
├── scripts/
└── .agents/
    ├── skills/
    ├── dictionary.md
    └── editing-standards.md
```

## Workflow overview

Two deliverable tracks share the same transcript. Long-form publication uses readable + show notes. Short-form clips use the transcript only (verbatim excerpts with montage elisions).

```mermaid
flowchart LR
  SRT[NNN-raw.srt]
  T[NNN-transcript.md]
  R[NNN-readable.md]
  SN[NNN-shownotes.md]
  SH[NNN-shorts.md]
  Y[NNN-episode.yml]
  SRT -->|srt-to-transcript| T
  T -->|human review| T
  T -->|transcript-to-readable| R
  R -->|human review| R
  R -->|readable-to-shownotes| SN
  T -->|transcript-to-shorts| SH
  Y -.->|title status hosts guests links| SN
```

Run one agent skill per step unless the user asks to combine steps. Each skill file under `.agents/skills/` defines scope, inputs, and stop conditions.

## Step by step

### 1. Subtitles

Generate `content/episodes/NNN/NNN-raw.srt` with Whisper on the episode audio.

- Model `medium` is a practical CPU choice for Russian.
- VAD filter with max segment duration around 20s improves stability.

### 2. Transcript (pass 1)

Run the `srt-to-transcript` skill on the SRT file.

- Timestamped paragraphs, speaker labels, dictionary spellings, light filler cleanup.
- Does not rewrite for readable prose.
- Output `content/episodes/NNN/NNN-transcript.md` (frontmatter: `episode` only).
- Create or update `NNN-episode.yml` for identity (hosts/guests slugs, dates, title when known).
- Sponsor lines in the recording can be aligned with `content/sponsorships/` when building the transcript.

Skill: `.agents/skills/srt-to-transcript/SKILL.md`

### 3. Transcript review

Human review of `NNN-transcript.md`.

- Speakers, boundaries, technical terms (`.agents/dictionary.md`).
- When satisfied, run downstream skills on this file.

### 4. Readable (pass 2)

Run `transcript-to-readable` on the reviewed `NNN-transcript.md`.

- One output line per input line (same timestamps and speakers; no merge or split).
- Copy-edit inside each block only.
- Long episodes: `scripts/split_transcript_chunks.py`, polish each chunk, then `scripts/merge_readable_chunks.py`. Chunk dirs live under `content/episodes/NNN/.chunks/` (gitignored).
- Output `NNN-readable.md` with the same minimal frontmatter as the transcript (`episode` only).

Skill: `.agents/skills/transcript-to-readable/SKILL.md`

### 5. Readable review

Check meaning, years (`.agents/editing-standards.md`), and flow before show notes.

### 6. Show notes

Run `readable-to-shownotes` on `NNN-readable.md`.

- Output `NNN-shownotes.md` without YAML frontmatter (full article body).
- Title line must match `title` in `NNN-episode.yml`.
- Sponsors from `content/sponsorships/` active for this episode number; `Ссылки:` from a URL list the user provides.
- Human review before setting `status: ready` on the episode YAML.

Skill: `.agents/skills/readable-to-shownotes/SKILL.md`  
Template: `content/episodes/templates/shownotes-template.md`

### 7. Shorts (optional)

Run `transcript-to-shorts` on the reviewed `NNN-transcript.md` (parallel with readable once the transcript is reviewed).

- Output `NNN-shorts.md`. Clip text is verbatim from the transcript only, not from `NNN-readable.md`.
- Segment layout, montage rules, `Диапазон в выпуске`, and the pre-finish checklist are defined in the skill, not duplicated here.

Skill: `.agents/skills/transcript-to-shorts/SKILL.md`

## Agent skills

| Skill | Input | Output |
|-------|--------|--------|
| `srt-to-transcript` | `NNN-raw.srt` | `NNN-transcript.md` (+ `NNN-episode.yml` identity) |
| `transcript-to-readable` | `NNN-transcript.md` | `NNN-readable.md` |
| `readable-to-shownotes` | `NNN-readable.md` + URL list | `NNN-shownotes.md` |
| `transcript-to-shorts` | `NNN-transcript.md` | `NNN-shorts.md` |

Shared references: `.agents/dictionary.md`, `.agents/editing-standards.md`, `podcast-info.md`.

Scripts under `scripts/` are only for mechanical transcript chunking and merge during `transcript-to-readable`. Skills that process Russian episode text do not call those scripts unless the skill explicitly says so (`transcript-to-readable` chunked mode only).

## Episode artifacts

| File | Role |
|------|------|
| `NNN-episode.yml` | Canonical metadata (title, status, hosts/guests, links) |
| `NNN-raw.srt` | Whisper subtitles |
| `NNN-transcript.md` | Canonical spoken wording and timestamps |
| `NNN-readable.md` | Canonical long-form reading text |
| `NNN-shownotes.md` | Full public article for site / platforms |
| `NNN-shorts.md` | Editor map for Shorts, Reels, or clip cuts |

Use one reviewed `NNN-readable.md` per episode for publication. Extra drafts, if kept, are outside the pipeline.

## Frontmatter and metadata

- Identity lives in `NNN-episode.yml` (see `content/episodes/templates/episode-template.yml` and `docs/content-model.md`).
- Speech files use minimal frontmatter: `episode: NNN` only (`content/episodes/templates/transcript-template.md`).
- `NNN-shorts.md` adds `source: NNN-transcript.md`.
- `NNN-shownotes.md` has no YAML frontmatter; first line is the title string from `NNN-episode.yml`.

Review gates are human workflow steps in this README, not frontmatter values on speech files.
`status: draft | ready` on `NNN-episode.yml` controls inclusion in the public site build.
