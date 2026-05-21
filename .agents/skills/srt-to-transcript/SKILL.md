# srt-to-transcript

Turn Whisper SRT into a structured transcript file. Establishes speakers, timestamped paragraphs, spelling, and light cleanup. Does not rewrite blocks for readable prose.

## Scope (this skill only)

When this skill is invoked, complete only the work described here and stop.

- Produce `episodes/NNN/NNN-transcript.md` from the raw SRT.
- Do not run `scripts/` under `knowledge-bases/basicblockradio/`.
- Do not generate Python or shell tools to transform SRT or transcript text.
- Do not start readable copy-editing or create `NNN-readable.md`.
- Do not split or merge transcript files for downstream passes.

## Purpose

Clean up Whisper output and freeze episode structure:

- Fix spelling in technical terms, names, and projects (`.agents/dictionary.md`)
- Correct obvious mistranscriptions
- Merge SRT cues into paragraphs with one timestamp per paragraph (see Paragraph boundaries)
- Standardize speaker labels and timestamp format
- Remove obvious noise fillers and false starts without changing meaning
- Do not merge or split paragraphs for readable prose; only structural boundaries per rules below

## Input

Required in user prompt when invoking skill:

- Episode number (extract from filename like `219-raw.srt` → 219, or ask if unclear)
- Guest name (who is being interviewed)
- Host names (who is asking questions)

Content being edited:

- Raw SRT file with timestamped segments (the AI reads this directly)

Context sources (read by the skill):

- Technical terms from `.agents/dictionary.md`
- Podcast metadata from `podcast-info.md`

Processing approach:

- The AI reads and parses the SRT file directly
- Builds paragraphs from consecutive SRT cues (same speaker, within duration limits)
- Agent-driven from SRT only — no parser or batch scripts in this workflow

## Output

New transcript file `episodes/NNN/NNN-transcript.md` containing:

- Frontmatter with episode context:
  - episode: episode number
  - guest: guest name (from user input)
  - hosts: host names (from user input)
  - recording_date: if available from podcast-info.md
  - status: raw
- Transcript content only — no chapter headers, no summarization
- Format: `(HH:MM:SS) Speaker Name: text of speech`
- Timestamp format: parentheses, not bold — `(00:15:30)`
- Example: `(00:15:30) Александр Селезнев: Вопрос о стейкинге...`
- Consistent speaker labels
- Corrected technical terms from dictionary
- Preserved informal tone

Note: The output filename starts with episode number (e.g., `219-transcript.md`).

## Paragraph boundaries

Each output line is one paragraph block. The timestamp on the line is the start time of that block (time of the first SRT cue merged into it).

Priority: group SRT cues into one block while a single speaker continues one coherent topic or answer. Split on topic and turn boundaries first; use duration only as a soft guardrail.

Always start a new paragraph when:

- The speaker changes
- The guest’s answer clearly ends and the host asks a new question (host question often gets its own block)
- The conversation shifts to a new topic (new question, new sub-question, sponsor read, intro or outro segment)
- A long pause in the SRT (clear break in recording) suggests a natural boundary

Prefer to keep one block when:

- The same speaker is still developing the same answer or thread, even past about two minutes, if there is no clean topic break

Soft duration guideline (not a hard cap):

- Rough guide: many blocks fall in the one-to-three minute range; about two minutes is typical, not a maximum
- Measure span from the block start timestamp to the end of the last SRT cue in that block
- If the same speaker continues one topic well beyond about three to four minutes with no natural break, consider splitting at the nearest SRT gap or sentence boundary so later copy-editing is not faced with one enormous paragraph — but do not split mid-thought just to satisfy a timer
- If a block is very long because the topic is long, that is acceptable

Do not merge cues across different speakers.

Paragraph boundaries in the transcript file are the canonical structure for the episode. Do not merge or split blocks for style in this skill.

## Fillers (bulk cleanup)

Remove when clearly noise only, without changing meaning: ну, значит, короче, типа, вот (standalone), так что (sentence start), вот как-то / так вот / вот именно, знаешь, понимаешь, слышишь, как бы, собственно, типа того, получается (pause), по-моему / не знаю / наверное (empty hedge), кстати (empty), там / вот там, false starts.

Context-dependent: и так далее, и все такое, короче говоря, все такое — keep if they narrow a list or sum up; drop if trailing off. точно-точно / ну-ну / вот-вот — drop as backchannel agreement; keep if emphatic or part of the thought (вот-вот, в этом суть).

«типа» is always a filler. «это» only when clearly empty pause-filler, not when grammatically needed.

You do not need to catch every disfluency; remove obvious noise only. Do not copy-edit for readable flow or cut redundancy inside blocks beyond filler cleanup.

## Constraints

- DO NOT run or write scripts under `knowledge-bases/basicblockradio/scripts/`
- DO NOT generate scripts or tools that transform transcript prose
- DO NOT create `NNN-readable.md` or perform readable-style rewriting
- DO NOT soften direct statements
- DO NOT add transition phrases or corporate speak
- DO NOT restructure sentences for style (fix obvious errors and fillers only)
- DO NOT remove personality or informal constructions
- DO NOT add chapter headers, section titles, or summarization
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
5. The skill will:
   - Read the SRT file directly
   - Build timestamped paragraphs per Paragraph boundaries
   - Identify speakers using provided names and heuristics
   - Apply correct spellings from dictionary.md and fillers per Fillers
   - Create transcript file (e.g., `episodes/219/219-transcript.md`)
6. Review the created transcript
7. Update frontmatter status to edited when satisfied

Do not continue with any other skill or script in the same run unless the user explicitly asks.

## Style Guide

- Transcript text remains in Russian — do not translate content
- Preserve the direct, no-nonsense tone — avoid softening statements or adding filler
- Keep technical depth intact — do not simplify technical explanations
- Preserve a friendly but technically demanding tone: conversational and rigorous, with precise questions and answers intact

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
  - Read sponsor messages at the start and end of the episode
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

Apply these spellings consistently throughout the transcript.

## Context Reference

See `../../../podcast-info.md` for podcast metadata, hosts, and goals.
Read episode frontmatter for guest name and recording date.
Follow `.agents/editing-standards.md` for year formatting and other common editing rules.
