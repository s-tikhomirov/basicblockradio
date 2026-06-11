---
name: transcript-to-shorts
description: >-
  Extract literal guest-voice clip candidates from NNN-transcript.md for short-form
  video or audio (Shorts, Reels), typically ~30 s after edit, up to ~60 s when the
  idea needs it. Writes NNN-shorts.md with elided verbatim quotes using <...>. Use when
  the user asks for shorts, clips, reels, or short-form cuts from an episode.
disable-model-invocation: true
---

# transcript-to-shorts

Find shareable ideas in a long episode and point editors to verbatim transcript spans that can be cut to tight short-form audio. Default target is about 30 seconds after edit; use up to about 60 seconds when one idea needs more guest time to stay clear and self-contained. Output is a montage map, not new prose.

## Scope (this skill only)

When this skill is invoked, complete only the work described here and stop.

- Input: `episodes/NNN/NNN-transcript.md` (use a human-reviewed transcript when possible; otherwise use whatever exists if the user asks)
- Output: `episodes/NNN/NNN-shorts.md`
- Read: episode frontmatter, `.agents/dictionary.md` (spelling for Russian titles, hooks, and terms)

Do not: rephrase, summarize, or copy-edit guest/host lines; merge transcript blocks into one invented paragraph; change speaker labels or timestamps on kept lines; pull wording from `NNN-readable.md` (that file is rephrased — wrong source for literal clips); run `scripts/`; edit `NNN-transcript.md`.

Do not continue with `transcript-to-readable`, `readable-to-shownotes`, or other episode skills in the same run unless the user explicitly asks.

## Difference from transcript-to-readable

| | transcript-to-readable | transcript-to-shorts |
|---|------------------------|----------------------|
| Goal | Clear long-form reading | Clip candidates for short-form |
| Wording | Copy-edit inside each block | Subset of original words only |
| Structure | One output line per input line | Few lines per segment, elisions with `<...>` |
| Length | Full episode | ~30 s after tight edit (up to ~60 s if justified) |

Verbatim rule: every character outside `<...>` must match the transcript in order (same spelling and punctuation as in `NNN-transcript.md`). You may only omit; never substitute synonyms or fix grammar inside kept spans.

## Language

- This skill file: English (except literal Russian inside transcript examples).
- `NNN-shorts.md`: Russian throughout the body — intro line, segment titles (`##`), editor summaries, field labels, and timestamp lines. YAML frontmatter: copy from the source transcript (`episodes/templates/transcript-template.md` fields) and add `source: NNN-transcript.md`.
- Write titles and hooks for the podcast Russian-speaking editors and social audience. Keep established English terms when the episode uses them (NIST, RSA, Harvest Now Decrypt Later, hash-based, and entries in `.agents/dictionary.md`).
- Do not write segment titles or hooks in English unless the user explicitly asks for an English deliverable.

## What makes a good segment

Prioritize guest speech that is:

- One clear idea (not a tour of five topics)
- Interesting, surprising, contrarian, or mildly controversial for a general crypto/tech audience
- Self-contained after montage (listener does not need prior 20 minutes of context)
- Strong opening hook within the first few seconds of the edited clip

Optional: one host line (question or short setup) before the guest payoff. The main thesis and punchline must be the guest. Prefer opening on the guest when their first sentence names the topic or the answer works without a question.

### Host setup lines (when the clip starts with a question)

Shorts viewers have not heard the episode. If you keep a host question, the first audible words must make the topic obvious — same bar as a strong `##` title.

Time and words: The host block must be a minority of the edited clip (rough guide: well under half the kept words, often ~15–25% / ~5–10 s). The guest carries most of the runtime. If the host question needs a long lead-in to be clear, drop the host and start on the guest, or pick another moment.

Prefer guest-only when:

- The guest names the topic in the opening of their answer (e.g. "Когда мы говорим про пост-квантовую криптографию…"), or
- The guest block is self-contained after montage without a setup question.

When you do keep a host opener: one line (or one tight elided line) that states the topic and asks the question; then maximize guest material within the segment duration budget.

Do:

- Start from the beginning of the question, or from the first clause that names the subject (terms, names, contrast).
- Use `<...>` only after the topic is clear, or to cut filler in the middle — not to delete the setup and leave a generic tail.
- Tighten the host with `<...>` before trimming the guest payoff.

Good (short host, topic in the question; guest has most of the clip):

```
(00:18:41) Сергей Тихомиров: Что вообще такое квантовый компьютер <...>?

(00:18:48) Михаил Кудинов: Квантовый компьютер — это устройство, <...>
```

Bad (generic tail; listener cannot tell what is being compared):

```
(00:09:33) Сергей Тихомиров: <...> Можешь прояснить, в чем различие?
```

Bad (only the end of a long question; the subject was in the cut part):

```
(00:35:17) Сергей Тихомиров: <...> или нужно переходить на принципиально новое.
```

Bad (host monologue dominates; guest reply is a footnote):

```
(00:33:58) Сергей Тихомиров: Вот допустим, у нас есть <...> [long question]

(00:35:31) Михаил Кудинов: Нужно переходить на принципиально новое, <...>
```

If the full host line is too long for the target duration, drop the host and open on the guest (or pick another moment).

### Guest answer openers (yes/no without the question)

Do not open a clip on a guest line that only reacts to a question the viewer did not hear ("Да,", "Прав.", "Именно.", "Верно," and similar), unless the same segment includes a short host question that makes the reaction intelligible.

Either:

- Include a tight excerpt of the host question (topic + ask), then the guest answer (including "Да" / "Прав" if it follows immediately in the transcript), or
- Omit the host line and start the guest on substantive content using `<...>` at the start of that timestamp line (e.g. elide "Прав." and begin at "На самом деле…").

Bad (reaction without setup):

```
(00:29:21) Михаил Кудинов: Да, есть математическая общность. <...>
```

Bad (acknowledgment without setup):

```
(00:22:52) Михаил Кудинов: Прав. На самом деле, <...>
```

Good (short question, then answer):

```
(00:28:49) Сергей Тихомиров: <...> про алгоритм Шора, <...> один алгоритм на них всех работает. Вот в чем здесь фишка?

(00:29:21) Михаил Кудинов: Да, есть математическая общность. <...>
```

Good (guest-only; drop acknowledgment):

```
(00:22:52) Михаил Кудинов: <...> На самом деле, с точки зрениями криптографии, на практике нам практически не нужен даже квантовый компьютер, <...>
```

Skip or deprioritize:

- Sponsor reads, patron thanks, generic intro/outro
- Long host monologues without a guest reply in the segment
- Pure biography unless there is a sharp unexpected fact
- Dense jargon without a plain-language payoff in the same clip

## Duration target

Editors will remove fillers, tighten pauses, and drop whole sentences. Your job is to mark a window in the transcript that can become the target length after edit, not one that already matches that length verbatim.

Default estimate: ~30 s after montage. Use ~60 s when the clip is still one clear idea but needs more guest lines to stay self-contained (e.g. a multi-step explanation listeners cannot follow if cut shorter). Say so in `Зацепка:` or in `Ориентировочная длина после монтажа` when you choose ~60 s.

Rough guide for edited Russian speech at podcast pace (count only words outside `<...>`):

- ~30 s: target ~55–85 words of guest+host text after montage
- ~60 s: target ~100–170 words when the topic justifies a longer clip
- If a host line is included, guest words should be a clear majority of that count
- Source span on the page is often longer; use `<...>` for cuts inside lines and omit whole low-value lines between kept lines
- If kept words (no elisions) already exceed the band for your target duration, tighten elisions or pick a narrower idea
- If after elisions fewer than ~40 words remain for a ~30 s clip, the segment may feel thin — add adjacent guest sentences (still verbatim) or choose another moment

Per segment, include a line: `Ориентировочная длина после монтажа: ~NN с (~WW слов)` (word count excludes `<...>`; count Russian words in kept spans).

## Tighten repetition (same line, still verbatim)

Spoken Russian often stacks the same idea three ways (anaphora, triads, immediate restatement). For shorts, the clip should not sound like the guest is circling one point. After the listener has heard the idea once, elide later repetitions on the same timestamp line with `<...>`. Do not rephrase; only omit intervening words that repeat what is already clear.

Typical patterns to cut:

- Parallel clauses with the same structure and rising specificity (keep the sharpest clause, elide the rest)
- The same noun or phrase twice in a row (e.g. a hook on "liquidity", then "maximum liquidity" again — keep the hook, elide the bridge; see examples below)
- Rhetorical lists where one item already carries the meaning (keep one representative item or the list ends, plus `<...>`)
- The same claim restated in the next sentence when montage already established it (elide the weaker repeat, keep the payoff)

Good:

```
мы не были первым ликвидным стейкингом на эфире, <...> мы не придумали ликвидный стейкинг.
```

```
правильная ставка на ликвидность <...> А максимальная ликвидность, это такая вещь, что она что-то вроде moat
```

Bad (sounds like a listicle, wastes seconds):

```
мы не были первым ликвидным стейкингом на эфире, мы не были первым ликвидным стейкингом вообще, мы не придумали ликвидный стейкинг.
```

Bad (paraphrase or synonym swap — never):

```
мы не изобретали liquid staking
```

When in doubt: one clear formulation per sub-idea inside the segment; use `<...>` for the rhetorical echo, not for facts the clip still needs.

## Workflow

1. Read full `NNN-transcript.md`. Note guest name(s) from frontmatter.
2. Scan for strong guest moments (contrasts, myth-busting, concrete stories, stakes for listeners).
3. For each candidate, pick one shareable idea and a short title for the clip.
4. Select contiguous transcript lines (timestamps in order). Trim with `<...>` inside lines; drop filler lines entirely; elide rhetorical repetition on a line (see Tighten repetition). For host openers, follow Host setup lines; for guest-first segments, follow Guest answer openers.
5. Write `NNN-shorts.md` (format below). Aim for 5–10 segments, best first.
6. Self-check each segment (checklist below).

## Output file

Path: `episodes/NNN/NNN-shorts.md`

### Frontmatter

```yaml
---
episode: NNN
guest: …
hosts:
  - …
recording_date: …
source: NNN-transcript.md
---
```

Copy frontmatter from `NNN-transcript.md` (field order per `episodes/templates/transcript-template.md`), including `recording_date` verbatim. Do not invent, change, or derive `recording_date`. Add `source: NNN-transcript.md`. Do not add a `status` field.

### Body structure

1. One short intro line in Russian explaining that kept speech is verbatim and `<...>` marks cuts for the edit.
2. Segments in discovery order (strongest clip first). For each segment:

| Field | Content |
|-------|---------|
| `## …` | Short clip title in Russian (cover line for Shorts/Reels) |
| `Зацепка:` | One sentence in Russian: which guest idea you surface and why it might interest someone who has not heard the episode |
| `Ориентировочная длина после монтажа:` | `~NN с (~WW слов)` |
| `Диапазон в выпуске:` | First timestamp of the segment and end bound for editors: `(HH:MM:SS)–(HH:MM:SS)` (see below) |
| Timestamp lines | Verbatim extraction with `<...>` (see rules) |

Rules for the excerpt block:

- Keep `(HH:MM:SS) Speaker Name:` prefix on every included line exactly as in the transcript.
- `<...>` marks removed audio/text; no spaces required inside the marker.
- Elisions may start or end a line; they may replace a middle clause.
- Do not open the first kept line of a segment with `<...>` if the audible result would start mid-phrase (broken hook). Keep from the first word of a complete opening clause or sentence on that line. Exception: guest-only segments may elide a short acknowledgment at the line start (see Guest answer openers).
- Use elisions to remove stacked repetitions of the same thought on one line (see Tighten repetition).
- Blank line between timestamp lines, same as transcript habit.
- Do not add chapter markers inside a segment except the `##` title.
- The `Зацепка:` line is editor meta in Russian. Everything under the timestamp lines is literal extraction only.

`Диапазон в выпуске` (from–to):

- **From:** timestamp on the first line included in the segment.
- **To:** timestamp on the **first transcript block after the last included line** (the next `(HH:MM:SS)` block in `NNN-transcript.md`, even if that block is not quoted in the segment).
- If all excerpt lines share one transcript block, **from and to must still differ** — use that block’s time as from and the next block’s time as to.
- If the segment spans several blocks, to is the start of the block immediately after the last quoted line’s block (same rule).
- Never write identical from and to (e.g. `(00:13:16)–(00:13:16)`).

### Canonical example (episode 220)

Literal output excerpt (Russian meta and Russian timestamp lines):

```
## Что такое квантовый компьютер

Зацепка: Гость отвергает интуицию "и 0, и 1 одновременно" и в конце разбивает миф, что квантовый компьютер "просто быстрее считает".

Ориентировочная длина после монтажа: ~30 с (~70 слов)

Диапазон в выпуске: (00:18:41)–(00:20:40)

(00:18:41) Сергей Тихомиров: Что вообще такое квантовый компьютер <...>?

(00:18:48) Михаил Кудинов: Квантовый компьютер — это устройство, которое работает с использованием эффектов на квантовом уровне. У нас вместо битов <...>  у нас здесь используются кубиты. <...> это скорее больше похоже на какую-то подброшенную монетку, которая с определённой вероятностью пойдёт либо в ноль, либо в единицу. <...> Второй важный момент — это запутывание <...> Я могу подготовить два кубита, которые будут между собой связаны. <...> Если там окажется 0, то значит, я буду в 100% узнать, что и второй тоже окажется 0. Вот эти вот два эффекта — то, что есть промежуточные состояния между 0 и 1 и то, что можно связывать кубиты между собой, позволяют производить определенный класс вычислений <...> Это не вещь, которая что-то быстро вычисляет. Это новый класс вычислений, который вот этот именно класс можно проводить быстрее <...>
```

## Segment checklist (required before finishing)

For each `##` segment:

- [ ] Guest delivers the core idea; host lines are setup only (if any)
- [ ] No wording taken from `NNN-readable.md`
- [ ] Every kept substring appears in `NNN-transcript.md` in the same order (no paraphrase)
- [ ] No rhetorical triads or immediate restatements left intact when one formulation is enough (repetition elided with `<...>`)
- [ ] Timestamps monotonic; speakers match transcript
- [ ] `Диапазон в выпуске`: from = first included line; to = start of next transcript block after the last included line; from ≠ to
- [ ] Word count outside `<...>` fits the stated duration (~55–85 words for ~30 s, ~100–170 for ~60 s when justified; note in `Ориентировочная длина после монтажа` if intentionally shorter or longer)
- [ ] `Зацепка:` line is in Russian and explains why the clip works for someone who has not heard the episode
- [ ] Segment title (`##`) is in Russian
- [ ] First kept line of the segment does not open mid-phrase with `<...>` (unless eliding only a guest acknowledgment per Guest answer openers)
- [ ] If a host line opens the clip, the first kept words name the topic (not only "объясни разницу", "в чем фишка", "или нужно…" after `<...>`)
- [ ] If a host line is present, guest speech is the majority of kept words and runtime; otherwise omit the host
- [ ] Guest line does not open with "Да"/"Прав"/similar unless a host question is included in the same segment, or the acknowledgment is elided with `<...>`
- [ ] Segment is not mostly sponsor or housekeeping

## Input when invoking

Required:

- Episode number `NNN` or path to `NNN-transcript.md`

Optional:

- Minimum/maximum number of segments (default 5–10)
- Themes to favor or avoid
- Guest name if multi-guest episode and user wants one guest only