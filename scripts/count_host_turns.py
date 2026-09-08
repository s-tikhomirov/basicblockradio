#!/usr/bin/env python3
"""
Count speaker paragraphs in episode readable or transcript files.

Host paragraphs are split into:
- questions: on-topic questions and discussion, including mixed
  paragraphs that greet and then state the episode topic
- asides: short remarks, clarifications, and follow-ups under
  MIN_QUESTION_WORDS that do not count as a question of their own
- show-frame: hello, goodbye, sponsor readings, subscribe, end thanks

Guest paragraphs are answers.

CSV columns: episode, total, show-frame, asides, questions, answers,
then each host's .questions and .share.

Formulas keep total = questions + answers, questions = sum of host
.questions, and shares adding to 1. Prefer NNN-readable.md;
otherwise NNN-transcript.md. Output is tab-separated so a paste
into Google Sheets turns = cells into live formulas.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Literal

import yaml

from transcript_io import BLOCK_RE

PREFERRED_HOST_SLUGS = (
    "alexander-seleznev",
    "sergei-tikhomirov",
    "ivan-ivanitskiy",
)

HostKind = Literal["questions", "asides", "show-frame"]
MIN_QUESTION_WORDS = 8
WORD_RE = re.compile(
    r"[A-Za-zА-Яа-яЁё0-9]+(?:['’-][A-Za-zА-Яа-яЁё0-9]+)?"
)

CYRILLIC_TRANSLIT = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "e",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "kh",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "shch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
}

INTERVIEW_PROMPT_RE = re.compile(
    r"\?|"
    r"расскажи|"
    r"можешь.{0,50}(?:описать|напомнить|рассказать)|"
    r"первый вопрос|"
    r"привычного вопроса|"
    r"перейд[её]м к (?:нашим )?вопрос|"
    r"перейд[её]м к (?:рассказу|основн|выпуск)",
    re.I,
)
EPISODE_TOPIC_RE = re.compile(
    r"сегодня мы (?:решили )?(?:поговорим|поговорить|обсудим|обсудить|"
    r"рассмотрим|рассмотреть|пригласили|разбер)|"
    r"в этом выпуске мы|"
    r"в ближайшие .{0,30}выпуск|"
    r"выпуск.{0,80}посвящ|"
    r"тема |"
    r"поговорим (?:про|о |и о)|"
    r"мы (?:сегодня )?(?:обсудим|поговорим|разберём|разберем)|"
    r"обсудим с |"
    r"не переключайтесь",
    re.I,
)
CANNED_SPONSOR_RE = re.compile(
    r"кор-разработчик блокчейна|"
    r"со-?разработчик блокчейна|"
    r"соразработчик блокчейна|"
    r"core-разработчик блокчейна|"
    r"enterprise-grade|"
    r"zerion api|"
    r"облачная платформа на (?:базе )?децентрализованной|"
    r"23 млн\w* пользователей|"
    r"1inch\.(?:io|dev|com)|"
    r"ведущий DeFi|"
    r"60%.{0,40}своп|"
    r"fastest blockchain",
    re.I,
)
SPONSOR_READING_RE = re.compile(
    r"наш.{0,25}спонсор|"
    r"нас .{0,40}поддержива|"
    r"благодар.{0,80}спонсор|"
    r"patreon|"
    r"boosty|"
    r"yoki finance|"
    r"кто поддерживает наш подкаст|"
    r"тех, кто (?:нас )?поддерживает",
    re.I,
)
HELLO_RE = re.compile(
    r"подкаст.{0,80}базов|"
    r"с вами.{0,40}подкаст|"
    r"у микрофона|"
    r"всем привет|"
    r"привет,?\s+друзья|"
    r"в гостях у нас|"
    r"у нас в гостях|"
    r"в гостях\s*[—–-]|"
    r"сегодняшн\w+ гост",
    re.I,
)
GREETING_RE = re.compile(r"привет|здравствуй", re.I)
GOODBYE_RE = re.compile(
    r"всем пока|"
    r"до встречи|"
    r"до скорых|"
    r"до следующего|"
    r"на этом мы заверш|"
    r"на этом .{0,30}заверш|"
    r"завершая (?:эту |этот |наш )|"
    r"завершаем (?:первую |эту |сегодняшн|наш )|"
    r"давайте завершать|"
    r"на н[её]м заканчиваем|"
    r"мы заканчиваем|"
    r"это был .{0,60}базов|"
    r"хорошего (?:всем )?(?:лета|сезона|дня)|"
    r"всего доброго",
    re.I,
)
SUBSCRIBE_RE = re.compile(
    r"подписывайтесь|"
    r"ставьте лайк|"
    r"пишите в (?:наш )?чат|"
    r"заходите в бб-чат",
    re.I,
)
END_THANKS_RE = re.compile(
    r"спасибо нашим (?:слушателям|патронам|спонсорам)|"
    r"спасибо.{0,80}(?:что (?:приш[её]л|зашёл|зашел|пришёл)|"
    r"патрон|спонсор|слушател)",
    re.I,
)


@dataclass(frozen=True)
class SpeakerBlock:
    seconds: int
    speaker: str
    text: str


@dataclass
class EpisodeCounts:
    number: int
    source: str
    questions: Counter[str] = field(default_factory=Counter)
    asides: Counter[str] = field(default_factory=Counter)
    show_frame: Counter[str] = field(default_factory=Counter)
    answers: int = 0


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def split_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    data = yaml.safe_load(text[4:end]) or {}
    return data if isinstance(data, dict) else {}


def load_people(people_dir: Path) -> tuple[dict[str, str], dict[str, str]]:
    """Return (slug_to_name, name_to_slug)."""
    slug_to_name: dict[str, str] = {}
    name_to_slug: dict[str, str] = {}
    if not people_dir.is_dir():
        return slug_to_name, name_to_slug
    for path in people_dir.glob("*.md"):
        data = split_frontmatter(path.read_text(encoding="utf-8"))
        slug = data.get("slug") or path.stem
        name = data.get("name")
        if isinstance(slug, str) and isinstance(name, str) and name.strip():
            slug_to_name[slug] = name.strip()
            name_to_slug[name.strip()] = slug
    return slug_to_name, name_to_slug


def slug_list(entries: Any) -> list[str]:
    slugs: list[str] = []
    if not entries:
        return slugs
    for entry in entries:
        if isinstance(entry, str):
            slugs.append(entry)
        elif isinstance(entry, dict) and isinstance(entry.get("slug"), str):
            slugs.append(entry["slug"])
    return slugs


def slugify_name(name: str) -> str:
    parts: list[str] = []
    for ch in name.lower():
        if ch in CYRILLIC_TRANSLIT:
            parts.append(CYRILLIC_TRANSLIT[ch])
        elif ch.isalnum():
            parts.append(ch)
        elif ch in " -_":
            parts.append("-")
    slug = re.sub(r"-{2,}", "-", "".join(parts)).strip("-")
    return slug or "unknown"


def resolve_source(episode_dir: Path, number: int) -> tuple[Path | None, str]:
    readable = episode_dir / f"{number}-readable.md"
    transcript = episode_dir / f"{number}-transcript.md"
    if readable.is_file():
        return readable, "readable"
    if transcript.is_file():
        return transcript, "transcript"
    return None, "missing"


def load_blocks(path: Path) -> list[SpeakerBlock]:
    blocks: list[SpeakerBlock] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = BLOCK_RE.match(line)
        if not match:
            continue
        h, m, s = int(match.group(1)), int(match.group(2)), int(match.group(3))
        blocks.append(
            SpeakerBlock(
                seconds=h * 3600 + m * 60 + s,
                speaker=match.group(4).strip(),
                text=match.group(5),
            )
        )
    return blocks


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def is_short_greeting(text: str) -> bool:
    stripped = text.strip()
    return len(stripped) <= 160 and bool(GREETING_RE.search(stripped))


def is_on_topic(text: str) -> bool:
    return bool(INTERVIEW_PROMPT_RE.search(text) or EPISODE_TOPIC_RE.search(text))


def is_canned_sponsor(text: str) -> bool:
    return bool(CANNED_SPONSOR_RE.search(text))


def is_show_frame(text: str) -> bool:
    if SPONSOR_READING_RE.search(text) or is_canned_sponsor(text):
        return True
    if is_short_greeting(text) or HELLO_RE.search(text):
        return True
    return bool(
        SUBSCRIBE_RE.search(text)
        or GOODBYE_RE.search(text)
        or END_THANKS_RE.search(text)
    )


def classify_host_text(text: str) -> HostKind:
    if is_canned_sponsor(text):
        return "show-frame"
    if is_on_topic(text):
        if word_count(text) < MIN_QUESTION_WORDS:
            return "asides"
        return "questions"
    if is_show_frame(text):
        return "show-frame"
    if word_count(text) < MIN_QUESTION_WORDS:
        return "asides"
    return "questions"


def classify_host_blocks(
    blocks: list[SpeakerBlock],
    host_names: set[str],
) -> list[HostKind | None]:
    """Return questions/asides/show-frame for host blocks, None for guests."""
    kinds: list[HostKind | None] = []
    for block in blocks:
        if block.speaker not in host_names:
            kinds.append(None)
        else:
            kinds.append(classify_host_text(block.text))
    return kinds


def speaker_slug(name: str, name_to_slug: dict[str, str]) -> str:
    if name in name_to_slug:
        return name_to_slug[name]
    return slugify_name(name)


def episode_meta(episode_dir: Path, number: int) -> dict[str, Any]:
    yml = episode_dir / f"{number}-episode.yml"
    if not yml.is_file():
        return {}
    loaded = load_yaml(yml) or {}
    return loaded if isinstance(loaded, dict) else {}


def host_slugs_for_episode(
    meta: dict[str, Any],
    roster: Iterable[str],
) -> set[str]:
    hosts = set(roster)
    hosts.update(slug_list(meta.get("hosts")))
    return hosts


def count_episode(
    number: int,
    episode_dir: Path,
    name_to_slug: dict[str, str],
    slug_to_name: dict[str, str],
    roster: tuple[str, ...],
) -> EpisodeCounts | None:
    source_path, source = resolve_source(episode_dir, number)
    if source_path is None:
        return EpisodeCounts(number=number, source=source)
    blocks = load_blocks(source_path)
    meta = episode_meta(episode_dir, number)
    host_slug_set = host_slugs_for_episode(meta, roster)
    host_names = {slug_to_name[s] for s in host_slug_set if s in slug_to_name}
    kinds = classify_host_blocks(blocks, host_names)
    counts = EpisodeCounts(number=number, source=source)
    for block, kind in zip(blocks, kinds):
        if kind is None:
            counts.answers += 1
            continue
        slug = speaker_slug(block.speaker, name_to_slug)
        if kind == "show-frame":
            counts.show_frame[slug] += 1
        elif kind == "asides":
            counts.asides[slug] += 1
        else:
            counts.questions[slug] += 1
    return counts


def collect_host_slugs(
    rows: list[EpisodeCounts],
    roster: tuple[str, ...],
) -> list[str]:
    host_slugs: list[str] = []
    seen: set[str] = set()
    for slug in roster:
        if slug not in seen:
            host_slugs.append(slug)
            seen.add(slug)
    extra: set[str] = set()
    for row in rows:
        extra.update(row.questions.keys())
        extra.update(row.asides.keys())
        extra.update(row.show_frame.keys())
    for slug in sorted(extra - seen):
        host_slugs.append(slug)
    return host_slugs


def col_letter(index: int) -> str:
    """1-based spreadsheet column index to letter (1=A)."""
    letters = ""
    n = index
    while n > 0:
        n, rem = divmod(n - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def range_sum(first_col: int, last_col: int, row: int) -> str:
    return f"${col_letter(first_col)}{row}:${col_letter(last_col)}{row}"


def csv_headers(host_slugs: list[str]) -> list[str]:
    headers = ["episode", "total", "show-frame", "asides", "questions", "answers"]
    headers.extend(f"{slug}.questions" for slug in host_slugs)
    headers.extend(f"{slug}.share" for slug in host_slugs)
    return headers


def write_csv(
    path: Path,
    rows: list[EpisodeCounts],
    host_slugs: list[str],
) -> None:
    n_hosts = len(host_slugs)
    first_data = 2
    last_data = 1 + len(rows)
    total_row = last_data + 1
    q_col = 5
    a_col = 6
    first_q = 7
    last_q = 6 + n_hosts
    headers = csv_headers(host_slugs)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(headers)
        for offset, row in enumerate(rows):
            sheet_row = first_data + offset
            q_sum = range_sum(first_q, last_q, sheet_row)
            cells: list[str] = [
                str(row.number),
                f"={col_letter(q_col)}{sheet_row}+{col_letter(a_col)}{sheet_row}",
                str(sum(row.show_frame.values())),
                str(sum(row.asides.values())),
                f"=SUM({q_sum})",
                str(row.answers),
            ]
            for slug in host_slugs:
                cells.append(str(row.questions.get(slug, 0)))
            for i in range(n_hosts):
                hq = col_letter(first_q + i)
                cells.append(f"={hq}{sheet_row}/{col_letter(q_col)}{sheet_row}")
            writer.writerow(cells)
        q_letter = col_letter(q_col)
        a_letter = col_letter(a_col)
        q_sum_total = range_sum(first_q, last_q, total_row)
        total_cells = [
            "total",
            f"={q_letter}{total_row}+{a_letter}{total_row}",
            f"=SUM({col_letter(3)}{first_data}:{col_letter(3)}{last_data})",
            f"=SUM({col_letter(4)}{first_data}:{col_letter(4)}{last_data})",
            f"=SUM({q_sum_total})",
            f"=SUM({a_letter}{first_data}:{a_letter}{last_data})",
        ]
        for i in range(n_hosts):
            hq = col_letter(first_q + i)
            total_cells.append(f"=SUM({hq}{first_data}:{hq}{last_data})")
        for i in range(n_hosts):
            hq = col_letter(first_q + i)
            total_cells.append(
                f"=ROUND({hq}{total_row}/{q_letter}{total_row};2)"
            )
        writer.writerow(total_cells)


def dump_classification(
    number: int,
    episode_dir: Path,
    name_to_slug: dict[str, str],
    slug_to_name: dict[str, str],
    roster: tuple[str, ...],
) -> None:
    source_path, source = resolve_source(episode_dir, number)
    if source_path is None:
        print(f"{number}: missing", file=sys.stderr)
        return
    blocks = load_blocks(source_path)
    meta = episode_meta(episode_dir, number)
    host_slug_set = host_slugs_for_episode(meta, roster)
    host_names = {slug_to_name[s] for s in host_slug_set if s in slug_to_name}
    kinds = classify_host_blocks(blocks, host_names)
    print(f"# {number} {source} {source_path.name}", file=sys.stderr)
    for block, kind in zip(blocks, kinds):
        slug = speaker_slug(block.speaker, name_to_slug)
        label = kind or "guest"
        preview = re.sub(r"\s+", " ", block.text)[:90]
        h, rem = divmod(block.seconds, 3600)
        m, s = divmod(rem, 60)
        print(
            f"{h:02d}:{m:02d}:{s:02d} {label:10} {slug}: {preview}",
            file=sys.stderr,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="output path (tab-separated, for pasting into Google Sheets)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="repository root (default: parent of scripts/)",
    )
    parser.add_argument(
        "--debug",
        type=int,
        metavar="EPISODE",
        help="print paragraph classification for one episode to stderr",
    )
    args = parser.parse_args()
    if args.end < args.start:
        print("error: --end must be >= --start", file=sys.stderr)
        return 1
    root = args.root.resolve() if args.root else repo_root()
    slug_to_name, name_to_slug = load_people(root / "content" / "people")
    episodes_dir = root / "content" / "episodes"
    missing: list[int] = []
    rows: list[EpisodeCounts] = []
    for number in range(args.start, args.end + 1):
        episode_dir = episodes_dir / str(number)
        counted = count_episode(
            number,
            episode_dir,
            name_to_slug,
            slug_to_name,
            PREFERRED_HOST_SLUGS,
        )
        if counted is None or counted.source == "missing":
            missing.append(number)
            if counted is not None:
                rows.append(counted)
            continue
        rows.append(counted)
    host_slugs = collect_host_slugs(rows, PREFERRED_HOST_SLUGS)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_csv(args.output, rows, host_slugs)
    if args.debug is not None:
        dump_classification(
            args.debug,
            episodes_dir / str(args.debug),
            name_to_slug,
            slug_to_name,
            PREFERRED_HOST_SLUGS,
        )
    if missing:
        print(
            "missing processed transcripts: "
            + ", ".join(str(n) for n in missing),
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
