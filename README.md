# Basic Block Radio

Knowledge base for the Basic Block Radio podcast — deep technical interviews about blockchain technologies in Russian.

## Repository Structure

```
├── README.md                          # This file
├── podcast-info.md                    # Podcast metadata
├── .agents/
│   └── skills/
│       └── edit-transcript/           # Skill for transcript editing
└── episodes/
    ├── transcript-template.md         # Template for transcript files
    ├── shownotes-template.md          # Template for show notes files
    └── 001/
        ├── transcript.md              # Edited transcript
        └── shownotes.md               # Show notes (summary, timecodes, links)
```

## Workflow

### Transcript Editing

1. Copy `episodes/transcript-template.md` to `episodes/NNN/transcript.md`
2. Fill the frontmatter and paste the raw Whisper transcript
3. Run the `edit-transcript` skill with episode-specific context
4. Review and confirm changes
5. Update `status` to `edited` in frontmatter

### Show Notes Creation (manual or TBD skill)

1. Copy `episodes/shownotes-template.md` to `episodes/NNN/shownotes.md`
2. Fill in summary, timecodes, and links based on the edited transcript
3. AI assistance available via future skill (TBD)

## Episodes

Each episode is stored in a numbered directory containing:
- `transcript.md` — The edited transcript with frontmatter
- `shownotes.md` — Summary, timecodes, and links (derived from transcript)

## Status Key

- `raw` — Initial Whisper output, unedited
- `edited` — Transcript has been reviewed and finalized
