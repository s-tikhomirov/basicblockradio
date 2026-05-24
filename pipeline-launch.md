# Hold — do not run the full pipeline yet

Do not run this launch flow end-to-end (srt-to-transcript through readable and shorts) until diarization is solved.

In the current workflow, speaker labels in `NNN-transcript.md` are not reliable enough from srt-to-transcript alone.
A human must fix who said what in the transcript before any downstream skill uses it.

Until diarization is in place, treat readable and shorts as blocked on manual speaker review even if a transcript file exists.

---

# How to use

When you launch a batch, name the episode numbers in the same message (e.g. `210, 211, 212`).

Paste this entire file into a Cursor chat (multitask mode recommended), or tell the agent to read
`knowledge-bases/basicblockradio/pipeline-launch.md` and execute it.

The coordinator must complete pre-flight (below), wait for your answers, and wait until you explicitly say to start the pipeline before launching any background workers.

When you are ready to run workers after pre-flight, say explicitly: start the pipeline (or equivalent clear go-ahead).

---

# Basic Block Radio — episode batch launch

You are the coordinator for a batch of Basic Block Radio episode processing.
The user supplies the episode list for this run in their launch message.

Unless the user has removed or superseded the hold at the top of this file, do not launch the full pipeline.
If the user asks to start anyway, remind them of the diarization gap and that readable/shorts need manually corrected speaker labels in the transcript first.

## Pre-flight — gather info before workers

Do not launch srt-to-transcript, transcript-to-readable, or transcript-to-shorts workers until pre-flight is done and the user has explicitly instructed you to start the pipeline.

1. Confirm the episode list with the user if it was ambiguous or missing.
2. Read the Required / Input sections of each skill used in this pipeline:
   - `.agents/skills/srt-to-transcript/SKILL.md`
   - `.agents/skills/transcript-to-readable/SKILL.md`
   - `.agents/skills/transcript-to-shorts/SKILL.md`
3. Build a checklist of everything those skills require from the user (not from files on disk). At minimum for this pipeline, srt-to-transcript requires per episode:
   - guest name (who is interviewed)
   - host names (who asks questions; note who is present if not all hosts)
   Optional when known: `recording_date` in pre-flight (ISO `YYYY-MM-DD`). If the user does not supply it, the srt-to-transcript worker must write `unknown` in frontmatter — not omit the key, and not infer a date from SRT, filenames, paths, or file metadata. Episode-level dates in `podcast-info.md` count only when that file explicitly lists a date for that episode number.
   transcript-to-readable and transcript-to-shorts rely on transcript frontmatter after step 1; note any optional shorts preferences (segment count, themes) if the shorts skill lists them.
4. Ask the user in one clear message for all missing items, grouped by episode (table or bullet list). If the same hosts appear on every episode, ask once for hosts and per-episode guests only.
5. Stop and wait. Do not start workers, read SRT content for processing, or create output files until the user replies with the requested info.
6. After the user provides answers, record a brief per-episode metadata block (episode, guest, hosts, optional recording_date, optional shorts options). Summarize what will run and stop again.
7. Launch workers only after the user explicitly says to start the pipeline (or an unambiguous equivalent). Supplying metadata alone is not permission to start.

If the user cannot supply required speaker names for an episode, do not start workers for that episode; report which episode is blocked.

When workers launch, pass the pre-flight metadata slice into each srt-to-transcript worker prompt (guest, hosts, optional recording_date).

## One episode — full flow

For a single episode `<n>`, the full flow is three separate worker runs in dependency order:

1. srt-to-transcript — reads `episodes/<n>/<n>-raw.srt`, writes a transcript file in that episode directory.
2. transcript-to-readable — reads that episode's transcript only; writes readable output in the same directory.
3. transcript-to-shorts — reads the same transcript; writes shorts output in the same directory.

Steps 2 and 3 do not depend on each other, but both require step 1 to have finished and the transcript file to exist on disk.

Each of those three steps must be its own fresh background worker (no chaining in one session).
That gives three workers per episode, with a clean context window for each skill.

## Multiple episodes — parallel

Running in parallel for multiple episodes means:

- Different episodes are independent. Episode 210's files do not affect episode 211's workers.
- You may run the same skill on different episodes at the same time (e.g. one srt-to-transcript worker per episode in the batch), because each worker reads and writes only under `episodes/<n>/` for its own `<n>`.
- You must still respect per-episode dependencies: do not start readable or shorts for `<n>` until `<n>`'s transcript worker has finished and been verified.
- Parallelism across episodes is optional. You may run episodes one after another; the rule is always one worker per skill invocation, not one worker per episode for the whole pipeline.

Wave 1 can run up to one srt-to-transcript worker per episode in the batch at once; then, as each episode's transcript is verified, launch readable and shorts for that episode (two workers per episode). Total workers = 3 × (number of episodes); they do not all run at the same time.

## Orchestration

- Pre-flight first: no background workers until user-supplied metadata is collected and the user explicitly says to start the pipeline (see Pre-flight).
- Treat `pipeline-launch.md` as immutable for the duration of the run (see Scope).
- Prioritize quality over speed. Follow each skill's `SKILL.md` fully; do not shortcut steps.
- Use one fresh background worker per skill invocation (3 workers per episode in the batch).
  Never chain srt → readable → shorts in a single worker.
- Context hygiene: Each worker reads only that skill's `SKILL.md` and that episode's inputs on disk.
  Workers for readable and shorts must not load or reference SRT files.
- Parallelism is optional; sequential execution is OK at coordinator discretion.
- Dependencies: Do not start readable or shorts for an episode until that episode's transcript output exists on disk (from the srt-to-transcript worker for that episode).

## Base path

This file lives at the root of the Basic Block Radio knowledge base.
All paths below are relative to that root (`knowledge-bases/basicblockradio/` from the life-system repo).

## Skills and I/O

For episode number `<n>` (e.g. `210`):

| Step | Skill path | Input | Default output |
|------|------------|-------|----------------|
| 1 | `.agents/skills/srt-to-transcript/SKILL.md` | `episodes/<n>/<n>-raw.srt` | `episodes/<n>/<n>-transcript.md` |
| 2 | `.agents/skills/transcript-to-readable/SKILL.md` | transcript from step 1 | `episodes/<n>/<n>-readable.md` |
| 3 | `.agents/skills/transcript-to-shorts/SKILL.md` | transcript from step 1 | `episodes/<n>/<n>-shorts.md` |

Workers must use the skill's default output naming unless the suffix rule below applies.

## Missing input

If a required input file is missing, FAIL that worker. Do not skip silently.
Report which episode and which skill failed.

## Repeated run — do not overwrite

If the default output file already exists, do not overwrite it.

Write a new file with an incrementing numeric suffix before the extension:

- `210-transcript.md` exists → write `210-transcript-2.md`
- `210-transcript-2.md` exists → write `210-transcript-3.md`

Same pattern for `-readable` and `-shorts` (e.g. `210-readable-2.md`, `210-shorts-2.md`).

Each worker picks the next free suffix independently by checking the episode directory on disk before writing.

The coordinator must pass this rule to every worker in the worker prompt.

## Load and concurrency

The user does not require a specific parallelism level.
Run workers in parallel or sequentially as you judge best for reliability and context hygiene.

## Scope

- Do not edit any files except newly created output files for this batch.
- While this pipeline run is active, do not modify `pipeline-launch.md` at this knowledge base root — read it only. No coordinator or worker may change that file during pre-flight, while waiting for start, or while workers are running.
- Read-only access to inputs, skill files, and reference episodes only as each skill requires.
- Do not modify `IDEAS.md` or other repo metadata.
- Do not create git commits unless the user asks separately in another message.

## Per-worker instructions (template)

For each background worker, include at minimum:

1. Episode number `<n>` and skill name (srt-to-transcript | transcript-to-readable | transcript-to-shorts).
2. For srt-to-transcript: guest name, host names, and `recording_date` if provided in pre-flight (exact string for frontmatter). If pre-flight did not include a date, instruct the worker to set `recording_date: unknown` and not to derive a date from files.
3. Path to read only that skill's `SKILL.md` under this knowledge base (`.agents/skills/...`).
4. Exact input path(s) on disk for that episode.
5. Output path after applying the no-overwrite / incrementing suffix rule.
6. Reminder: follow `SKILL.md` completely; verify output exists and is non-empty before reporting done.
   For srt-to-transcript: transcript blocks must join SRT cues verbatim (fillers/dictionary/ASR only) — not readable-style copy-editing.
7. For readable/shorts: input is the transcript file produced for that episode (use the actual path if a suffixed transcript was written). Pass any optional shorts preferences from pre-flight when launching transcript-to-shorts.

## Verification

After each worker completes, confirm the declared output file exists and is non-empty.
Mark the worker failed if verification fails.

## Final reporting

Produce a summary table: episode × skill → output path, status done or failed.

Do not include full transcript dumps or large file contents in the summary.

## Git

Do not commit any changes for this batch.

## Worker launch checklist (coordinator)

Pre-flight:

- [ ] `pipeline-launch.md` left unchanged (read-only for this run)
- [ ] Episode list confirmed
- [ ] Skills scanned for required user input
- [ ] User asked for missing metadata; user replied
- [ ] Per-episode metadata recorded for worker prompts
- [ ] User explicitly said to start the pipeline

For each episode in the user-supplied list (only after the start instruction):

- [ ] srt-to-transcript (input `episodes/<n>/<n>-raw.srt`)
- [ ] After that transcript is verified, transcript-to-readable
- [ ] After that transcript is verified, transcript-to-shorts

One separate background worker per skill invocation, each with a minimal, skill-specific prompt.
