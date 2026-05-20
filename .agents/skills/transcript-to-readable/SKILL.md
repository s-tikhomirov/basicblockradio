# transcript-to-readable

Transform an edited transcript into a readable version by removing filler words, merging segments by topic, and restructuring for clarity while preserving the direct-speech format.

## Purpose

Aggressively polish an edited transcript into a fluid, readable form while maintaining:
- Direct-speech format with speaker attribution
- First-person perspective of each speaker
- One timestamp per logical section
- All technical content, facts, and semantic meaning

This transformation removes all conversational artifacts of live speech: filler words, fragmented sentences, repetitive phrasing, and jumpy ordering — without converting to third-person narrative.

## Input

Content being transformed:
- Edited transcript file `episodes/NNN/NNN-transcript.md` with `status: edited`

The skill infers the episode number from the filename and reads the transcript directly.

## Output

New file `episodes/NNN/NNN-readable.md` containing:
- Frontmatter copied from source with `status: readable`
- Polished transcript with same speaker-timestamp format
- Merged paragraphs by topic within speaker boundaries
- Removed filler words and smoothed sentence flow

Output format preserves the structure of the edited transcript:

```
(00:06:28) Василий Шаповалов: Полированный текст без заполнителей, объединенный из нескольких сегментов на одну тему...
```

## Constraints

- DO NOT convert to third-person narrative
- DO NOT add editorial commentary or interpretation
- DO NOT remove timestamps entirely — keep one timestamp per merged paragraph
- DO NOT change technical content, numbers, or factual claims
- DO NOT soften or intensify statements — preserve original tone and emphasis
- DO NOT merge speech from different speakers into one paragraph
- DO NOT add chapter headers or section titles
- DO NOT use bold formatting for timestamps or speaker names
- DO preserve first-person pronouns and direct speech perspective
- DO maintain speaker attribution for every paragraph

## Transformation Rules

### 1. Speaker Boundaries

Never merge speech from different speakers. Each paragraph belongs to exactly one speaker.

### 2. Aggressive Topic-Based Merging

Merge consecutive segments from the same speaker liberally. A single paragraph may span multiple original timestamps if the speaker continues on the same general topic. Create a new paragraph only when:
- A different speaker begins talking
- The speaker explicitly answers a new question
- The subject matter shifts to a completely different topic area

Default to merging. If segments flow together conceptually, combine them into one cohesive paragraph.

### 3. Timestamp Placement

Place one timestamp at the start of each merged paragraph using the earliest timestamp from the group of segments being merged.

### 4. Filler Removal

Always remove (pure noise, never carry meaning):
- "ну", "значит", "короче", "типа", "вот" (standalone)
- "так что" (at sentence start)
- "вот как-то", "вот так вот", "вот именно"
- "знаешь", "понимаешь", "слышишь", "понимаешь ли"
- "как бы", "собственно", "типа того"
- "получается" (when used as filler pause)
- "по-моему" (when hedging)
- "не знаю" (when self-deprecating)
- "наверное" (when uncertain)
- "кстати" (when empty transition)
- "там", "вот там"
- Repetitions: "точно-точно", "ну-ну", "вот-вот" (when agreement)
- False starts and self-corrections

Evaluate in context (may carry semantic weight):
- "и так далее", "и все такое", "и так далее и тому подобное" — keep when indicating intentional non-exhaustiveness of a list; remove when clearly just trailing off
- "все такое" — keep if referring to previously mentioned category; remove if filler
- "короче говоря" — keep when genuinely summarizing; remove when just restarting

### 5. Aggressive Sentence Restructuring

Restructure sentences liberally within speaker paragraphs to create fluid, readable prose:

Do aggressively:
- Reorder sentences for logical flow — even if it means significant reordering
- Combine fragmented sentences into flowing, complete thoughts
- Break overly long run-on sentences into clearer structure
- Smooth out self-corrections and false starts completely
- Remove redundant phrases and repetitions of the same idea
- Rephrase awkward constructions while keeping the speaker's vocabulary
- Convert conversational parentheticals into integrated clauses
- Fix broken anaphora (pronouns with unclear antecedents)

Example of aggressive restructuring:
- Input: "Я посмотрел, какие будут важные темы. Буквально в первые две недели. Я посмотрел три самые важные вещи. Из вещей, которые были важны в 20-м году уже. Там были Game of Zones космосовские."
- Output: "В первые две недели я определил три самые важные темы для 2020 года: Game of Zones космосовские, запуск стейкинга на Polkadot и на эфире."

Preserve:
- Technical terms and their original phrasing
- Specific numbers, dates, and quantities
- Named entities (projects, people, protocols)
- Emotional emphasis and intentional informal constructions
- Metaphors, idioms, and figurative expressions (e.g., "объекты в зеркале ближе, чем кажется")
- Direct questions and challenges
- Humor and personality markers

### 6. Format

Maintain exactly the same format as the edited transcript:

```
(00:15:30) Speaker Name: Text of speech...
```

- One blank line between paragraphs
- Timestamp in parentheses, not bold
- Speaker name in original form
- No section headers or chapter breaks

## Processing Approach

1. Read the edited transcript file directly
2. Parse segments by speaker and timestamp
3. Group aggressively: combine consecutive segments from the same speaker unless there is a clear topic shift
4. For each group:
   - Take the earliest timestamp
   - Strip ALL filler words and conversational artifacts
   - Restructure sentences for logical flow and readability
   - Combine fragments into cohesive paragraphs
5. Output the polished transcript with updated frontmatter

Be aggressive. The goal is readable prose, not cautious preservation of transcript structure. If a speaker has 10 consecutive segments on the same topic, merge them into 1-2 flowing paragraphs.

## Example Transformation

Input (edited transcript):
```markdown
(00:06:28) Василий Шаповалов: Если быть вот совсем честным в этой истории, да, ликвидный стейкинг — это идея была не новая, когда Lido появилась. Впервые я ее прочитал в коммьюнити Космоса, где это была большой-большой темой. Космос вообще очень много сделал для какой-то теории продуктовой, какое-то развитие стейкинга как коммьюнити нод-операторов и так далее. Это была очень мощная сетка для того, чтобы стейкинг в индустрию запустить после Тезоса.

(00:06:53) Василий Шаповалов: В начале 20-го года я в середине февраля начал работать CTO в P2P-валидаторе. Тоже один из проектов Кости. Буквально в первые же две недели я посмотрел, какие будут важные темы, что мне нужно сделать в этом году. Из вещей, которые были важны в 20-м году уже, там, знаешь, объекты в зеркале ближе, чем кажется.

(00:07:30) Василий Шаповалов: Почему? Потому что он был заточен под людей, которые будут стейкать свои, у тебя дома, 32 эфира, без встроенных в протокол механизмов делегации стейкинга операторам. А большинство людей, у которых есть деньги, они стейкать не будут. То есть люди, у которых деньги, они любят, чтобы у них циферки шли вперед и вверх. Чтобы им работать было, они не любят. То есть чтобы ноду была запустить, следить за ней и так далее. Они хотят кому-нибудь делегировать это дело, как можно меньше риска взять, как можно больше APR получить.
```

Output (readable):
```markdown
(00:06:28) Василий Шаповалов: Если быть совсем честным, идея ликвидного стейкинга была не новой, когда появился Lido. Впервые я прочитал о ней в коммьюнити Космоса, где это была большая тема. Космос много сделал для развития стейкинга как коммьюнити нод-операторов — это была мощная сетка для запуска стейкинга в индустрию после Тезоса. В начале 2020 года я стал CTO в P2P-валидаторе, проекте Кости. В первые две недели я определил три ключевые темы года — объекты в зеркале ближе, чем кажется. Эфир был заточен под людей, которые будут стейкать свои 32 эфира дома, без механизмов делегации операторам. А большинство держателей капитала не хотят этим заниматься. Они любят, когда циферки растут, но не любят работать — запускать ноду, следить за ней. Они хотят делегировать это дело, взяв минимум риска и получив максимум APR.
```

## Usage

1. Ensure the transcript has `status: edited` in frontmatter
2. Run this skill with the transcript file open
3. The skill infers episode number from filename and creates `NNN-readable.md`
4. Review the readable version for accuracy and flow
5. Update frontmatter status if satisfied (e.g., to `reviewed`)

## Context Reference

The skill reads technical terms from `.agents/dictionary.md` to ensure correct spelling in the output.

See `../../../podcast-info.md` for podcast metadata and host information.

Follow repository editing standards from `.agents/editing-standards.md` for year formatting and other common rules.
