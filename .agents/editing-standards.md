# Editing Standards

Repository-wide editing standards for all transcript and content work.

## Year Formatting

Spell years fully using 4-digit format (2020, 2021, etc).

- Convert abbreviated forms: "20-м году" → "2020 году", "в 20-м" → "в 2020-м"
- Convert written forms: "в двадцатом году" → "в 2020 году"
- Never use 2-digit years like "20" or "19" — always "2020", "2019"
- Never interpret "в 20-м" as "в 1920-м" — always assume 2000s for podcast content

### Examples

| Input | Output |
|-------|--------|
| в 20-м году | в 2020 году |
| в начале 20-го | в начале 2020-го |
| конец 21-го | конец 2021-го |
| в 17-м году я начал | в 2017 году я начал |
| между 2020 и текущим | между 2020 и текущим (keep as-is) |

This applies to all markdown files: transcripts, readable versions, show notes, shorts clip maps, documentation.

Short-form files (`NNN-shorts.md`) use Russian editor fields and verbatim transcript lines only. Do not copy-edit guest speech inside kept spans; montage is marked with `<...>` per `transcript-to-shorts` skill.
