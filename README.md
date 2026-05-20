# Basic Block Radio

Knowledge base for the Basic Block Radio podcast — deep technical interviews about blockchain technologies in Russian.

## Repository Structure

```
├── README.md                          # This file
├── podcast-info.md                    # Podcast metadata
├── PROJECT_STATUS.md                  # Current workflow status
├── .agents/
│   ├── skills/
│   │   ├── edit-transcript/           # Convert SRT to edited transcript
│   │   └── transcript-to-readable/    # Polish transcript to readable version
│   ├── dictionary.md                  # Technical terms and spellings
│   └── editing-standards.md           # Common editing rules (years, etc)
└── episodes/
    ├── transcript-template.md         # Template for transcript files
    ├── shownotes-template.md          # Template for show notes files
    └── 001/
        ├── 001-transcript.md          # Edited transcript
        ├── 001-readable.md            # Polished readable version
        └── shownotes.md               # Show notes (summary, timecodes, links)
```

## Workflow

### Full Pipeline

1. Generate SRT: Run Whisper on audio to get `NNN-raw.srt`
   - Model: `medium` for best speed/quality balance on CPU
   - Use VAD filter with max duration 20s for stability

2. Run `edit-transcript` skill on the SRT file
   - AI converts SRT to transcript with speaker labels and timestamps
   - Output: `episodes/NNN/NNN-transcript.md`

3. Review and edit the transcript
   - Verify speaker labels
   - Confirm technical term spellings
   - Update frontmatter `status` to `edited`

4. Run `transcript-to-readable` skill on the edited transcript
   - AI polishes by removing fillers, merging by topic, restructuring
   - Output: `episodes/NNN/NNN-readable.md`

5. Review the readable version
   - Check that meaning is preserved
   - Verify years are formatted as 4 digits (2020, not 20)
   - Update frontmatter `status` to `reviewed` when satisfied

### Show Notes Creation (manual or TBD skill)

1. Copy `episodes/shownotes-template.md` to `episodes/NNN/shownotes.md`
2. Fill in summary, timecodes, and links based on the readable transcript
3. AI assistance available via future skill (TBD)

## Episodes

Each episode is stored in a numbered directory containing:
- `NNN-transcript.md` — The edited transcript with timestamps and speaker labels
- `NNN-readable.md` — Polished readable version with merged paragraphs
- `shownotes.md` — Summary, timecodes, and links (derived from readable version)

## Status Key

- `raw` — Initial Whisper output, unedited
- `edited` — Transcript has been reviewed and finalized
- `readable` — Readable version generated from edited transcript
- `reviewed` — Readable version has been checked and approved
