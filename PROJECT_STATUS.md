# Project Status

## 2026-05-20

### Current Approach - ON PAUSE

The dual-transcript comparison and merge workflow is currently on pause.

- Created `scripts/merge-srt.py` for automated merging of two SRT files
- Created `scripts/compare-srt.py` for manual diff review (legacy approach)
- Tested on episode 219 with `medium` + `distill-large-v3` models
- Issue encountered: `distill-large-v3` produced English translation instead of Russian transcription despite settings

Status: Waiting for clarity on alternative transcription sources before proceeding with dual-transcript approach.

### Active Method

Single raw SRT workflow (current):

1. Generate one SRT file using `medium` model (or other reliable model)
2. Use skill to convert SRT to paragraphs with timecodes
3. Edit transcript for quality

This is the working method until dual-transcript approach is resolved.

### Scripts Available

- `scripts/merge-srt.py` - Automated merge (ready but not in active use)
- `scripts/compare-srt.py` - Manual comparison (ready but not in active use)
- `scripts/apply-choices.py` - Apply manual choices (helper script)

### Next Steps (Pending)

- [ ] Resolve transcription model issue (distill-large-v3 translating instead of transcribing)
- [ ] Or identify alternative reliable model for Run 2
- [ ] Or decide to stay with single-transcript workflow permanently
- [ ] Document final workflow in README once approach is decided
