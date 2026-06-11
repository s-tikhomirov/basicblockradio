---
name: readable-to-shownotes
description: >-
  Draft Basic Block Radio show notes from NNN-readable.md (title, intro,
  timecodes, Ссылки from a user URL list, sponsors from sponsors/current).
  Use when the user asks for shownotes, show notes, таймкоды, or episode links.
disable-model-invocation: true
---

# readable-to-shownotes

Produce Russian show notes for publication from a reviewed readable transcript.
Output title, intro, timecodes, episode `Ссылки:` (from a user-supplied URL list), and sponsor lines from `sponsors/current/`.

## Scope (this skill only)

When this skill is invoked, complete only the work described here and stop.

- Input: `episodes/NNN/NNN-readable.md` (after human review of the readable)
- Output: `episodes/NNN/NNN-shownotes.md` (same numbering as `NNN-readable.md`, `NNN-transcript.md`; body structure per `episodes/templates/shownotes-template.md`)
- Read: episode frontmatter, `podcast-info.md`, `.agents/dictionary.md`, active files in `sponsors/current/`

Do not: edit `NNN-readable.md`; run `scripts/`; invent episode URLs or add links the user did not supply; invent sponsor URLs or rewrite `Shownotes line` text; rewrite the readable line-by-line; translate to English.

Do not continue with transcript or readable skills in the same run unless the user explicitly asks.

## Input

Required when invoking:

- Episode number `NNN` (from filename or user prompt)
- Path to readable if not the default `episodes/NNN/NNN-readable.md`

Episode links (for `Ссылки:`):

- Preferred: a raw list of URLs (and optional short hints) in the prompt when invoking the skill.
- If omitted: still write the rest of the show notes and leave a `Ссылки:` placeholder; remind the user to re-run with the link list.

## Output file

Write `episodes/NNN/NNN-shownotes.md` (not `shownotes.md`):

1. YAML frontmatter — same fields and order as `episodes/templates/shownotes-template.md` (copy from readable, including `recording_date` verbatim). Do not invent or derive `recording_date`; if missing in readable, use `unknown`. Change it only when the user explicitly provides a date in the prompt.
2. Body in publication order (plain text, Russian):
   - Title line
   - Blank line
   - Intro (one or more paragraphs; optional sponsor disclaimer if guest ↔ sponsor)
   - Blank line
   - `Таймкоды:` header
   - Timecode lines (see Timecodes)
   - `Ссылки:` (see Episode links) — before sponsors
   - `Спасибо нашим спонсорам!` with sponsor list (see Sponsors in shownotes)
   - Fixed podcast footer (see Podcast footer) — always last; plain URLs, not markdown

## Title

- `ББ-{N}:` + hyphen (not `ББ 218:`). Under 100 characters; shorten the theme before dropping the guest.
- Default — guest interview: `Имя Фамилия (Организация) о …` / `об …` (e.g. ББ-213, ББ-205). Two guests: `Имя и Имя (Org) о …`. Colon instead of «о» when the subtitle is a list: `ББ-219: Василий Шаповалов: Lido, Ethereum и DeFi…`
- Document-centered (Messari): `Отчёт Messari-YYYY. Часть N. …` + `(feat. Имя Гостя)` when you discuss the report with a guest (ББ-217, ББ-215; `(ft. …)` if the user prefers).
- Event-centered: `Devcon… Часть 1: …` — guest names usually not in the title.
- Use о / об, not про, in new titles. First body line after frontmatter, not a markdown heading.

## Prose style (intro, preview, timecode labels)

Apply to all show-notes Russian you write (not to sponsor lines copied from files).

Sentences: prefer short. One idea per sentence when possible. Avoid long chained clauses.

Technical terms: use only if correct (check `.agents/dictionary.md` and the readable). If unsure, use a simpler phrase or omit. Example: do not write «открытая криптография» for TLS/Web3 keys — say «асимметричная криптография» or just «криптография» where context is enough. When the thread is crypto threat or migration, you may write «CRQC» instead of «квантовый компьютер» if meaning is clear (see dictionary).

Register: avoid podcast slang («база», «разнос», «отжать тему», «под квант», «против кванта», «квант» as shorthand). Name mechanisms plainly: пост-квантовая криптография, устойчивость к CRQC, миграция PKI, гибридные схемы подписей. For episode structure prefer «теория», «основы», «первая часть», «продолжение в следующем выпуске».

Guest credentials: concrete facts from the readable (разработал…, соавтор…, участвовал в стандартизации…, PhD, компания). Do not pad with empty praise («с академической и прикладной стороны», «уникальный эксперт», «глубоко разбирается»).

What to promise in the intro: include only topics that have real weight in `NNN-readable.md` — sustained discussion, not a passing name-drop. Scan the readable for depth (several blocks, back-and-forth, explanations). Do not tease a deep dive («как устроены алгоритмы X») if the episode only mentions X in passing.

Wording: prefer positive statements. Avoid negations, «без …», «а не …», «не X, а Y» unless essential for accuracy. Never use podcast-meta phrases like «без булшита», «без паники», «без магии» in show notes (including timecode labels).

Tone (`podcast-info.md`): rigorous and conversational, not adversarial to the guest. Direct address OK on series episodes. Editorial wit is rare and never via «без булшита»-style lines.

Open vs closed: hooks may use questions and tension; do not hang the whole intro on verdicts. Messari may list themes covered after the hook without spoiling each answer.

Hook and guest voice: weight what the guest actually says over host color. If the host opens with a catchy frame (industry mood, «все говорят X») and the guest does not echo or own that angle, do not build the hook only on the host line — use a question, a fact from the guest’s thread, or the episode’s technical stake instead.

Brevity vs completeness: cut fluff, but every noun phrase must carry meaning. Do not leave bare labels («гибридные схемы», «внедрение», «миграция») without saying what (гибридные схемы подписей, внедрение пост-квантовой криптографии, миграция TLS).

## Intro

Length: usually 2–4 short paragraphs; deep architecture episodes may stack brief paragraphs («Обсуждаем…», «Также…») — each obeying Prose style.

Order of ideas (pick what fits):

1. Hook — see «Hook and guest voice»; prefer guest-backed or technical stakes over host-only rhetoric.
2. Why this episode — «чтобы разобраться…», «позвали», «пригласили».
3. Guest(s) — role, employer, concrete credits (standards, papers, products); for Messari — co-reader of the report.
4. Preview — only substantive arcs from the readable (see Prose style); open questions OK. Messari: tradition + invite listener (ББ-214); optional topic list after critical hook (ББ-215).
5. Sponsor disclaimer — before `Таймкоды:` if guest ↔ sponsor (below).

Episode shapes (reference):

- 216: industry scene → why we invited → product → preview of real threads.
- 215 / 214: report angle; feat. guest; playful bullets only when the episode actually goes there.
- 213 / 212: layered technical summary — facts from readable only.

Do not paste long quotes from readable. Guest and topic URLs belong in `Ссылки:` when the user supplies them.

### Sponsor disclaimer (guest ↔ sponsor)

If the guest’s organization matches a sponsor named in the readable (GOSH / Acki Nacki, Fluence, 1inch, Zerion — check the sponsor block), add before `Таймкоды:`:

```
Дисклеймер: {Организация} – спонсоры нашего подкаста. Выпуск подготовлен по нашим обычным редакционным стандартам. Ведущие сделали всё возможное, чтобы он не был излишне комплиментарным.
```

Example: GOSH for ББ-212. If affiliation is unclear, ask the user.

## Timecodes

### Where timestamps come from

Readable lines: `(HH:MM:SS) Speaker: text`. Each line is one block.

Anchor each timecode to the block that introduces the topic for the listener — the moment the question or new thread begins — not to the start of the guest’s answer.

How to pick the block:

1. Read forward in the readable for the arc your label describes.
2. Find the paragraph that poses the question, names the subtopic, or opens that thread (often a host question; sometimes the guest pivots with «давайте про…», «следующий вопрос…», or a long setup).
3. Use the timestamp on that introducing block. If the host asks and the guest then answers at length, stamp the host’s question block, not the first line of the answer — unless the label is specifically about what the guest said in reply, then still prefer the question that prompted it when the label reads like a chapter title for the thread.
4. If the topic starts mid-guest monologue without a prior question, use the guest block where the new thread clearly begins.
5. Highlights (punchline, controversy): stamp the block where the turn happens, which may be inside an answer; still avoid stamping only the tail if the setup was one block earlier and the label refers to the whole exchange.

The timestamp must match an existing readable line. Do not invent times between blocks.

Cover major arcs (~20–30 lines per ~1.5 h is typical). You do not need a line for every subject touched once. No filler transitions.

### Line format

- Header: `Таймкоды:` then a blank line.
- One bullet per topic: `- {time} — {label}` (markdown list item; em dash between time and label).
- Convert time: `HH == 00` → `MM:SS`; `HH >= 01` → `H:MM:SS` (e.g. `03:45`, `1:03:00`)

### Label style

Follow Prose style. Each label is one short statement: one topic, one question, or one claim. Avoid laundry lists joined with «и», «а также», commas of equals («X, Y и Z»). If several topics fall in the same time window, pick the single most interesting or central thread for that stamp — not a summary of everything said.

Prefer compressing over stacking:

| Too long / parallel | Shorter |
|--------------------|---------|
| Кубиты, запутывание и новый класс вычислений | Запутывание кубитов |
| Центр X и ответвление Y | Центр X (if Y is side note) |
| Как NIST выбирает стандарты и расставляет дедлайны | Как NIST выбирает стандарты |
| Кто строит квантовые компьютеры и насколько это закрыто | Квантовые компьютеры строят в секрете? |

Keep objects explicit when the label names a mechanism or policy (see «Brevity vs completeness» in Prose style).

| Pattern | Example |
|--------|---------|
| Question from the show | `Можно ли исключить людей-аудиторов?` |
| One thread | `Harvest Now, Decrypt Later` |
| Segment | `Итоги` |

Chronological order. Never use the same timestamp twice; merge labels into one line if needed.

## Episode links (Ссылки)

Section comes after `Таймкоды:` and before `Спасибо нашим спонсорам!`.

### When the user did not supply links

Still produce title, intro, timecodes, and sponsors. Add:

```
Ссылки:

- *добавить: передайте список URL при следующем запуске skill*
```

Tell the user show notes are incomplete until they provide the raw link list and you fill `Ссылки:`.

### When the user supplied a raw link list

1. Normalize to full `https://…` URLs (dedupe).
2. Open/fetch each URL when possible. Write the markdown link text from the page title or an honest short name.
3. Language: link text follows the page (English page → English title; Russian page → Russian title). Do not translate paper titles or product names. English names of people, brands, conferences, and projects stay in English inside Russian link text or clarifications (Dan Boneh, ACM CCS, Coinbase, Zero Knowledge). The readable file may contain one-time ` (English Name)` disclosures after Russian foreign names; show-note prose and links still use English canonical from the source page, not a duplicate parenthetical in every mention.
4. Style: brief; no em dashes, en dashes, or hyphen chains in link text.
5. Resource type: say what it is either inside the link text or in parentheses after the link, or skip if obvious. Examples: `[Подкаст Zero Knowledge 400: Dan Boneh](url)` needs no extra tag; `[SPHINCS+](url) (Википедия)` when the title alone is unclear.
6. Parenthetical clarifications are usually in Russian: (личный сайт), (диссертация), (статья), (доклад, 2023), (блог Google). Keep English tokens inside them when they are names (ACM CCS 2019, Coinbase). Omit parentheses when the link text already states the type (reading list, podcast in the title, and similar).
7. One link per list line: each URL is its own `- ` bullet with a single markdown link (optional parenthetical after that link only). Never put two links on one bullet.
8. Related links (same guest site, same topic): place consecutive bullets together; homepage before other paths on that domain. Each line still follows rules 5–6.
9. If fetch fails, use the user’s hint, readable context, and URL path. Do not invent titles.
10. Order bullets:
   - First: main guest or topic anchor (guest site group, key report, main project).
   - Then: roughly order of mention; keep related URLs in consecutive bullets (rule 8).
11. Format:

```
Ссылки:

- [Mikhail Kudinov](https://example.com/) (личный сайт)
- [Materials for cryptography and computer science](https://example.com/materials)
- [Подкаст Zero Knowledge 400: Dan Boneh](https://example.com/episode)
```

Do not add URLs that were not in the user’s list (sponsor URLs stay only under `Спасибо нашим спонсорам!` from sponsor files).

## Podcast footer (fixed)

After `Спасибо нашим спонсорам!`, append this block verbatim (blank line before it). These three lines are plain text with spelled-out URLs — not markdown links:

```
Поддержите подкаст! https://basicblockradio.com/donate/

Заходите в наш чат: https://t.me/basicblockradio_chat

Наш сайт: https://basicblockradio.com/
```

Do not rephrase or reorder. Every complete `NNN-shownotes.md` ends with this footer.

## Sponsors in shownotes

After `Ссылки:`, append the sponsor block from sponsor files (not from the readable transcript).

### Which sponsors apply

Same rule as `srt-to-transcript`: episode `NNN`, include every `sponsors/current/sponsor-*.md` where `first_episode` ≤ `NNN` ≤ `last_episode`.

### What to insert

From each file, take the single line under `## Shownotes line` (trim whitespace). Copy it exactly — do not rephrase. If the section is empty, skip that file and tell the user.

### Section format

```
Спасибо нашим спонсорам!

- {Shownotes line}
- {Shownotes line}
```

Use a markdown bullet list (`- `). Header line exactly `Спасибо нашим спонсорам!`, blank line, then bullets.

### Order (randomized)

Do not list sponsors in filename order or read order. Shuffle the bullet lines into a random order.

Use episode number `NNN` as the shuffle seed so the same episode gets the same order if show notes are regenerated (e.g. order sponsors by hash of `name` + `NNN`, or a documented deterministic shuffle). Do not always put the same brand first.

## Workflow

1. Read `NNN-readable.md`, frontmatter, `podcast-info.md`, `.agents/dictionary.md`, and matching `sponsors/current/sponsor-*.md`.
2. Outline topics and highlights with timestamps.
3. Draft title (under 100 characters).
4. Draft intro (+ disclaimer if needed).
5. Build timecodes (anchor to topic-intro blocks, not answer starts); verify each time against readable blocks.
6. Build `Ссылки:` from the user’s link list (or placeholder if missing); fetch URLs to label; order logically.
7. Collect `Shownotes line` from each active sponsor file; shuffle order (seed `NNN`).
8. Write `NNN-shownotes.md` in publication order; append the podcast footer last.
9. Report: missing sponsor `Shownotes line`; incomplete `Ссылки:` if no URL list was provided.

## Quality check

- [ ] Output file is `episodes/NNN/NNN-shownotes.md`
- [ ] Title under 100 characters, `ББ-NNN:`
- [ ] Intro: short sentences, correct terms, concrete guest facts, preview matches readable weight; no «без булшита» / «без магии»
- [ ] Timecodes: each line is `- {time} — {label}`; labels on topic intro blocks (usually question), not guest-answer starts; timestamps valid
- [ ] `Ссылки:` one URL per bullet; related URLs consecutive; types in link text or Russian `(уточнение)`; English names preserved
- [ ] Link order: main guest/topic first, then logical/mention-based order
- [ ] Sponsor bullets match `Shownotes line`; order shuffled (seed `NNN`)
- [ ] No URLs in `Ссылки:` except from the user’s list
- [ ] Podcast footer appended verbatim (plain URLs, last block)
