# transcript-to-readable

Copy-edit each transcript block into readable direct speech — clearer sentences and flow inside the paragraph, while keeping the same boundaries and facts. Expect input already structured with speakers, timestamps, paragraph lines, and dictionary spellings — with spoken wording preserved from `srt-to-transcript` (not pre-edited for flow).

## Scope (this skill only)

When this skill is invoked, complete only the work described here.

- Input: `content/episodes/NNN/NNN-transcript.md`
- Output: `content/episodes/NNN/NNN-readable.md`
- Chunk orchestration scripts (split/merge only) and `disclose_foreign_names.py` (English parentheticals only) are allowed; they must not copy-edit Russian prose.

Do not convert raw SRT in this skill. If the user only has `NNN-raw.srt`, ask them to produce `NNN-transcript.md` from the SRT in a separate chat invocation before running this skill.

Sponsor reads: primary cleanup belongs in `srt-to-transcript` (`content/sponsorships/`). In this skill, only touch sponsor blocks if something is still unclear or misspelled after pass 1 — same rules (no rewriting to match sponsor script; fix names, numbers, clarity only). See that skill’s «Sponsor read segments».

## Files

- Input: `content/episodes/NNN/NNN-transcript.md` (after human review). Episode number from filename.
- Output: `content/episodes/NNN/NNN-readable.md` — frontmatter copied verbatim from the transcript (`episode: NNN` only per `content/episodes/templates/transcript-template.md`). Same line format:

```
(00:06:28) Speaker Name: Text...
```

## Hard limits

Do not: third-person narrative; editorial commentary; drop or change timestamps; add or remove paragraph blocks; merge two input lines into one; split one input line into two; change speaker labels; change facts, numbers, or technical claims; soften or sharpen tone; telegraphic compression (dropping pronouns, objects, or examples the speaker clearly expressed); “fix” gender or pronouns when referent is ambiguous; strip pronouns or objects that carry meaning (ты/вы/она/он/это/в ней/мне and similar) only to sound tighter; compress a block into headline-style dash chains; use scripts or tools that rewrite Russian prose or auto-edit wording (orchestration split/merge under `scripts/` is allowed in chunked mode; `disclose_foreign_names.py` only after the readable body is finished — see Foreign names).

Do: copy-edit every block so it reads clearly as written Russian, not as raw transcript pasted verbatim; keep first person and speaker on every block; one output line per input line (same timestamp and speaker); restore implied subjects when written Russian needs them; fix Russian endings when context is clear (section Russian grammar).

## Structure (locked)

- Paragraph boundaries are fixed in `NNN-transcript.md`. Do not merge or split blocks.
- For each input line `(time) Name: text`, produce exactly one output line with the same `(time)` and `Name:`.
- Blank line between blocks, same as input. No chapter headings, no bold on names or times.
- If an input block is missing or extra lines appear, fix to match input count before finishing.

## Fillers and speech noise

While copy-editing each block, still remove words when they add no meaning in writing:

- Stand-alone fillers (ну, как бы, короче, …) if any remain in the transcript line
- Empty hedges that add no meaning in writing (наверное, не знаю) when they only stall
- False starts, stutters, and immediate self-repeats («я я», «то есть то есть»)
- Trailing «и так далее», «вот», «да» at clause ends when they are pause-fillers, not emphasis

Do not delete a word that changes emphasis, irony, or a careful qualification the speaker meant. When unsure, keep it.

## Prose (copy-edit within the block)

Goal: each block should read noticeably cleaner than the transcript line — full sentences, clear flow — while still sounding like the same person on the podcast. Verbatim preservation of spoken clutter is a failure mode for this skill.

Stay close to how the person spoke; several clear sentences beat one stitched telegram block.

Within the block only (structure stays one line):

- Reorder jumpy clauses; join fragments; break run-ons; turn abandoned half-sentences into complete thoughts or drop them if they add nothing.
- Cut duplicate ideas said twice in one breath; trim rhetorical repetition that is typical of speech but heavy on the page.
- Rephrase for grammar, anaphora, and readability; keep the speaker’s terms, numbers, and technical claims.
- Remove or shorten wordy spoken glue when written Russian does not need it, as long as meaning stays the same.
- Keep spoken pronouns and objects that carry meaning (e.g. «как она проходит», «кто в ней участвует»). Do not replace «Можешь рассказать» with bare «Расскажи» unless the speaker said so.
- Preserve: substantive examples, asides that add content, idioms, humor, full questions, emphasis that matters.

Length: a block may become somewhat shorter when cutting redundancy; it may stay similar length when the transcript is already tight. Do not chase brevity. Long answers stay long in full sentences — never bullets or headline dash chains.

Punctuation: prefer periods between thoughts, not `;` or dash chains. Em dash for apposition only (e.g. «нужно предоставить proof — выписку из университета»).

Dash chaining (from host questions about Eindhoven / PhD):

Bad:
«пара вопросов про Эйндховен, где ты защитил PhD — поздравляю с защитой. Я полистал тезис, introduction, что-то понял, очень немного — впечатляет. Почему именно Эйндховен, сильная школа криптографии — как выбрал университет?»

Better:
«пара вопросов про Эйндховен, где ты защитил PhD (поздравляю с защитой!). Я полистал тезис, introduction, что-то понял, хотя очень немного — впечатляет. Почему именно Эйндховен, там сильная школа криптографии? Как ты выбрал университет?»

Semicolons and dashes instead of sentences (from guest path to PhD):

Bad:
«В квантовом центре нашли проблемы с доказательствами безопасности одной из схем; написал одному из ведущих специалистов по этой схеме — она тогда участвовала в конкурсе NIST на стандартизацию — что обнаружили проблему, интересует PhD»

Better:
«В квантовом центре мы нашли проблемы с доказательствами безопасности одной из схем. Я написал одному из ведущих специалистов по этой схеме. Она тогда участвовала в конкурсе NIST на стандартизацию. Я объяснил, что мы обнаружили проблему и что меня интересует PhD»

Question clarity — input: «Рассчитано на студентов или есть ограничение по возрасту?» Too terse without subject. Better: «Олимпиада рассчитана на студентов? Есть ограничение по возрасту или квалификации?»

Pronouns — do not compress for style:

Transcript: «Можешь бы рассказать, что это за олимпиада, как она проходит, кто в ней участвует.»

Too aggressive: «Расскажи, что это за олимпиада, как проходит, кто участвует.»

Better: «Можешь рассказать, что это за олимпиада? Как она проходит, кто в ней участвует?»

## Russian grammar

Read each block as written Russian. Use `podcast-info.md` and episode frontmatter for host/guest gender when «я» forms are wrong in the transcript.

- Speaker «я»: fix verb/participle gender when speaker is clearly male or female (e.g. работал я, not работала я, for a male guest).
- Do not change «она/он» for общий род or unclear referent (e.g. специалист … Она участвовала — «она» = специалист, not forced «он» from «одному специалисту»).
- Restore when missing in transcript: я, мы, все, это, objects needed for grammar (…я смогу взломать эту подпись; все уже перешли; им это не понадобится).
- Do not remove when present in transcript: same words if the speaker said them — including ты/вы forms, «она/он» for things (олимпиада … она проходит), «в ней», «мне», «тебе». Fixing errors ≠ making speech telegraphic.
- «это» depends on context: may be required (e.g. copula when speech omits it: способ таргетировать → способ — это таргетировать).
- Subject–verb: verb agrees with grammatical subject (Северная Корея … начнет, not начнут).
- Skip fixes that need facts not in the transcript.

## Foreign names

Policy: `.agents/dictionary.md` (People names) and `.agents/foreign-persons.json`.

During copy-edit (single-file or per chunk):

- Use **Russian** forms for foreign persons, with **correct case** in each block (`Джастином Дрейком`, `с Дэном Боне`). Russian hosts and guests: Cyrillic only, no English parenthetical.
- **Do not** add `(English Name)` during chunk work or the main copy-edit pass — parallel chunks cannot know episode-wide first mention.

After the full `NNN-readable.md` exists (always run, including single-file mode):

```bash
python3 scripts/disclose_foreign_names.py content/episodes/NNN/NNN-readable.md
```

The script inserts ` (English canonical)` once per foreign person per episode, immediately after the first matched Russian name span. Case mismatch is OK (`с Джастином Дрейком (Justin Drake)`). It does not change block count, timestamps, or speakers. Use `--dry-run` to preview.

## Workflow

### When to use chunked mode

Use chunked mode when either:

- Block count in `NNN-transcript.md` is greater than 50, or
- Wall-clock span from first to last block timestamp exceeds about 45 minutes

Otherwise a single full-file pass is fine.

### Single-file mode

1. Read `NNN-transcript.md` line by line (each timestamped speaker line is one block).
2. For each block: copy-edit per Prose and Fillers above (expect visible improvement, not near-verbatim output); keep same timestamp and speaker; do not merge with adjacent blocks.
3. Verify output block count and timestamps match input.
4. Write `NNN-readable.md` with frontmatter copied from the transcript (`episode: NNN` only); use `.agents/dictionary.md`, `podcast-info.md`, `.agents/editing-standards.md`.
5. Run `python3 scripts/disclose_foreign_names.py content/episodes/NNN/NNN-readable.md`.

### Chunked mode (long episodes)

Orchestration only — run repo scripts from `knowledge-bases/basicblockradio/scripts/` (they do not edit Russian text):

1. Split: `python3 split_transcript_chunks.py content/episodes/NNN/NNN-transcript.md`  
   - Default: writes `content/episodes/NNN/.chunks/chunk-001.md`, … (gitignored; safe to delete after merge).  
   - Defaults: about **15 minutes** per chunk (`--max-span-seconds 900`) and `--max-blocks 22` (whichever limit is hit first). Smaller chunks reduce quality drift on long episodes.  
   - Override only when needed, e.g. `--max-span-seconds 1200` for ~20 minutes.  
   - `--dry-run` prints JSON manifest (block counts, line ranges, timestamps, span per chunk) without writing files.
2. For each chunk file: apply this skill’s rules to every line in that chunk only — exactly one output line per input line; same timestamps and speakers; full within-block copy-edit; no merge/split across chunk boundaries.
3. Save each result as `content/episodes/NNN/.chunks/chunk-NNN-readable.md` (same chunk order as split).
4. Merge:  
   `python3 merge_readable_chunks.py --transcript content/episodes/NNN/NNN-transcript.md --chunks-dir content/episodes/NNN/.chunks -o content/episodes/NNN/NNN-readable.md`  
   Optional: `--qc` warns on blocks where readable text is much shorter than transcript (ratio heuristic).
5. Verify merged block count equals the transcript; spot-check timestamps monotonic.
6. Run `python3 scripts/disclose_foreign_names.py content/episodes/NNN/NNN-readable.md`.
7. Remove the chunk working directory after a successful merge — do not leave split/readable chunk files on disk. Delete `content/episodes/NNN/.chunks/` entirely (e.g. `rm -rf content/episodes/NNN/.chunks`). Only keep `NNN-readable.md` as the artifact for this skill.

For three or more chunks, parallel Task subagents (one per chunk) are reasonable; each subagent gets one chunk path and the same hard limits above (no English parentheticals in chunks). The orchestrating agent still runs merge, disclose, and step 7 cleanup.

Goal: reads like the podcast in clearly edited written Russian — not a summary, not a near-verbatim transcript. Structure matches the transcript file (whole file or sum of chunks).

## End-to-end example

Input (three blocks — boundaries unchanged):

```markdown
(00:06:28) Василий Шаповалов: Если быть вот совсем честным в этой истории, да, ликвидный стейкинг — это идея была не новая, когда Lido появилась. Впервые я ее прочитал в коммьюнити Космоса, где это была большой-большой темой.

(00:06:53) Василий Шаповалов: В начале 20-го года я в середине февраля начал работать CTO в P2P-валидаторе. Тоже один из проектов Кости. Буквально в первые же две недели я посмотрел, какие будут важные темы, что мне нужно сделать в этом году.

(00:07:30) Василий Шаповалов: Почему? Потому что он был заточен под людей, которые будут стейкать свои, у тебя дома, 32 эфира, без встроенных в протокол механизмов делегации стейкинга операторам. А большинство людей, у которых есть деньги, они стейкать не будут.
```

→ readable (three blocks, same timestamps):

```markdown
(00:06:28) Василий Шаповалов: Если быть совсем честным, идея ликвидного стейкинга была не новая, когда появился Lido. Впервые я прочитал о ней в коммьюнити Космоса, где это была большая тема.

(00:06:53) Василий Шаповалов: В начале 2020 года я в середине февраля начал работать CTO в P2P-валидаторе, тоже один из проектов Кости. Буквально в первые две недели я посмотрел, какие будут важные темы, что мне нужно сделать в этом году.

(00:07:30) Василий Шаповалов: Почему? Потому что он был заточен под людей, которые будут стейкать свои 32 эфира дома, без механизмов делегации стейкинга операторам. А большинство людей, у которых есть деньги, они стейкать не будут.
```

## Usage

Run on a reviewed `NNN-transcript.md` → `NNN-readable.md`; human-review the readable before show notes.

Do not convert SRT or build `NNN-transcript.md` in the same run unless the user explicitly asks for that work separately.
