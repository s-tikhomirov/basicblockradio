---
name: improve-transcript-labels
description: >-
  Retags host speaker names in NNN-transcript.md for a range of episode
  numbers using vocatives, floor passes, topic stickiness, attendance maps,
  and host-typical phrases. Flags episodes that lack a transcript and
  episodes that already have NNN-readable.md. Use when the user asks to
  fix, improve, check, or reattribute host labels on transcripts, especially
  multi-host episodes produced from undiarized SRT.
---

# improve-transcript-labels

Correct host speaker labels on existing transcripts in a given episode range.
Transcripts from undiarized Whisper assign host names by heuristics
(the host asks, the guest answers), so which host spoke is often wrong
when two or more hosts are present.
In host-only recaps that same split inverts the table:
the reporter explains, the interlocutor asks.

## Scope (this skill only)

When this skill is invoked, complete only the work described here and stop.

- Input: a range of episode numbers from the user prompt
- Output: in-place edits to each eligible `content/episodes/NNN/NNN-transcript.md`
- Change only the speaker name on a line already labeled as a host
- Keep timestamps, paragraph text, blank lines, frontmatter, and block count
- Do not split or merge blocks
- Do not create or edit `NNN-readable.md`
- Do not run `scripts/` under this knowledge base
- Do not generate Python or shell tools to retag lines

## Input

Required in the user prompt:

- Episode range (inclusive), e.g. `200–223`, `201-218`, or `201 202 204`

Expand the range to every integer from start through end.
A comma- or space-separated list is a set of those numbers, not a span.

Before editing any file, scan every number in the range and flag:

- Missing transcript: no `content/episodes/NNN/NNN-transcript.md`
  (missing folder counts as missing transcript)
- Already checked: `content/episodes/NNN/NNN-readable.md` exists,
  or `NNN-episode.yml` `status` is `transcript-reviewed`, `readable-reviewed`, or `ready`
  (the spoken record already had a human pass)

List both flags in chat before retagging.
Skip those episodes: do not open them to retag, do not edit them.
Continue with the remaining episodes that have a transcript and no readable.

For each remaining episode, read before editing:

- `content/episodes/NNN/NNN-transcript.md`
- `content/episodes/NNN/NNN-episode.yml` (`hosts`, `guests`)
- `content/people/<slug>.md` for Cyrillic `name` of each host and guest slug

Show roster (always hosts when they speak, even if YAML lists one as a guest):

- Александр Селезнев (`alexander-seleznev`) — Саша, Саш, Александр
- Сергей Тихомиров (`sergei-tikhomirov`) — Сергей, Серёжа
- Иван Иваницкий (`ivan-ivanitskiy`) — Ваня, Вань, Иван
- Евгений Марченко (`evgeny-marchenko`) — Женя, Евгений

Use those full Cyrillic names in labels. Do not invent names.

## Classify the episode

Build the host set for this episode:

- Every YAML `hosts` slug, resolved to `name`
- Plus every roster member who appears as a speaker in the transcript

Guest speakers are everyone else named on a transcript line.

Then, for that episode:

- One host in the host set → skip retagging. Note it as single-host and continue the range.
- Every speaker is in the host set → host-only (two hosts talk to each other).
- At least one speaker is outside the host set → hosts+guest (interview or roundtable with an outside guest).

Apply the shared heuristics in both formats, then the format-specific ones.

## What to change

Walk every block `(HH:MM:SS) Name: text`.

If `Name` is in the host set and heuristics show a different host in that set,
replace `Name` with that host’s full Cyrillic name.

Leave the line unchanged when:

- `Name` is a guest
- the current host label is consistent with the cues
- two hosts could both have said the line
- the only cue is a weak prior (new topic, voice, late first appearance of the second host)

Late first appearance of the second host is a reason to look, not a reason to spread questions evenly.

A block that contains two hosts’ speech (vocative plus another person’s recap in one line) still gets one label.
Pick the speaker of the identifiable vocative or floor-pass clause. Do not split the line.
If a recap paragraph also contains an interlocutor cue
(«follow-up», «глупый вопрос», «можно напомнить») and there is no vocative,
keep the recap speaker.
Retag that cue only when it already has its own timestamp.

## Shared heuristics

Use these in both host-only and hosts+guest episodes. Strongest first.

### Vocatives and named address

Someone says «Саш», «Саша», «Сергей», «Ваня», «Вань», «Женя», or a full name
in a way that points at a person at the table.

- The addressee is not the speaker of that block.
- A guest answering «мы с тобой, Саш, и познакомились» pins the previous host turn as Александр.
- «Сергей, ты хотел спросить» pins the next host turn as Сергей.
- «мой соведущий Иван» means the speaker is not Иван.
- Third person for the audience: «мы с Сергеем сидим в одной комнате» is Иван;
  «спасибо Ване» is not Иван.

### Self-identification in the show frame

Opening and closing often name the speaker:
«у микрофона сегодня я, Сергей Тихомиров».
Without «я», naming a cohost is a greeting, not self-ID.
«У микрофона Иван Иваницкий. Привет.» is the unnamed host speaking.
The named host’s next line is the short hello («Привет, друзья»).
«И я, Сергей Тихомиров» continues the unnamed host’s intro,
including when it was glued onto the hello.

Sponsor reads stay with one host for a stretch;
a second host usually marks the handoff («И добавлю я»).
A one-line sponsor thank-you after the other host names that sponsor
(«Спасибо, Zerion, спонсор») is the sponsor-reader,
not the host who mentioned the product.
Reliable for the first minutes and for those sponsor stings.
It does not decide later interview questions.

### First-person facts

Personal history with the guest, a previous episode they hosted,
a paper they read, a job, a conference they attended.
«Женю я очень давно хотел позвать» belongs to the host who owns that story.
These pin even in the middle of the other host’s recap
(«документацию у нас в Waku», «я работаю в Reactive Network»).
Rare and strong when they appear.

### Topic stickiness (hosts+guest)

A clarification of the last answer
(«правильно ли я понял», «то есть», «follow-up по этой части»,
«у меня еще вопрос по вот этому разделу»)
stays with the host who asked the question that produced that answer.

A new question after the guest has finished is not that clarification,
even on the same subject.
«В каком регионе самые ценные пользователи» after «вы работаете в Европе»
is a new question.
The other host often asks it, and often takes a tangent from a long guest answer
(a regulatory aside, a vendor, a product the first host did not pursue).

A new topic or «давай перейдем» is only a weak prior for a host change.
The same host often closes one thread and opens the next,
especially the host running the episode.
Same-subject adjacency is only a weak prior for giving the turn back
to the previous host.

Before retagging host B to host A on stickiness, look at the next host turns.
If those turns are already B, or are soon pinned as B
(vocative, prepared block, guest addressing that host),
keep B.

In host-only, a follow-up is the interlocutor’s probe.
The answer is the reporter’s. See Reporter versus interlocutor.

### Hosts talking to each other

Two host blocks in a row, or a joke or aside after a technical thread
(«а я хотел полу пошутить»), often the other host entering.
Host A asks, the guest answers at length, then a full new question:
often host B, including when the subject is adjacent.
Short reactions («да», «узнаваемо») are weaker than a full new question.

### Voice phrases

Typical phrases are a prior on that block, never enough alone unless listed as strong.
Combine with vocative, floor pass, attendance, or stickiness.
See Typical phrases below.
Do not use «мне кажется», «как будто», «в целом», «можешь рассказать»,
sponsor-read wording, or guest-directed «ты сказал» / «ты сказал, что»
to choose a host.

## Hosts+guest heuristics

Guest-versus-host is usually already correct. Only retag host-versus-host.

The interview ask/answer split does not distinguish hosts.
Both hosts ask questions.

Prepared-block handoffs are strong:
«у нас был целый блок про KYC», «Вань, у тебя есть сейчас какая-то тема»,
«моя тема связана с…».
After an explicit handoff, the next long host turn is the named person.

Clarifications of that person’s answers stay with them
even if the intro host currently owns the label.
Use that to move an intro-host label onto the prepared-block host.
Keep a second-host label when the running host asked about a nearby subject.

## Host-only heuristics

Both hosts report, both ask, both react.
Treat the episode as two reporters sharing a table.

### Opening menu

Early on, each host lists what they attended or which half they will cover.
That list is the speaker map for the rest of the episode.
A long recap of a named event belongs to the host who put it on their list.

### Floor passing

«передаю микрофон Ивану», «расскажи, что посетил ты»,
«давай теперь поменяемся местами»
name who speaks next.
After a handoff, the next long block is that person.
The one who just handed off becomes the short-question host until the next handoff.
«switch gears» names a topic change.
The reporter often says it on their own event.
Treat it as a host change only when it names a person.

### Reporter versus interlocutor

Whisper’s interview heuristic (who asks vs who explains) inverts this table.
The reporter explains. The interlocutor asks.
Pairs and short sequences come out swapped.

While one host is on their event, they get the long turns
(talk recaps, «следующий доклад»).
The other host gets the probes
(«можно напомнить, что такое…», «глупый вопрос», «follow-up»,
a joke, looking up an episode number).

After the interlocutor’s probe, the next explanation of that talk
or product goes back to the reporter.
Keep the interlocutor on the question.
Do not keep them through the answer.

A paragraph that continues the same talk list stays with the reporter.
«Anyway, возвращаемся к [my event]» reclaims the reporter floor.
A paragraph that only probes that report is the other host.

Topic-change as “likely the other host” is weaker here:
the reporter often moves to the next talk themselves.

### Attendance

«Я посетил», «мне показался доклад», «я сходил на воркшоп» pins the reporter.
«Я не был на той конференции, про которой ты рассказываешь» pins the other host.
That other host may then take a long turn if they saw the same project elsewhere
(«но на DappCon Circles тоже»).
That report stays with them.
Do not hand it back to the host whose conference is on the table.

### Disagreement and ping-pong

«У меня вайбы не совпали с тем, что ты описываешь» is the other host answering a take.
A concrete counterexample interrupting an argument is the other host.

Rapid fact-check turns already split as alternating blocks stay alternating
in structure.
Whisper often inverts the whole run (off by one).
Repair from the unfinished sentence and from who owns the thread,
not each line in isolation.

## Typical phrases

Counts from reviewed transcripts (episodes 200, 201, 203, 211, 219–223).
Евгений Марченко has no readable corpus yet.

### Александр Селезнев

Strong: «ощущение, что» / «у меня ощущение» / «у меня лично ощущение»;
«я верно понимаю» / «верно ли я понимаю» (his check-question);
«чуть ли не».

Useful: «давай поговорим» / «давай вернёмся» / «давай сейчас»;
«прикольно», «любопытно», «знаешь» as address;
«вопрос от слушателя»;
closing frame «подписывайтесь», «всем пока», «в эфире».

### Сергей Тихомиров

Strong: block opener «Правильно ли я понимаю» / «Правильно ли я понял»;
«follow-up» / «follow-up вопрос» / «у меня есть follow-up»;
«скажем так», «строго говоря», «в числе прочего»;
«выясняется, что»;
«мне показалось интересным»;
«хотелось бы понять» / «хотелось бы обсудить».

Useful: «на практике», «не совсем», «собственно»;
«окей» as a turn-start;
«наивный вопрос», «поправь, если неправильно понял»;
«своими словами переформулируй»;
«передаю микрофон».

### Иван Иваницкий

Strong: «учитывая»;
«если я правильно понимаю» / «проинтерпретировал» /
«удалось поместить это знание в контекст» (restate, then ask);
a question built on «ты упомянул»;
«забавно, что» / «меня забавляет»;
«со своей стороны».

Useful: «а можешь дать немного бэкграунда»;
«а в чём необходимость»;
«у меня возник вопрос» / «в связи с этим у меня возник вопрос»;
«я задумался»;
«честно говоря»;
«подожди, я понял».

A block that opens «Правильно ли я понял» is Сергей.
A block that opens «Я верно понимаю» or «У меня ощущение» is Александр.
A restating «Если я правильно понимаю» is Иван.
During the other host’s recap, «правильно ли я понимаю» is the interlocutor
(usually Сергей), not Ивана restating.
Quoting the guest with «Ты сказал, что» is a shared interview move.

## Keep or retag

Retag when a vocative, a floor pass, a unique first-person fact,
the opening attendance map, or a clarification of the last answer
contradicts the current label.
In host-only, also retag when the intro names a cohost without «я»,
when a probe/answer pair is inverted,
or when a ping-pong run is off by one.

A strong phrase hit plus a true clarification may retag.
A strong phrase hit alone may retag when it opens the block
(«Правильно ли я понял», «Я верно понимаю», «У меня ощущение»).
A useful phrase alone does not.
Same-subject adjacency after a finished guest answer does not retag
a second-host label back to the running host.

## After editing

Check:

- Block count unchanged
- Timestamps unchanged and still in file order
- Only host `Name:` fields changed
- Every new name is a full Cyrillic roster name for this episode

Then list in chat, for the whole range:

- Numbers with no transcript
- Numbers with a readable (already checked, skipped)
- For each episode that was retagged or inspected: format (host-only or hosts+guest), host set, each retag `(HH:MM:SS)` old name → new name and one-line reason, timestamps left as-is where a cue was weak or mixed
- Single-host episodes inspected and left unchanged

If every number was flagged or nothing changed, say so and stop.

## Constraints

- DO change only host speaker labels on `NNN-transcript.md`
- DO keep guest labels, timestamps, and spoken text
- DO use people-file Cyrillic full names
- DO flag missing transcripts and existing readables before any retag
- DO skip flagged episodes and continue through the rest of the range
- DO stop after the range pass and the chat summary
- DO NOT merge, split, or rewrite blocks
- DO NOT edit `NNN-readable.md` or SRT
- DO NOT even-distribute turns because one host’s labeled share is small
- DO NOT pull a second-host label back to the running host on related-subject stickiness or guest-directed «ты сказал»
- DO NOT apply the interview ask/answer split in host-only
- DO NOT mark a new `[неясно]` in place of a name; keep the current label when unsure

## Usage

1. Name the episode range (e.g. `201–218`).
2. Run this skill.
3. Review the flag list and the retags before `transcript-to-readable`.
