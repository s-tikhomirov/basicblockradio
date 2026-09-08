---
name: expand-transcript-placeholders
description: >-
  Expands speaker-slot abbreviations (ST, MG, II, and Cyrillic analogues
  such as ИИ, МГ) to the full names already used as labels in
  NNN-transcript.md, fills empty () timestamps, and spreads duplicate
  start times by interpolating from neighboring times and paragraph
  length. Use when the user is reviewing a transcript, added missed
  speaker paragraphs, typed initials instead of full names, left empty
  parentheses for timestamps, or several consecutive blocks share the
  same (HH:MM:SS).
---

# expand-transcript-placeholders

Mechanical cleanup during human review of `NNN-transcript.md`.
Expands speaker-slot initials to in-file full names,
fills empty `()` timestamps, and spreads duplicate start times
from neighboring times and paragraph length.

## Scope (this skill only)

When this skill is invoked, complete only the work described here and stop.

- Input: episode number, or the open `NNN-transcript.md`
- Output: in-place edits to `content/episodes/NNN/NNN-transcript.md`
- Change only the timestamp token and the speaker name on existing block lines
- Keep paragraph text, blank lines, frontmatter, and block count
- Run the helper script under this skill directory
- Do not create or edit `NNN-readable.md`
- Do not retag hosts from conversation cues (that is `improve-transcript-labels`)
- Do not rewrite spoken wording

## Input

Required in the user prompt, or taken from the focused transcript file:

- Episode number `NNN`

Content being edited:

- `content/episodes/NNN/NNN-transcript.md` after a human has added missed turns
  as new `(HH:MM:SS) Name:` or `() Abbrev:` lines

Markup this skill resolves:

- Speaker slot is a Latin letter code (`ST`, `MG`, `II`) or a Cyrillic analogue
  (`СТ`, `МГ`, `ИИ`), any length, matching the initials of a full name already
  used as a speaker label in this file
- Timestamp is empty parentheses: `()` immediately before the speaker name
- Two or more consecutive blocks share the same `(HH:MM:SS)` because a missed
  turn was split off and the original start time was copied onto each line

Example lines before this skill:

```text
(00:12:20) ST: если считать что изначально цена...
() MG: ну конечно да но мы же имеем...
() II: Если не закапываться прям во все подробности...
```

```text
(00:00:22) Сергей Тихомиров: Всем привет! С вами подкаст «Базовый Блок»...
(00:00:22) Иван Иваницкий: Привет, друзья!
(00:00:22) Сергей Тихомиров: И Александр Селезнев.
(00:00:50) Сергей Тихомиров: Fluence — облачная платформа...
```

The expansion target is the spelling already used on other speaker lines
in this episode (`Сергей Тихомиров`, `Митя Горошевский`, `Иван Иваницкий`).

## Helper script

Path: `.agents/skills/expand-transcript-placeholders/scripts/expand_placeholders.py`

Run from the knowledge-base root:

```bash
python3 .agents/skills/expand-transcript-placeholders/scripts/expand_placeholders.py \
  --episode NNN
```

`--path content/episodes/NNN/NNN-transcript.md` is an equivalent input.
`--dry-run` prints the plan without writing.
`--json` adds a JSON plan after the text report.

The script:

1. Reads every block `(HH:MM:SS) Name: text` or `() Name: text`
2. Treats labels that contain a space as full names for this episode
3. Builds Latin and Cyrillic initials from those names
   (first letter of each word; Cyrillic first letters mapped to Latin)
4. Expands a letter-code speaker slot when it uniquely matches one in-file name
5. Fills each `()` and each later copy of a duplicate start time
   from neighboring distinct times and word counts
6. Writes the file only when every non-full-name speaker slot uniquely expands
7. Prints a line-by-line summary on stdout

Exit codes:

- `0` — wrote changes, or nothing to change (`clean-noop`)
- `1` — missing file or parse error
- `2` — needs input; file left unchanged

## Names

Walk every block. Leave the speaker unchanged when it is already a full name
used in this file (a label with a space).

A speaker slot is a letter code when it is one to four Latin letters
or one to four Cyrillic letters, with no spaces (`ST`, `mg`, `ИИ`).
Longer single tokens (`Сергей`, `Guest`) are other temp labels.

Match that code, case-insensitive, to the initials of in-file full names:

- Latin initials: first letter of each word, transliterated (`Митя Горошевский` → `MG`)
- Cyrillic initials: first letter of each word (`Митя Горошевский` → `МГ`)

Expand when exactly one in-file full name produces that code.
Write that name exactly as it already appears on other speaker lines.

Stop without writing when any of these appear, and ask in chat:

- Ambiguous code: two or more in-file full names share those initials
- Unknown code: the code matches no in-file full name
- Other temp label: the speaker slot is not a full name and not a letter code
  (`Сергей`, `[неясно]`, `Guest`)

List every blocked label with line numbers (and candidate names when ambiguous).
Wait for the user. Do not guess.

After the user answers, put their names onto those lines (or ask them to)
and run the script again.

## Timestamps

Each `()` is an approximate start time for that new paragraph.
A run of the same `(HH:MM:SS)` on consecutive blocks is the same problem
with the first line already stamped.
Second-level `(HH:MM:SS)` is enough.

Keep the first distinct time in a run. Fill later copies, and every `()`,
from neighboring distinct times and word counts.

Between two distinct times `T_a` (block A) and `T_b` (block B),
the span `T_b - T_a` belongs to block A plus every fill in between.
Split that span in proportion to word counts of those blocks.
The new time for a filled block is the cumulative share of the words
before it, rounded to the nearest second.

Several `()` or duplicate stamps in a row share the same span that way.

Example: seven hello-lines all at `(00:00:22)` before `(00:00:50)`.
The first stays `(00:00:22)`. The next six get times between 00:00:22
and 00:00:50 in proportion to paragraph length.

Empty or duplicate blocks after the last distinct timestamp:
use the seconds-per-word rate from the previous distinct span.
If there is no previous span, use 2 words per second.

Empty blocks before the first distinct timestamp:
split the span from `00:00:00` to that first known time
across those empty blocks only.

After rounding, keep times moving forward:
a filled time is at least one second after the previous block.
If the window until the next distinct time is too tight, clamp and list a flag.

Leave a timestamp unchanged when it is already `(HH:MM:SS)` and strictly
later than the previous block’s time.

## Agent workflow

1. Resolve episode `NNN` from the prompt or the focused `NNN-transcript.md`.
2. Confirm `content/episodes/NNN/NNN-transcript.md` exists.
3. Run the helper from the knowledge-base root (command above).
4. If the script exits `2`, paste the `Needs input` list, ask the user, and stop.
5. If the script exits `1`, paste the error and stop.
6. If the script exits `0`, paste the summary (names expanded, timestamps filled or spread, flags).
7. Stop.

`--dry-run` first is optional when the user only wants a preview.

## After editing

Check:

- Block count unchanged
- Spoken text on each block unchanged
- Every expanded name is a full name already used as a label in this file
- Every former `()` is `(HH:MM:SS)`
- Consecutive blocks no longer share a start second, aside from flags the script listed
- Times still move forward in file order

Then list in chat:

- Episode number
- Each name expansion with line number: code → full name
- Each filled or spread timestamp with line number: old token → `(HH:MM:SS)`
- Any clamp or default-rate flags
- That remaining speaker labels are in-file full names

## Constraints

- DO change `()` timestamps, later copies of a duplicate start second, and letter-code speaker slots on `NNN-transcript.md`
- DO take full names from speaker labels already in this transcript
- DO stop and ask on ambiguous codes, unknown codes, and other temp labels
- DO keep spoken text, blank lines, and frontmatter
- DO run the helper script under this skill directory
- DO stop after the write (or after asking)
- DO NOT invent a full name that does not already appear as a speaker label in this file
- DO NOT retag a full name to a different person
- DO NOT look up times in SRT or audio
- DO NOT edit `NNN-readable.md`, SRT, or episode YAML
- DO NOT copy-edit paragraph wording

## Usage

1. While reviewing `NNN-transcript.md`, add missed turns as new lines.
   Type `()` for the time and initials for the speaker (`ST`, `MG`, `II`, or `ИИ`, `МГ`),
   or copy the previous `(HH:MM:SS)` onto the new line.
2. Run this skill with the episode number.
3. Answer any blocked labels the script reports.
4. Skim the filled and spread times; they are approximate.
5. Continue the rest of transcript review, then set `status: transcript-reviewed`.
