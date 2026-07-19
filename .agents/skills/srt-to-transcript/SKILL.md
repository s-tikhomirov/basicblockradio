# srt-to-transcript

Turn Whisper SRT into a structured transcript file. Establishes speakers, timestamped paragraphs, dictionary spellings, and minimal cleanup (fillers and false starts only). Preserves spoken wording cue-by-cue. Readable copy-editing belongs in `transcript-to-readable`, not here.

## Scope (this skill only)

When this skill is invoked, complete only the work described here and stop.

- Produce `content/episodes/NNN/NNN-transcript.md` from the raw SRT.
- Do not run `scripts/` under `knowledge-bases/basicblockradio/`.
- Do not generate Python or shell tools to transform SRT or transcript text.
- Do not start readable copy-editing or create `NNN-readable.md`.
- Do not split or merge transcript files for downstream passes.

## Purpose

Clean up Whisper output and freeze episode structure:

- Fix spelling in technical terms, names, and projects (`.agents/dictionary.md`) — token swaps in place, not sentence rewrites
- Fix obvious ASR mistranscriptions (wrong word heard for a word clearly intended), without paraphrasing
- Group consecutive SRT cues from the same speaker into paragraph lines with one timestamp per paragraph (see Paragraph boundaries and Speech fidelity)
- Standardize speaker labels and timestamp format
- Remove obvious noise fillers and false starts per Fillers — without shortening or polishing sentences
- Do not copy-edit for flow, clarity, or compression; that is `transcript-to-readable`

## Input

Required in user prompt when invoking skill:

- Episode number (extract from filename like `219-raw.srt` → 219, or ask if unclear)
- Guest name (who is being interviewed)
- Host names (who is asking questions)

Optional in user prompt (or from pre-flight metadata passed by the coordinator):

- `recording_date` — ISO date (`YYYY-MM-DD`) when the user or coordinator supplies it explicitly

Content being edited:

- Raw SRT file with timestamped segments (the AI reads this directly)

Context sources (read by the skill):

- Technical terms from `.agents/dictionary.md`
- Podcast metadata from `podcast-info.md` (including episode-level `recording_date` only if that file lists a date for this episode number — not inferred from anything else; patron support URLs in the same file)
- Active sponsor copy for the episode from `content/sponsorships/` (see Sponsor read segments)

### Input formats

The skill accepts two raw SRT formats. The skill auto-detects the format by examining the first non-empty line of the file.

Format A — Standard Whisper SubRip (default)
- Numbered cue blocks: `1`, `2`, `3`...
- Time line: `HH:MM:SS,mmm --> HH:MM:SS,mmm` (comma before milliseconds)
- Text follows on subsequent lines
- No speaker labels inside cues (one speaker per cue, determined by sequence)

Format B — Diarized bracket format
- Time range in brackets: `[HH:MM:SS:ff - HH:MM:SS:ff]` (four colon-separated fields)
- Optional speaker label on first line of text block: `Speaker N`, `Speaker 1`, `Speaker 2`, `Speaker 3`
- Text may follow on same line (after speaker) or subsequent lines
- Blocks may contain placeholder content: `(Music)`, `Transcription Pending`

### Timestamp normalization

Both formats convert to output `(HH:MM:SS)` with second-level precision:

- Format A: Truncate milliseconds (`00:15:30,450` → `(00:15:30)`)
- Format B: Drop fourth field (frames/centiseconds): `00:03:30:13` → `(00:03:30)`

Use floor (truncate), not round, for consistency.

### Placeholder handling

Some exports contain non-speech markers. Handle as follows:

| Marker | Action |
|--------|--------|
| `(Music)` | Omit entirely — do not create transcript line |
| `Transcription Pending` | Flag — needs manual resolution |
| Empty text after timestamp | Skip block |

Do not emit transcript lines for content not yet transcribed.

Processing approach:

- Detect format by first non-empty line: numbered cues (Format A) vs bracket timestamp (Format B)
- Parse accordingly: arrow-delimited SubRip cues (A) or bracket ranges with optional speaker labels (B)
- For each paragraph block: take cue text in time order from the same speaker, join with spaces (Format A) or split bracket blocks per boundary rules (Format B), then apply only Speech fidelity allowed edits
- Agent-driven from SRT only — no parser or batch scripts in this workflow

## Output

New transcript file `content/episodes/NNN/NNN-transcript.md` containing:

- Frontmatter: only `episode: NNN` (see `content/episodes/templates/transcript-template.md`)
- Also create or update `content/episodes/NNN/NNN-episode.yml` for identity (see `docs/content-model.md` and `content/episodes/templates/episode-template.yml`):
  - `episode`, `title` when known, `status: draft` until show notes are ready
  - `hosts` / `guests` as slugs under `content/people/` (create person stubs if new; do not invent slugs without confirming)
  - `recording_date`: exact date from user prompt, pre-flight metadata, or an explicit episode-level entry in `podcast-info.md` for this episode; if none of those apply, use `unknown`
- Transcript content only — no chapter headers, no summarization
- Format: `(HH:MM:SS) Speaker Name: text of speech`
- Timestamp format: parentheses, not bold — `(00:15:30)`
- Example: `(00:15:30) Александр Селезнев: Вопрос о стейкинге...`
- Consistent speaker labels
- Corrected technical terms from dictionary
- Preserved informal tone

Note: The output filename starts with episode number (e.g., `219-transcript.md`).

## Speech fidelity (mandatory)

The transcript is not a readable article. It is labeled, timestamped speech with Whisper fixes and filler cleanup only.

### Allowed edits inside a block

- Join consecutive cues from the same speaker with spaces; keep cue order and keep each sentence the speaker said (you may fix obvious punctuation only where SRT left none and a period or comma was clearly spoken)
- Replace or capitalize terms per `.agents/dictionary.md` and sponsor-file spelling fixes (same slot in the sentence — do not rephrase around them)
- Swap an obvious ASR garbage word for the intended word when context and audio meaning are clear
- Remove items listed under Fillers and obvious false starts (aborted phrase immediately restarted)
- Apply `.agents/editing-standards.md` year formatting where a year appears

### Forbidden edits (copy-editing)

- Paraphrasing, summarizing, or “tightening” across cues or sentences
- Dropping clauses, sentences, hedges, or examples because they feel redundant
- Merging several spoken sentences into one shorter sentence
- Changing word order or substituting synonyms for flow
- Replacing spoken connectives (“Так что давай”, “Я думаю, что”) with shorter equivalents unless they are pure filler per Fillers
- Dash chains or list compression that the speaker did not use
- Anything `transcript-to-readable` describes as copy-editing

When unsure whether a change is cleanup or copy-editing, keep the SRT wording.

### Anti-pattern (do not produce this)

SRT cues (same speaker, one thread):

```text
Хорошо, давай. Я подумал, стоит ли углубляться еще глубже именно в этот конкретный вопрос, который меня, безусловно, интересует.
Но я думаю, что, наверное, логичнее это сделать в контексте разговора про какую-то конкретику.
Так что давай, наверное, перейдем к разговору про zkSync Era, собственно, роллап, с которого начинался zkSync.
```

Wrong (rewritten):

```text
Я подумал, стоит ли углубляться ещё в этот конкретный вопрос, но логичнее сделать это в контексте конкретики. Давай перейдём к разговору про zkSync Era — роллап, с которого начинался zkSync.
```

Right (joined + dictionary/filler only; «собственно» dropped as filler; «Ethereum» from dictionary if applicable):

```text
Хорошо, давай. Я подумал, стоит ли углубляться еще глубже именно в этот конкретный вопрос, который меня, безусловно, интересует. Но я думаю, что, наверное, логичнее это сделать в контексте разговора про какую-то конкретику. Так что давай, наверное, перейдем к разговору про zkSync Era, роллап, с которого начинался zkSync.
```

Keep «наверное» when it qualifies the speaker’s judgment (as above). Do not strip it to shorten the block.

## Paragraph boundaries

Each output line is one paragraph block. The timestamp on the line is the start time of that block (time of the first SRT cue grouped into it).

Grouping cues into one line is structural only: concatenate their text per Speech fidelity. It does not permit rewriting the combined passage into fewer or smoother sentences.

### Priority (mandatory)

Question–answer semantics override paragraph length. Never merge cues from different speakers into one block, even when the exchange is short or the SRT has no long pause between turns.

When in doubt, split at a speaker change rather than keep one long block.

### Always start a new paragraph when

- The speaker changes (including host follow-up questions, clarification checks, and brief guest replies such as «Именно так»)
- The host asks a new question or reframes the prior answer («Правильно ли я понял…», «То есть…», «Получается…») — the host turn gets its own block even if it immediately follows the guest’s last cue
- The guest’s answer clearly ends and the host takes the floor
- The conversation shifts to a new topic (new question, new sub-question, intro or outro segment)
- Each sponsor in the opening sponsor segment (see Sponsor read segments — one block per sponsor at start, mandatory)
- Do not split the closing sponsor segment into one block per sponsor (see Sponsor read segments — one combined block at end, mandatory)
- A long pause in the SRT (clear break in recording) suggests a natural boundary and the same speaker continues

### One speaker, multiple cues

Both formats: Group consecutive cues from the same speaker into one block only while that speaker continues the same turn (one answer, one sponsor read, one uninterrupted host question).

Format A cues are SubRip entries. Format B bracket blocks are cues — even if some are short (one line or a few words), they are not pre-grouped into meaningful paragraphs. Apply the same grouping logic to both:
- Join consecutive blocks from the same speaker into one transcript paragraph
- Split at speaker changes, host reframes/clarifications, or topic shifts
- Do not assume Format B blocks are already editorially grouped

Do not extend a guest block across a host question or a host block across a guest answer, regardless of topic continuity.

Paragraphs may be very short: a single host question, a single-sentence guest confirmation, or one clarifying exchange each get separate blocks when speakers alternate.

### Duration (secondary)

Length guidelines apply only within a single speaker’s turn. They must not justify merging host and guest speech.

- Rough guide: many single-speaker blocks fall in the one-to-three minute range; about two minutes is typical, not a target
- If the same speaker continues one topic well beyond about three to four minutes with no natural break, consider splitting at the nearest SRT gap or sentence boundary so later copy-editing is not faced with one enormous paragraph — but do not split mid-thought just to satisfy a timer
- If a block is very long because the topic is long, that is acceptable

### Anti-pattern (merged Q&A)

Wrong — guest answer, host check, and guest reply in one block:

```text
(00:36:47) Иван Богатый: …защита от цензурирования…

Правильно ли я понял, что разница здесь с оптимистическими роллапами…

Именно так. Потому что это доказано в зике…
```

Right — three blocks, three timestamps:

```text
(00:36:47) Иван Богатый: …защита от цензурирования…

(00:37:47) Сергей Тихомиров: Правильно ли я понял, что разница здесь…

(00:38:04) Иван Богатый: Именно так. Потому что это доказано…
```

Paragraph boundaries in the transcript file are the canonical structure for the episode. Do not merge or split blocks for style in this skill.

Self-check before finishing:

- Spot-read several multi-cue blocks against the SRT. If whole sentences or distinct clauses disappeared, restore them from the SRT.
- Scan for host questions or guest confirmations embedded inside another speaker’s block (missing `(timestamp) Name:` line). Split any you find.
- Opening sponsor reads: one block per sponsor; closing sponsor roll call: one block for all end mentions (not one block per sponsor at the end).

## Fillers (bulk cleanup)

Remove when clearly noise only, without changing meaning: ну, значит, короче, типа, вот (standalone), так что (sentence start only when followed by a new action and the connective adds no meaning), вот как-то / так вот / вот именно, знаешь, понимаешь, слышишь, как бы, собственно, типа того, получается (pause), по-моему / не знаю (empty hedge only), кстати (empty), там / вот там, false starts.

Context-dependent: и так далее, и все такое, короче говоря, все такое — keep if they narrow a list or sum up; drop if trailing off. точно-точно / ну-ну / вот-вот — drop as backchannel agreement; keep if emphatic or part of the thought (вот-вот, в этом суть).

«типа» is always a filler. «это» only when clearly empty pause-filler, not when grammatically needed.

You do not need to catch every disfluency; remove obvious noise only. Do not copy-edit for readable flow or cut redundancy inside blocks beyond filler cleanup.

If a word might be filler or might carry meaning (e.g. «наверное», «я думаю, что»), keep it.

## Constraints

- DO NOT run or write scripts under `knowledge-bases/basicblockradio/scripts/`
- DO NOT generate scripts or tools that transform transcript prose
- DO NOT create `NNN-readable.md` or perform readable-style rewriting
- DO NOT soften direct statements
- DO NOT add transition phrases or corporate speak
- DO NOT restructure, merge, condense, or paraphrase sentences for style or readability (fix obvious ASR/dictionary tokens and fillers only)
- DO NOT drop spoken sentences, clauses, or examples when grouping SRT cues into one paragraph line
- DO NOT remove personality or informal constructions
- DO NOT add chapter headers, section titles, or summarization
- DO NOT add `(English Name)` parentheticals for foreign persons (readable disclosure pass only)
- DO NOT invent or guess `recording_date`
- DO NOT derive `recording_date` from SRT headers or cue text, raw or mix filenames, export paths, git history, file modification times, or any other file or path metadata
- DO set `recording_date` to `unknown` when no explicit user or coordinator value and no explicit episode-level date for this episode in `podcast-info.md`
- DO NOT use bold formatting for timestamps or speaker names
- DO change only what is necessary for accuracy, structure rules above, and filler removal
- DO read and process SRT content directly to produce the transcript
- DO output only the transcript content with speaker labels and timestamps
- DO insert exactly one blank line between paragraph blocks
- DO stop after writing and verifying `NNN-transcript.md`

## Usage

1. Generate SRT file from Whisper (e.g., `219-raw.srt`)
2. Open the SRT file in Cursor
3. Run this skill with the SRT file open
4. In your prompt, provide:
   - Episode number (e.g., 219)
   - Guest name
   - Host names with context (who asks questions, who gives answers)
   - For Format B (diarized with `Speaker N` labels): `speaker_map` mapping each speaker number to a full name (see Format B speaker mapping)
   - Optional `recording_date` when known (otherwise the skill writes `unknown`)
5. The skill will:
   - Read the SRT file directly
   - Detect format (A or B) automatically
   - Build timestamped paragraphs by grouping cues per Paragraph boundaries and joining text verbatim per Speech fidelity
   - Identify speakers using provided names and heuristics (Format A) or the provided `speaker_map` (Format B)
   - Apply dictionary spellings, sponsor-file fixes in sponsor segments, and fillers per Fillers
   - Create transcript file (e.g., `content/episodes/219/219-transcript.md`)
6. Review the created transcript before running downstream skills.

Do not continue with any other skill or script in the same run unless the user explicitly asks.

## Style Guide

- Transcript text remains in Russian — do not translate content
- Preserve the direct, no-nonsense tone — avoid softening statements or adding filler
- Keep technical depth intact — do not simplify technical explanations
- Wording should stay close to the SRT: spoken, sometimes repetitive. Clarity edits wait for `transcript-to-readable`

## Speaker Identification

Identify speakers using the following context and patterns:

### Known Speakers

The user must provide all speaker names when invoking the skill:

- Guest name: Required — who is being interviewed
- Host names: Required — which hosts are present in this episode

The skill uses these exact names plus heuristics to label speakers.

Use only the provided names for speaker labels — do not invent speaker names.
If speaker identity is uncertain, mark as `[неясно]: text` rather than guessing.

### Identification Heuristics

Use these patterns to distinguish speakers when the raw SRT lacks diarization:

- Hosts typically:
  - Ask questions (sentences ending with `?`)
  - Introduce the episode topic at the beginning
  - Read sponsor messages at the start (one block per sponsor) and at the end (one combined block for all closing sponsor mentions)
  - Manage topic transitions and wrap up discussions
  - Speak less overall compared to guests

- Guests typically:
  - Answer questions in detail
  - Provide technical explanations and examples
  - Speak the majority of the episode
  - Focus on content rather than managing the conversation flow

### Speaker Label Format

- Format: `(timestamp) Full Name: text of speech`
- Example: `(00:15:30) Александр Селезнев: Добро пожаловать на подкаст`
- Timestamp in parentheses, no bold formatting
- If uncertain about speaker identity, mark as `(неясно) (timestamp): text`

### Format B speaker mapping (required when labels present)

When the input contains `Speaker N` labels (`Speaker 1`, `Speaker 2`, `Speaker 3`, etc.), the user must provide a `speaker_map` in the prompt when invoking the skill:

```
speaker_map:
  Speaker 1: Александр Селезнев
  Speaker 2: Сергей Тихомиров
  Speaker 3: [Guest Name]
```

Why required: Format B exports only provide generic numbers. The skill cannot reliably infer which number maps to which person without explicit mapping.

How to apply:
1. Read the SRT file first to identify which speaker numbers appear
2. Ask the user for the mapping if not provided
3. Replace every `Speaker N` label with the mapped full name in the transcript output

If no map provided: Ask the user before proceeding. Do not guess based on heuristics alone when explicit speaker labels exist in the source.

For blocks without speaker labels (opening intros, music, pending transcription): Apply standard heuristics (hosts ask questions, guests answer) or mark as `[неясно]` if uncertain.

## Terms and Corrections

Terminology is mixed: some English terms have naturalized into Russian spelling and grammar, while newer terms remain in original English. The boundary is fluid — established terms tend toward Russian forms over time.

General rules:

- Project names: Always in English with correct capitalization (AAVE, Lido, Ethereum)
- Company names: Always in English with correct capitalization
- Established Russian terms: Use naturalized forms (блокчейн, стейкинг, коммьюнити)

Source for correct spellings:

- Read `.agents/dictionary.md` for the complete list of:
  - Spelled in English (protocols, platforms, technical terms)
  - Spelled in Russian (naturalized technical concepts)
  - Equivalent Terms (alternative forms that should be normalized)
  - Abbreviations and their expansions

Apply these spellings consistently throughout the transcript. Change only the term token; do not rewrite the sentence for grammar around English names unless the SRT form is clearly wrong ASR.

### People names (mandatory)

- **Russian persons** (hosts, Russian-speaking guests): Cyrillic in speaker labels and body. Use names from user input and `NNN-episode.yml` / `content/people/`; fix ASR only.
- **Foreign persons** (see `.agents/foreign-persons.json` and Equivalent Terms): write **Russian** given + family in the text (`Джастин Дрейк`, `Бенедикт Вагнер`, `Дэн Боне`), with case matching speech (`с Джастином Дрейком`, `с Дэном Боне` when the surname is indeclinable). Normalize ASR variants via Equivalent Terms (e.g. `Джастин Рейком` → `Джастин Дрейк`, `Виндикт Вагнер` → `Бенедикт Вагнер`).
- **Do not** insert `(English Name)` parentheticals in `NNN-transcript.md`. English canonical spellings are added later in `NNN-readable.md` only (`disclose_foreign_names.py`).
- **Do not** leave foreign researchers in Latin in the transcript body unless the speaker clearly cites a written English form letter-by-letter (rare).

### 1inch (mandatory)

Whisper often outputs `oneinch`, `Oneinch`, or spelled-out «one inch» for the sponsor and its domains.

- Always write the brand as `1inch` (digit `1`, no space) — never `oneinch`, `Oneinch`, or `One inch`.
- Always write URLs and hostnames as `1inch.io`, `1inch.dev`, `1inch.com`, `link.1inch.com`, and other official `1inch.*` forms — never `oneinch.io`, `oneinch.dev`, `oneinch.com`, or similar.
- Applies in sponsor reads, guest mentions, and any other cue; not limited to sponsor segments.

### Bitcoin vs биткоин (mandatory in Russian speech)

When the transcript is in Russian, distinguish the protocol or network from units of the asset.

- Use `Bitcoin` for the network, protocol, ecosystem, product name, and fixed English phrases (Bitcoin Conference, Bitcoin Improvement Proposal, paper titles such as «Bitcoin and quantum computing», comparisons «Ethereum и Bitcoin», «на Bitcoin», «подход Bitcoin», «обновления Bitcoin», «supply Bitcoin» as the protocol cap, «security budget Bitcoin», «Bitcoin-разработчики»).
- Use russified forms for amounts and countable units of the currency: `биткоин`, `биткоины`, `биткоинов` (and other cases as grammar requires), e.g. «6–9 миллионов биткоинов», «количество биткоинов», «перевести биткоины», «лимитированное количество биткоинов», «холдишь биткоин».
- Do not write «миллионов Bitcoin» or «количество Bitcoin» when meaning coins; Whisper may output «биткоин» — keep or normalize to the correct Russian case, do not replace with `Bitcoin` unless the speaker clearly means the network.

### Data sizes (mandatory in Russian speech)

When the transcript is in Russian, write units of data size in Russian, with correct grammar after numbers.

- `байт`, `байта`, `байтов`; `килобайт`, `килобайта`, `килобайтов`; `мегабайт`, … (not `byte`, `bytes`, `kilobyte`, `KB` in spoken-size phrases such as «600 байт», «несколько килобайт», «в байтах считать»).
- Keep English only in fixed proper names or spec labels if the speaker cites them verbatim (rare); default for sizes is Russian.

### use case (mandatory in Russian speech)

Write `юз-кейс`, `юз-кейса`, `юз-кейсы`, `юз-кейсов` (hyphenated) instead of English `use case` / `use cases` / `use-case` in Russian transcript lines; inflect for grammar.

## Sponsor read segments

At the start (and sometimes end) of the episode the host reads sponsor messages. Whisper often garbles names, numbers, and product terms in these blocks.

### Which sponsor files apply

1. Take episode number `NNN` from the job.
2. In `content/sponsorships/`, open every `*.md` (except templates) whose frontmatter has `first_episode` ≤ `NNN` ≤ `last_episode`.
3. Use `organization` (resolve display name via `content/organizations/<slug>.yml` when needed) and the bodies under `Episode read: start` and `Episode read: end` as reference only (including numbered variants under `### Вариант …` if present).

If no file matches, use `.agents/dictionary.md` and context from the SRT only.

### How to use sponsor copy (important)

The host is not reading the sponsor file verbatim. They may follow one variant closely, paraphrase, or skip lines within a single sponsor read. The transcript must reflect what was said for each sponsor, not the approved script. Structural rules for sponsor blocks differ at the start vs the end of the episode (see below); apply them even when the host flows from one sponsor to the next without a long SRT gap.

Consult sponsor files only when needed to fix:

- obvious ASR or spelling errors (бренд, продукт, URL, метрики),
- unclear wording where the sponsor text makes the intended fact unambiguous,
- inconsistent capitalization or naming (see 1inch (mandatory) under Terms and Corrections — never `oneinch` in brand or URLs; also Zerion API, GOSH, Acki Nacki, Fluence, MEV, DeFi Llama, etc.).

Do not:

- replace the host’s wording with a variant from the sponsor file,
- add claims, metrics, or CTAs that the host did not say,
- pick one `### Вариант` and treat it as the only correct text.

When the host’s meaning is clear but phrasing differs from every variant, keep the host’s phrasing and fix spelling only.

### Opening sponsor segment (start of episode)

After the intro, when the host reads start-of-episode sponsors (`Episode read: start` in applicable sponsor files):

- One paragraph block per sponsor that is actually read for this episode, in the order read on the show.
- Do not merge two sponsors into one transcript block, even if the same host speaks through both without a long SRT gap or the cues look like one continuous turn.
- Start each block at the timestamp of the first SRT cue for that sponsor’s read.
- Text inside each block still follows Speech fidelity (join cues for that sponsor only; no copy-editing).
- If a sponsor that applies to this episode number was skipped in the recording, do not invent a block for it.

Use sponsor file names and copy to recognize where one sponsor read ends and the next begins (brand mention, product pivot, typical CTA). When uncertain, split at the clearest sponsor boundary rather than keeping one long combined block.

### Closing sponsor segment (end of episode)

When the host reads end-of-episode sponsors (`Episode read: end` in applicable sponsor files), typically after patron thanks and before the sign-off:

- One paragraph block for the entire closing sponsor segment, in the order read on the show.
- Do not split closing sponsors into separate transcript blocks, even if the SRT has a new cue per sponsor or per brand name.
- Start the block at the timestamp of the first SRT cue of that segment (often the line that introduces sponsors after patron thanks).
- Join all consecutive cues from the same host that belong to the closing sponsor roll call into that single block per Speech fidelity.
- On the show, each sponsor at the end is usually a one-sentence (or one short clause) mention; preserve that rhythm in the joined text — do not expand from sponsor-file long reads, and do not drop a sponsor the host actually named.
- Patron thanks immediately before the closing sponsor list may stay in the preceding block if it is a separate thought; once the host begins naming end sponsors, keep those names in the one closing sponsor block through the last sponsor mention before the final sign-off.

### Boundaries

Apply paragraph and filler rules as elsewhere in sponsor segments. Patreon/Boosty thanks are not sponsor-file content unless a matching sponsor file exists.

### Patron URLs

Read the Patron support section in `podcast-info.md` for this show’s canonical patron URLs.

When the host mentions Patreon, Boosty, or reads a patron link (including spoken «slash», dotted domains, or garbled path segments from ASR), recognize the reference and write the matching URL from `podcast-info.md` in normal slash form. Do not invent URLs or copy ASR literally when the intent is clearly the show’s patron link.

## Context Reference

See `../../../podcast-info.md` for podcast metadata, hosts, goals, and patron URLs.
For `recording_date`, use only explicit user or coordinator input or an episode-level date in `podcast-info.md` — never infer from files on disk.
Follow `.agents/editing-standards.md` for year formatting and other common editing rules.
