#!/usr/bin/env python3
"""Expand speaker-slot initials and fill empty or duplicate timestamps in NNN-transcript.md."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


BLOCK_RE = re.compile(
    r"^(\((?:(\d{2}):(\d{2}):(\d{2}))?\))\s+([^:]+):\s*(.*)$"
)
LATIN_CODE_RE = re.compile(r"^[A-Za-z]{1,4}$")
CYR_CODE_RE = re.compile(r"^[А-ЯЁа-яё]{1,4}$")

DEFAULT_WORDS_PER_SECOND = 2.0

CYR_TO_LAT_FIRST = {
    "А": "A",
    "Б": "B",
    "В": "V",
    "Г": "G",
    "Д": "D",
    "Е": "E",
    "Ё": "E",
    "Ж": "Z",
    "З": "Z",
    "И": "I",
    "Й": "Y",
    "К": "K",
    "Л": "L",
    "М": "M",
    "Н": "N",
    "О": "O",
    "П": "P",
    "Р": "R",
    "С": "S",
    "Т": "T",
    "У": "U",
    "Ф": "F",
    "Х": "H",
    "Ц": "C",
    "Ч": "C",
    "Ш": "S",
    "Щ": "S",
    "Ы": "Y",
    "Э": "E",
    "Ю": "Y",
    "Я": "Y",
}


@dataclass
class Block:
    line_no: int
    raw: str
    seconds: int | None
    speaker: str
    text: str
    stamp_token: str


@dataclass
class AskItem:
    kind: str
    label: str
    lines: list[int]
    candidates: list[str] = field(default_factory=list)


@dataclass
class Plan:
    name_expansions: list[dict]
    timestamps: list[dict]
    ask: list[AskItem]
    flags: list[str]


def find_repo_root() -> Path:
    starts = [Path.cwd(), Path(__file__).resolve().parent]
    for start in starts:
        for path in [start, *start.parents]:
            if (path / "content" / "episodes").is_dir():
                return path
    return Path.cwd()


def timestamp_to_seconds(h: int, m: int, s: int) -> int:
    return h * 3600 + m * 60 + s


def format_timestamp(seconds: int) -> str:
    if seconds < 0:
        seconds = 0
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def round_seconds(value: float) -> int:
    if value < 0:
        return 0
    return int(value + 0.5)


def word_count(text: str) -> int:
    n = len(text.split())
    return n if n > 0 else 1


def first_latin_letter(word: str) -> str:
    if not word:
        return ""
    ch = word[0].upper()
    if "A" <= ch <= "Z":
        return ch
    return CYR_TO_LAT_FIRST.get(ch, ch)


def name_codes(full_name: str) -> tuple[str, str]:
    words = full_name.split()
    latin = "".join(first_latin_letter(w) for w in words)
    cyr = "".join(w[0].upper() for w in words if w)
    return latin, cyr


def is_letter_code(speaker: str) -> bool:
    return bool(LATIN_CODE_RE.fullmatch(speaker) or CYR_CODE_RE.fullmatch(speaker))


def is_full_name(speaker: str) -> bool:
    return " " in speaker.strip()


def split_frontmatter(lines: list[str]) -> int:
    """Return the 0-based index where the body starts, or 0 if no frontmatter."""
    if not lines or lines[0].strip() != "---":
        return 0
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return i + 1
    raise ValueError("Unclosed YAML frontmatter")


def parse_transcript(path: Path) -> tuple[list[str], list[Block]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    body_start = split_frontmatter(lines)
    blocks: list[Block] = []
    for idx in range(body_start, len(lines)):
        raw = lines[idx]
        line_no = idx + 1
        if not raw.strip():
            continue
        match = BLOCK_RE.match(raw)
        if not match:
            raise ValueError(
                f"Line {line_no}: expected '(HH:MM:SS) Speaker: text' or '() Speaker: text', "
                f"got: {raw[:80]!r}"
            )
        stamp_token = match.group(1)
        if match.group(2) is None:
            seconds = None
        else:
            seconds = timestamp_to_seconds(
                int(match.group(2)), int(match.group(3)), int(match.group(4))
            )
        speaker = match.group(5).strip()
        text = match.group(6)
        blocks.append(
            Block(
                line_no=line_no,
                raw=raw,
                seconds=seconds,
                speaker=speaker,
                text=text,
                stamp_token=stamp_token,
            )
        )
    return lines, blocks


def collect_full_names(blocks: list[Block]) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for block in blocks:
        if is_full_name(block.speaker) and block.speaker not in seen:
            seen.add(block.speaker)
            names.append(block.speaker)
    return names


def code_index(full_names: list[str]) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for name in full_names:
        latin, cyr = name_codes(name)
        for code in {latin.upper(), cyr.upper()}:
            if not code:
                continue
            index.setdefault(code, [])
            if name not in index[code]:
                index[code].append(name)
    return index


def plan_names(blocks: list[Block], full_names: list[str]) -> tuple[dict[int, str], list[AskItem]]:
    index = code_index(full_names)
    expansions: dict[int, str] = {}
    ask_map: dict[tuple[str, str], AskItem] = {}

    def add_ask(kind: str, label: str, line_no: int, candidates: list[str] | None = None) -> None:
        key = (kind, label)
        if key not in ask_map:
            ask_map[key] = AskItem(
                kind=kind,
                label=label,
                lines=[],
                candidates=list(candidates or []),
            )
        item = ask_map[key]
        if line_no not in item.lines:
            item.lines.append(line_no)

    full_set = set(full_names)
    for block in blocks:
        speaker = block.speaker
        if speaker in full_set:
            continue
        if is_full_name(speaker):
            continue
        if not is_letter_code(speaker):
            add_ask("other-temp", speaker, block.line_no)
            continue
        code = speaker.upper()
        matches = index.get(code, [])
        if len(matches) == 1:
            expansions[block.line_no] = matches[0]
        elif len(matches) > 1:
            add_ask("ambiguous", speaker, block.line_no, matches)
        else:
            add_ask("unknown", speaker, block.line_no)
    return expansions, list(ask_map.values())


def fill_needed(blocks: list[Block]) -> list[bool]:
    """True for empty () and for a timestamp equal to the last anchor time."""
    need: list[bool] = []
    last_known: int | None = None
    for block in blocks:
        if block.seconds is None:
            need.append(True)
            continue
        if last_known is not None and block.seconds == last_known:
            need.append(True)
            continue
        need.append(False)
        last_known = block.seconds
    return need


def anchor_indices(need: list[bool]) -> list[int]:
    return [i for i, fill in enumerate(need) if not fill]


def span_rate(blocks: list[Block], left: int, right: int) -> float | None:
    t0 = blocks[left].seconds
    t1 = blocks[right].seconds
    if t0 is None or t1 is None:
        return None
    span = t1 - t0
    if span <= 0:
        return None
    total = sum(word_count(blocks[i].text) for i in range(left, right))
    if total <= 0:
        return None
    return span / total


def interpolate_times(blocks: list[Block]) -> tuple[dict[int, int], list[str]]:
    proposed: dict[int, float] = {}
    flags: list[str] = []
    need = fill_needed(blocks)
    anchors = anchor_indices(need)
    if not anchors:
        flags.append("no known timestamps; cannot fill times")
        return {}, flags

    first_anchor = anchors[0]
    if first_anchor > 0:
        t_end = blocks[first_anchor].seconds or 0
        total = sum(word_count(blocks[i].text) for i in range(0, first_anchor))
        cum = 0
        for i in range(0, first_anchor):
            proposed[i] = t_end * (cum / total) if total else 0.0
            cum += word_count(blocks[i].text)

    for left, right in zip(anchors, anchors[1:]):
        t0 = blocks[left].seconds or 0
        t1 = blocks[right].seconds or 0
        span = t1 - t0
        occupiers = range(left, right)
        total = sum(word_count(blocks[i].text) for i in occupiers)
        cum = 0
        for i in occupiers:
            if need[i]:
                frac = (cum / total) if total else 0.0
                proposed[i] = t0 + span * frac
            cum += word_count(blocks[i].text)

    last_anchor = anchors[-1]
    if last_anchor < len(blocks) - 1:
        rate = None
        if len(anchors) >= 2:
            rate = span_rate(blocks, anchors[-2], anchors[-1])
        if rate is None:
            rate = 1.0 / DEFAULT_WORDS_PER_SECOND
            flags.append(
                f"end-of-file fill used default {DEFAULT_WORDS_PER_SECOND:g} words/s"
            )
        t_last = blocks[last_anchor].seconds or 0
        cum = 0
        for i in range(last_anchor, len(blocks)):
            if need[i]:
                proposed[i] = t_last + rate * cum
            cum += word_count(blocks[i].text)

    snapped: dict[int, int] = {}
    prev_sec: int | None = None
    for i, block in enumerate(blocks):
        next_anchor_sec: int | None = None
        remaining_fill = 0
        for j in range(i + 1, len(blocks)):
            if not need[j]:
                next_anchor_sec = blocks[j].seconds
                break
            remaining_fill += 1

        if not need[i]:
            prev_sec = block.seconds
            continue
        value = round_seconds(proposed.get(i, prev_sec or 0))
        if prev_sec is not None:
            value = max(value, prev_sec + 1)
        if next_anchor_sec is not None:
            max_allowed = next_anchor_sec - remaining_fill - 1
            if max_allowed > (prev_sec or -1):
                if value > max_allowed:
                    flags.append(
                        f"line {block.line_no}: clamped to {format_timestamp(max_allowed)}"
                    )
                    value = max_allowed
            elif value >= next_anchor_sec:
                flags.append(
                    f"line {block.line_no}: tight window, {format_timestamp(value)} "
                    f"meets next known {format_timestamp(next_anchor_sec)}"
                )
        snapped[block.line_no] = value
        prev_sec = value
    return snapped, flags


def build_plan(blocks: list[Block]) -> Plan:
    full_names = collect_full_names(blocks)
    expansions, ask = plan_names(blocks, full_names)
    name_rows = [
        {
            "line": line_no,
            "from": next(b.speaker for b in blocks if b.line_no == line_no),
            "to": new_name,
        }
        for line_no, new_name in sorted(expansions.items())
    ]
    times, flags = interpolate_times(blocks)
    time_rows = []
    for block in blocks:
        if block.line_no not in times:
            continue
        new_seconds = times[block.line_no]
        if block.seconds is not None and block.seconds == new_seconds:
            continue
        origin = "()" if block.seconds is None else f"({format_timestamp(block.seconds)})"
        time_rows.append(
            {
                "line": block.line_no,
                "from": origin,
                "to": f"({format_timestamp(new_seconds)})",
                "seconds": new_seconds,
            }
        )
    return Plan(
        name_expansions=name_rows,
        timestamps=time_rows,
        ask=ask,
        flags=flags,
    )


def apply_plan(lines: list[str], blocks: list[Block], plan: Plan) -> list[str]:
    names = {row["line"]: row["to"] for row in plan.name_expansions}
    stamps = {row["line"]: row["seconds"] for row in plan.timestamps}
    out = list(lines)
    for block in blocks:
        if block.line_no not in names and block.line_no not in stamps:
            continue
        new_speaker = names.get(block.line_no, block.speaker)
        if block.line_no in stamps:
            stamp = f"({format_timestamp(stamps[block.line_no])})"
        elif block.seconds is not None:
            stamp = f"({format_timestamp(block.seconds)})"
        else:
            stamp = "()"
        out[block.line_no - 1] = f"{stamp} {new_speaker}: {block.text}"
    return out


def format_report(path: Path, plan: Plan, status: str) -> str:
    parts = [
        f"File: {path}",
        f"Status: {status}",
        f"Name expansions: {len(plan.name_expansions)}",
        f"Timestamps filled or spread: {len(plan.timestamps)}",
    ]
    if plan.name_expansions:
        parts.append("Names:")
        for row in plan.name_expansions:
            parts.append(f"  L{row['line']}: {row['from']} -> {row['to']}")
    if plan.timestamps:
        parts.append("Timestamps:")
        for row in plan.timestamps:
            parts.append(f"  L{row['line']}: {row['from']} -> {row['to']}")
    if plan.ask:
        parts.append("Needs input (no write):")
        for item in plan.ask:
            extra = ""
            if item.candidates:
                extra = " candidates: " + ", ".join(item.candidates)
            lines = ", ".join(str(n) for n in item.lines)
            parts.append(f"  {item.kind}: {item.label} (lines {lines}){extra}")
    if plan.flags:
        parts.append("Flags:")
        for flag in plan.flags:
            parts.append(f"  {flag}")
    return "\n".join(parts)


def resolve_path(args: argparse.Namespace) -> Path:
    if args.path:
        return Path(args.path)
    if args.episode is None:
        raise SystemExit("Provide --episode NNN or --path PATH")
    nnn = str(int(args.episode))
    return find_repo_root() / "content" / "episodes" / nnn / f"{nnn}-transcript.md"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episode", type=int, help="Episode number NNN")
    parser.add_argument("--path", help="Path to NNN-transcript.md")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the plan without writing",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Also print a JSON plan on stdout after the text report",
    )
    args = parser.parse_args(argv)

    path = resolve_path(args)
    if not path.is_file():
        print(f"ERROR: missing transcript: {path}", file=sys.stderr)
        return 1

    try:
        lines, blocks = parse_transcript(path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if not blocks:
        print(f"ERROR: no transcript blocks in {path}", file=sys.stderr)
        return 1

    plan = build_plan(blocks)
    if plan.ask:
        status = "needs-input"
        print(format_report(path, plan, status))
        if args.json:
            print(
                json.dumps(
                    {
                        "status": status,
                        "ask": [item.__dict__ for item in plan.ask],
                        "name_expansions": plan.name_expansions,
                        "timestamps": [
                            {k: v for k, v in row.items() if k != "seconds"}
                            for row in plan.timestamps
                        ],
                        "flags": plan.flags,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        return 2

    status = "dry-run" if args.dry_run else "applied"
    if not plan.name_expansions and not plan.timestamps:
        status = "clean-noop"

    if not args.dry_run and status != "clean-noop":
        new_lines = apply_plan(lines, blocks, plan)
        text = "\n".join(new_lines)
        if path.read_text(encoding="utf-8").endswith("\n"):
            text += "\n"
        path.write_text(text, encoding="utf-8")

    print(format_report(path, plan, status))
    if args.json:
        print(
            json.dumps(
                {
                    "status": status,
                    "name_expansions": plan.name_expansions,
                    "timestamps": [
                        {k: v for k, v in row.items() if k != "seconds"}
                        for row in plan.timestamps
                    ],
                    "flags": plan.flags,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
