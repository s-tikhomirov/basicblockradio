"""Parse and serialize Basic Block Radio transcript/readable markdown (structure only)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, TextIO

BLOCK_RE = re.compile(
    r"^\((\d{2}):(\d{2}):(\d{2})\)\s+([^:]+):\s*(.*)$"
)


def timestamp_to_seconds(h: int, m: int, s: int) -> int:
    return h * 3600 + m * 60 + s


def parse_timestamp_from_match(m: re.Match[str]) -> int:
    return timestamp_to_seconds(int(m.group(1)), int(m.group(2)), int(m.group(3)))


def format_timestamp(seconds: int) -> str:
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


@dataclass(frozen=True)
class Block:
    line_no: int  # 1-based line number in source file
    seconds: int
    speaker: str
    text: str

    @property
    def line(self) -> str:
        return f"({format_timestamp(self.seconds)}) {self.speaker}: {self.text}"


@dataclass
class TranscriptDocument:
    frontmatter: str  # includes leading/trailing --- lines, or empty
    blocks: list[Block]

    @property
    def block_count(self) -> int:
        return len(self.blocks)

    @property
    def span_seconds(self) -> int:
        if not self.blocks:
            return 0
        return self.blocks[-1].seconds - self.blocks[0].seconds


def split_frontmatter(lines: list[str]) -> tuple[str, list[str]]:
    if not lines or lines[0].strip() != "---":
        return "", lines
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fm = "\n".join(lines[: i + 1])
            if i + 1 < len(lines) and lines[i + 1] == "":
                body = lines[i + 2 :]
            else:
                body = lines[i + 1 :]
            return fm, body
    return "", lines


def parse_body_lines(body_lines: Iterable[str], line_offset: int = 0) -> list[Block]:
    blocks: list[Block] = []
    for idx, raw in enumerate(body_lines, start=1):
        line_no = line_offset + idx
        line = raw.rstrip("\n")
        if not line.strip():
            continue
        m = BLOCK_RE.match(line)
        if not m:
            raise ValueError(
                f"Line {line_no}: expected '(HH:MM:SS) Speaker: text', got: {line[:80]!r}..."
            )
        speaker = m.group(4).strip()
        text = m.group(5)
        sec = parse_timestamp_from_match(m)
        blocks.append(
            Block(line_no=line_no, seconds=sec, speaker=speaker, text=text)
        )
    return blocks


def load_document(path: Path | None = None, stream: TextIO | None = None) -> TranscriptDocument:
    if path is not None:
        text = path.read_text(encoding="utf-8")
    elif stream is not None:
        text = stream.read()
    else:
        raise ValueError("path or stream required")
    lines = text.splitlines()
    frontmatter, body = split_frontmatter(lines)
    # line numbers in file: frontmatter lines + body
    fm_line_count = len(frontmatter.splitlines()) if frontmatter else 0
    body_start = fm_line_count + (1 if frontmatter and fm_line_count else 0)
    blocks: list[Block] = []
    for i, raw in enumerate(body):
        line_no = body_start + i + 1
        line = raw
        if not line.strip():
            continue
        m = BLOCK_RE.match(line)
        if not m:
            raise ValueError(
                f"Line {line_no}: expected '(HH:MM:SS) Speaker: text', got: {line[:80]!r}..."
            )
        speaker = m.group(4).strip()
        text_part = m.group(5)
        sec = parse_timestamp_from_match(m)
        blocks.append(
            Block(line_no=line_no, seconds=sec, speaker=speaker, text=text_part)
        )
    return TranscriptDocument(frontmatter=frontmatter, blocks=blocks)


def blocks_to_body(blocks: Iterable[Block]) -> str:
    parts = [b.line for b in blocks]
    return "\n\n".join(parts) + ("\n" if parts else "")


def write_chunk_body(path: Path, blocks: Iterable[Block]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(blocks_to_body(blocks), encoding="utf-8")
