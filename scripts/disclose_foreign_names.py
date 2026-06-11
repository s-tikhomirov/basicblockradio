#!/usr/bin/env python3
"""
Insert canonical English names after the first Russian mention of each foreign
person in NNN-readable.md (one parenthetical per person per episode).

Does not change block count, timestamps, or speakers — only appends
` (English Name)` after the matched Russian name span.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from transcript_io import Block, blocks_to_body, format_timestamp, load_document

# Masculine / default foreign name case endings (optional suffix after stem).
CASE_SUFFIX = r"(?:а|у|ом|е)?"


@dataclass(frozen=True)
class ForeignPerson:
    id: str
    english: str
    given: str
    family: str
    family_indeclinable: bool

    def match_pattern(self) -> re.Pattern[str]:
        g = re.escape(self.given) + CASE_SUFFIX
        if self.family_indeclinable:
            f = re.escape(self.family)
        else:
            f = re.escape(self.family) + CASE_SUFFIX
        return re.compile(rf"{g}\s+{f}")


def default_family_indeclinable(family: str) -> bool:
    if not family:
        return True
    last = family[-1].lower()
    return last in "еиоуыэюя"


def load_persons(path: Path) -> list[ForeignPerson]:
    data = json.loads(path.read_text(encoding="utf-8"))
    persons: list[ForeignPerson] = []
    for raw in data.get("persons", []):
        family = raw["family"]
        indecl = raw.get("family_indeclinable")
        if indecl is None:
            indecl = default_family_indeclinable(family)
        persons.append(
            ForeignPerson(
                id=raw["id"],
                english=raw["english"],
                given=raw["given"],
                family=family,
                family_indeclinable=bool(indecl),
            )
        )
    return persons


def person_already_disclosed_in_text(text: str, english: str) -> bool:
    return f"({english})" in text


def disclose_in_text(
    text: str,
    persons: list[ForeignPerson],
    disclosed: set[str],
) -> tuple[str, list[str]]:
    """Return updated text and list of person ids newly disclosed on this line."""
    new_ids: list[str] = []
    matches: list[tuple[int, int, ForeignPerson]] = []

    for person in persons:
        if person.id in disclosed:
            continue
        if person_already_disclosed_in_text(text, person.english):
            disclosed.add(person.id)
            continue
        for m in person.match_pattern().finditer(text):
            end = m.end()
            if text[end : end + 2] == " (" and person.english in text[end : end + 4 + len(person.english)]:
                disclosed.add(person.id)
                continue
            matches.append((m.start(), m.end(), person))
            break

    if not matches:
        return text, new_ids

    matches.sort(key=lambda x: x[0], reverse=True)
    for start, end, person in matches:
        if person.id in disclosed:
            continue
        text = text[:end] + f" ({person.english})" + text[end:]
        disclosed.add(person.id)
        new_ids.append(person.id)

    return text, new_ids


def disclose_document(
    blocks: list[Block],
    persons: list[ForeignPerson],
) -> tuple[list[Block], list[str]]:
    disclosed: set[str] = set()
    log: list[str] = []

    for person in persons:
        for block in blocks:
            if person_already_disclosed_in_text(block.text, person.english):
                disclosed.add(person.id)
                break

    updated: list[Block] = []
    for block in blocks:
        new_text, new_ids = disclose_in_text(block.text, persons, disclosed)
        for pid in new_ids:
            person = next(p for p in persons if p.id == pid)
            log.append(
                f"{person.english} → ({format_timestamp(block.seconds)})"
            )
        updated.append(
            Block(
                line_no=block.line_no,
                seconds=block.seconds,
                speaker=block.speaker,
                text=new_text,
            )
        )
    return updated, log


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Add first-mention (English) disclosures to NNN-readable.md"
    )
    parser.add_argument("readable", type=Path, help="Path to NNN-readable.md")
    parser.add_argument(
        "--persons",
        type=Path,
        help="foreign-persons.json (default: .agents/foreign-persons.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without writing the file",
    )
    args = parser.parse_args()

    repo = Path(__file__).resolve().parent.parent
    persons_path = args.persons or (repo / ".agents" / "foreign-persons.json")
    if not persons_path.is_file():
        print(f"error: persons file not found: {persons_path}", file=sys.stderr)
        return 1
    if not args.readable.is_file():
        print(f"error: readable not found: {args.readable}", file=sys.stderr)
        return 1

    persons = load_persons(persons_path)
    doc = load_document(path=args.readable)
    new_blocks, log = disclose_document(doc.blocks, persons)

    if args.dry_run:
        for entry in log:
            print(entry)
        if not log:
            print("(no new disclosures)")
        return 0

    body = blocks_to_body(new_blocks)
    out = doc.frontmatter
    if out and not out.endswith("\n"):
        out += "\n"
    out = out + "\n" + body if body else out + "\n"
    args.readable.write_text(out, encoding="utf-8")
    for entry in log:
        print(entry)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
