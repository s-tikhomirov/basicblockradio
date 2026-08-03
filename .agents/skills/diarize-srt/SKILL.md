# diarize-srt

Merge an undiarized Format A Whisper SRT with a speaker-labeled diarized TXT export into Format B, and promote that into the canonical raw file `NNN-raw.srt`.
SRT wording and cue times are canonical.
TXT export labels are the speaker track — keep those strings as-is in the merged file.

## Scope

When this skill is invoked, complete only the work described here and stop.

- Promote Format B into `content/episodes/NNN/NNN-raw.srt` from Format A `NNN-raw.srt` + `NNN-raw-diarized.txt`
- Preserve the previous Format A as `NNN-raw-undiaried.srt`
- Run the helper aligner under this skill directory
- Summarize results in chat (labels, reconstructions, flagged timestamps)

## Purpose

Make `NNN-raw.srt` a Format B file so `srt-to-transcript` always reads that one path.

- Attach TXT speaker labels to each Format A cue
- Reconstruct clearly missing TXT-only turns as extra Format B blocks
- Preserve SRT text for all cues that exist in the SRT
- Surface hard cases as timestamps in the chat summary

## Input

Required in user prompt when invoking skill:

- Episode number (from `NNN-raw.srt` / `NNN-raw-diarized.txt`, or ask if unclear)

Files (convention under `content/episodes/NNN/`):

- `NNN-raw.srt` — Format A SubRip before this skill runs
- `NNN-raw-diarized.txt` — export turns `Label (M:SS)` or `Label (H:MM:SS)` then text

### Preconditions (stop and flag)

- Either input file missing → stop, say which path is missing
- `NNN-raw.srt` is already Format B (first non-empty line is a `[HH:MM:SS:ff - …]` bracket) → stop
- `NNN-raw-diarized.txt` missing or empty of labeled turns → stop

## Output

- `content/episodes/NNN/NNN-raw.srt` — Format B (canonical raw for `srt-to-transcript`)
- `content/episodes/NNN/NNN-raw-undiaried.srt` — preserved Format A from before promotion
- Chat summary only (no report file)

### Output block shape

One Format B block per SRT cue, plus any reconstructed TXT-only blocks.
First non-empty line is a bracket timestamp so `srt-to-transcript` auto-detects Format B:

```text
[00:00:06:08 - 00:00:14:50]
Sergei
Всем привет, с вами подкаст Базовый Блок, ...
```

- Time fields: `HH:MM:SS:ff` with `ff` = floor(milliseconds / 10) from the SRT cue (e.g. `084` → `08`)
- Speaker line: exact export label from the TXT
- Text: SRT cue text for SRT-backed blocks; TXT text for reconstructed blocks
- Blocks sorted by start time

## Helper script

Path: `.agents/skills/diarize-srt/scripts/align_diarization.py`

The script:

1. Parses Format A cues and TXT turns
2. Assigns a speaker to each SRT cue (time overlap primary, lexical overlap tie-break, prior-cue continuity if still weak)
3. Emits one Format B block per SRT cue
4. Reconstructs TXT turns whose wording is clearly absent from nearby SRT text
5. Moves Format A `NNN-raw.srt` → `NNN-raw-undiaried.srt`, then writes Format B to `NNN-raw.srt`
6. Prints a summary (labels, reconstructed count, flagged timestamps) on stdout

### Reconstructed TXT-only blocks

Principle: do not lose content.

When a TXT turn is clearly missing from the SRT (low coverage against overlapping or nearby cues):

- Emit a Format B block with that turn’s speaker and text
- Start = TXT turn start
- End = earlier of next SRT cue start and next TXT turn start after this turn’s start
- If that end is not after start, use start + 1s and flag the timestamp for manual check

### Hard cases

Best-effort reconcile (time + text + continuity).
If confidence is weak, still emit a best-effort speaker and flag the cue or turn start timestamp in the chat summary for manual check.

## Agent workflow

1. Resolve episode `NNN` and paths under `content/episodes/NNN/`
2. Check preconditions (both files present; `NNN-raw.srt` is Format A)
3. Run the helper from the knowledge-base root, e.g.

```bash
python3 .agents/skills/diarize-srt/scripts/align_diarization.py \
  --episode NNN
```

Or pass explicit paths (default `--out` is the same as `--srt`):

```bash
python3 .agents/skills/diarize-srt/scripts/align_diarization.py \
  --srt content/episodes/NNN/NNN-raw.srt \
  --txt content/episodes/NNN/NNN-raw-diarized.txt
```

4. Confirm `NNN-raw.srt` is Format B and `NNN-raw-undiaried.srt` exists
5. Paste a short chat summary from the script stdout
6. Stop

## Downstream

After this skill, `srt-to-transcript` takes `NNN-raw.srt` with a `speaker_map` from every export label to Cyrillic full names:

```text
speaker_map:
  Sergei: Сергей Тихомиров
  Ivan Ivanitskiy: Иван Иваницкий
  Alexander: Александр Селезнев
```

## Constraints

- DO keep SRT cue text unchanged in SRT-backed blocks
- DO keep TXT export speaker strings unchanged
- DO reconstruct clearly missing TXT-only turns
- DO flag weak alignments by timestamp in chat
- DO preserve Format A as `NNN-raw-undiaried.srt` when promoting into `NNN-raw.srt`
- DO NOT invent Cyrillic display names in the merged file
- DO NOT apply dictionary, filler, or sponsor edits
- DO NOT run `scripts/` under the knowledge-base root
- DO NOT write `NNN-transcript.md`, `NNN-readable.md`, or edit episode YAML
- DO NOT chain into other skills unless the user asks
- DO NOT treat the diarized TXT timestamps as more precise than the SRT
