# Project Status

## 2026-05-20

### Current Workflow (Active)

Four-step pipeline for episode processing:

1. Generate SRT: `whisper audio.mp3 --model medium --language ru`
2. Edit transcript: `edit-transcript` skill → `NNN-transcript.md`
3. Manual review: Verify and update `status: edited`
4. Create readable: `transcript-to-readable` skill → `NNN-readable.md`
5. Review readable: Verify and update `status: reviewed`

### New Skills Added

- `transcript-to-readable`: Aggressively polishes edited transcript by removing fillers, merging segments by topic, restructuring sentences for flow
- `.agents/editing-standards.md`: Repository-wide editing rules (year formatting, etc.)

### Updated Dictionary

- Added Cosmos vs космос distinction (Cosmos for blockchain, космос for space)

### Dual Transcript Approach - ON PAUSE

The dual-transcript comparison workflow was attempted but abandoned.

- Tested on episode 219 with `medium` + `distill-large-v3` models
- Issue: `distill-large-v3` produced English translation instead of Russian transcription

Status: Not pursuing further. Single-transcript AI skill workflow is working well.

### Next Steps

- [x] Document final workflow in README
- [x] Create `transcript-to-readable` skill
- [x] Create `editing-standards.md`
- [ ] Create `generate-shownotes` skill (future)
