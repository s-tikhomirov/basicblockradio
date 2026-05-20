# Basic Block Radio

Knowledge base for the Basic Block Radio podcast — deep technical interviews about blockchain technologies in Russian.

## Repository Structure

```
├── README.md                          # This file
├── podcast-info.md                    # Podcast metadata
├── PROJECT_STATUS.md                  # Current workflow status
├── .agents/
│   ├── skills/
│   │   └── edit-transcript/           # Skill for transcript editing
│   └── dictionary.md                  # Technical terms and spellings
└── episodes/
    ├── transcript-template.md         # Template for transcript files
    ├── shownotes-template.md          # Template for show notes files
    └── 001/
        ├── transcript.md              # Edited transcript
        └── shownotes.md               # Show notes (summary, timecodes, links)
```

## Workflow

### Transcript Pipeline

1. Generate SRT: Run Whisper on audio to get `NNN-raw.srt`
   - Model: `medium` for best speed/quality balance on CPU
   - Use VAD filter with max duration 20s for stability

2. Run skill: Use `edit-transcript` skill on the SRT file
   - Provide episode number, guest name, host names
   - AI converts SRT to transcript with speaker labels and timestamps
   - Output: `episodes/NNN/NNN-transcript.md`

3. Review and edit: Check the generated transcript for accuracy
   - Verify speaker labels
   - Confirm technical term spellings
   - Update frontmatter `status` to `edited`

See `PROJECT_STATUS.md` for workflow history and alternative approaches.

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
