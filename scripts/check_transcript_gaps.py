#!/usr/bin/env python3
"""
Flag transcript places that need a listen against the audio.

Reads NNN-transcript.md. Reports unlabeled speaker lines, two blocks
that share a start second, a timestamp that jumps backward, and a
block whose word count is sparse for the seconds until the next start.

Also reads sibling NNN-episode.yml. Reports episode-status when
status is readable-reviewed or ready, so transcript-to-readable
leaves NNN-readable.md unchanged.

Span is next-block start minus this start. The last block has no next
start and is skipped for the sparse check.

Constants frozen from transcripts that already had NNN-readable.md
(200, 203, 211, 219, 220, 221, 223). On that set, no positive span
of 12s or more fell under 0.4 words per second. A one-word line over
17s (202, 00:27:55) is below that floor and is flagged.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from transcript_io import format_timestamp, timestamp_to_seconds

MIN_SPAN_SECONDS = 12
MIN_WORDS_PER_SECOND = 0.4
BLOCKING_EPISODE_STATUSES = frozenset({"readable-reviewed", "ready"})

EPISODE_RANGE_RE = re.compile(r"^(\d+)\s*-\s*(\d+)$")
TRANSCRIPT_NAME_RE = re.compile(r"^(\d+)-transcript\.md$")
STATUS_LINE_RE = re.compile(
    r"^status:\s*[\"']?([A-Za-z0-9_-]+)[\"']?\s*(?:#.*)?$"
)
TIME_LINE_RE = re.compile(r"^\((\d{2}):(\d{2}):(\d{2})\)\s*(.*)$")
LABELED_RE = re.compile(r"^([^:]+):\s*(.*)$")


@dataclass(frozen=True)
class Line:
    line_no: int
    seconds: int
    speaker: str
    text: str
    labeled: bool


@dataclass(frozen=True)
class Flag:
    seconds: int
    line_no: int
    kind: str
    detail: str


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def word_count(text: str) -> int:
    return len(text.split())


def episode_yaml_path(transcript: Path) -> Path | None:
    match = TRANSCRIPT_NAME_RE.match(transcript.name)
    if not match:
        return None
    return transcript.parent / f"{match.group(1)}-episode.yml"


def episode_status_flag(transcript: Path) -> Flag | None:
    yml = episode_yaml_path(transcript)
    if yml is None or not yml.is_file():
        return None
    status = None
    status_line_no = 0
    for line_no, raw in enumerate(yml.read_text(encoding="utf-8").splitlines(), 1):
        match = STATUS_LINE_RE.match(raw.strip())
        if match:
            status = match.group(1)
            status_line_no = line_no
            break
    if status not in BLOCKING_EPISODE_STATUSES:
        return None
    return Flag(
        seconds=0,
        line_no=status_line_no,
        kind="episode-status",
        detail=f"status {status}; leave readable unchanged",
    )


def parse_lines(path: Path) -> list[Line]:
    lines: list[Line] = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = raw.strip()
        if not stripped:
            continue
        match = TIME_LINE_RE.match(stripped)
        if not match:
            continue
        seconds = timestamp_to_seconds(
            int(match.group(1)), int(match.group(2)), int(match.group(3))
        )
        rest = match.group(4)
        labeled_match = LABELED_RE.match(rest)
        if labeled_match:
            speaker = labeled_match.group(1).strip()
            text = labeled_match.group(2)
            labeled = bool(speaker)
        else:
            speaker = ""
            text = rest
            labeled = False
        lines.append(
            Line(
                line_no=line_no,
                seconds=seconds,
                speaker=speaker,
                text=text,
                labeled=labeled,
            )
        )
    return lines


def check_lines(lines: list[Line]) -> list[Flag]:
    flags: list[Flag] = []
    for index, line in enumerate(lines):
        if not line.labeled:
            flags.append(
                Flag(
                    seconds=line.seconds,
                    line_no=line.line_no,
                    kind="unlabeled",
                    detail="no speaker name before the text",
                )
            )
        if index + 1 >= len(lines):
            continue
        nxt = lines[index + 1]
        span = nxt.seconds - line.seconds
        if span == 0:
            who = nxt.speaker or "unlabeled"
            flags.append(
                Flag(
                    seconds=line.seconds,
                    line_no=line.line_no,
                    kind="duplicate-timestamp",
                    detail=f"same start as next block ({who}, L{nxt.line_no})",
                )
            )
            continue
        if span < 0:
            flags.append(
                Flag(
                    seconds=line.seconds,
                    line_no=line.line_no,
                    kind="time-order",
                    detail=(
                        f"next block starts earlier "
                        f"({format_timestamp(nxt.seconds)}, L{nxt.line_no})"
                    ),
                )
            )
            continue
        words = word_count(line.text)
        rate = words / span
        if span >= MIN_SPAN_SECONDS and rate < MIN_WORDS_PER_SECOND:
            flags.append(
                Flag(
                    seconds=line.seconds,
                    line_no=line.line_no,
                    kind="sparse",
                    detail=(
                        f"{span}s {words} words {rate:.2f} w/s "
                        f"(floor {MIN_WORDS_PER_SECOND} w/s over "
                        f"{MIN_SPAN_SECONDS}s)"
                    ),
                )
            )
    flags.sort(key=lambda flag: (flag.seconds, flag.line_no, flag.kind))
    return flags


def expand_target_specs(specs: list[str]) -> list[str]:
    expanded: list[str] = []
    for spec in specs:
        stripped = spec.strip()
        match = EPISODE_RANGE_RE.match(stripped)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            if start > end:
                raise ValueError(f"episode range start > end: {stripped}")
            expanded.extend(str(number) for number in range(start, end + 1))
            continue
        expanded.append(stripped)
    return expanded


def resolve_transcript(root: Path, spec: str) -> Path:
    path = Path(spec)
    if path.is_file():
        return path
    if spec.isdigit():
        number = int(spec)
        candidate = (
            root / "content" / "episodes" / f"{number}" / f"{number}-transcript.md"
        )
        if candidate.is_file():
            return candidate
        raise FileNotFoundError(f"no transcript for episode {number}: {candidate}")
    raise FileNotFoundError(f"not a file or episode number: {spec}")


def print_report(path: Path, flags: list[Flag]) -> None:
    print(path)
    if not flags:
        print("  clean")
        return
    for flag in flags:
        if flag.kind == "episode-status":
            print(f"  {flag.kind:22} {flag.detail}")
            continue
        print(
            f"  {flag.kind:22} {format_timestamp(flag.seconds)}  "
            f"L{flag.line_no:<5} {flag.detail}"
        )
    print(f"  {len(flags)} check(s)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "targets",
        nargs="+",
        help=(
            "episode number (201), inclusive range (200-223), "
            "or path to NNN-transcript.md"
        ),
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="repository root (default: parent of scripts/)",
    )
    args = parser.parse_args()
    root = args.root.resolve() if args.root else repo_root()

    try:
        target_specs = expand_target_specs(args.targets)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    any_flags = False
    status = 0
    for spec in target_specs:
        try:
            path = resolve_transcript(root, spec)
        except FileNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            status = 2
            continue
        flags: list[Flag] = []
        status_flag = episode_status_flag(path)
        if status_flag:
            flags.append(status_flag)
        flags.extend(check_lines(parse_lines(path)))
        print_report(path, flags)
        if flags:
            any_flags = True
    if status == 2:
        return 2
    return 1 if any_flags else 0


if __name__ == "__main__":
    raise SystemExit(main())
