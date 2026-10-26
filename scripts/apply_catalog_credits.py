#!/usr/bin/env python3
"""Fill catalog episode credits from the title guesses in the review table.

Host lists stay empty unless every guessed name is a regular host and the title
names no organization. Companies are not written into the episode file.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EPISODES = ROOT / "content" / "episodes"
PEOPLE = ROOT / "content" / "people"
REVIEW = PEOPLE / "historical-review.csv"

DROPPED = {
    "и инфраструктура децентрализации",
    "базовый блок",
    "lightning на мейннете",
    "dag-консенсус",
    "nyt",
    "компания smartdec",
    "биткойн-фьючерсы",
    "parity",
}
ALIASES = {
    "тихомиров": "sergei-tikhomirov",
    "sergei tikhomirov": "sergei-tikhomirov",
    "марченко": "evgeny-marchenko",
    "иваницкий": "ivan-ivanitskiy",
}
REGULAR_HOSTS = {
    "sergei-tikhomirov",
    "alexander-seleznev",
    "ivan-ivanitskiy",
    "evgeny-marchenko",
}
TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "kh", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "shch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def norm(value: str) -> str:
    return re.sub(r"\s+", " ", value.casefold().replace("ё", "е")).strip()


def slug_for(name: str) -> str:
    alias = ALIASES.get(norm(name))
    if alias:
        return alias
    chars: list[str] = []
    for char in name.casefold():
        if char in TRANSLIT:
            chars.append(TRANSLIT[char])
        elif char.isascii() and char.isalnum():
            chars.append(char)
        elif char in {" ", "-"}:
            chars.append("-")
    slug = re.sub(r"-+", "-", "".join(chars)).strip("-")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise SystemExit(f"bad slug {slug!r} from {name!r}")
    return slug


REVIEW_HEADER = [
    "title",
    "guests",
    "guests status",
    "hosts",
    "hosts status",
]
SOURCE_NOTES = {
    "title names a person and an organization": "name-org",
    "title names a person": "unsure",
    "feat. credit": "feat",
    "title names no guest": "no guest in title",
    "name-org": "name-org",
    "unsure": "unsure",
    "feat": "feat",
    "no guest in title": "no guest in title",
}


def format_list(key: str, slugs: list[str]) -> str:
    if not slugs:
        return f"{key}: []"
    return "\n".join([f"{key}:", *[f"  - slug: {slug}" for slug in slugs]])


def load_rows() -> list[list[str]]:
    with REVIEW.open(encoding="utf-8-sig", newline="") as handle:
        lines = list(csv.reader(handle))
    if lines and ("guests" in lines[0] or "needs_review" in lines[0]):
        raise SystemExit(
            "content/people/historical-review.csv already records review status"
        )
    rows = []
    for parts in lines[1:]:
        while len(parts) < 5:
            parts.append("")
        folder, title, name, source, existing = parts[:5]
        notes = SOURCE_NOTES.get(source.strip(), source.strip())
        role = "guest" if name.strip() else ""
        rows.append([folder, title, name, role, existing, notes, ""])
    fixed: list[list[str]] = []
    for folder, title, name, role, existing, notes, decision in rows:
        if folder == "111" and name.startswith("Дебаты!"):
            name = "Кирилл Пименов"
            existing = "kirill-pimenov"
            notes = "name-org"
        if folder == "055" and notes == "no guest in title":
            for person in ("Владимир Заречнев", "Михаил Заикин", "Максим Стребков"):
                fixed.append([folder, title, person, "guest", "", "name-org", ""])
            continue
        fixed.append([folder, title, name, role, existing, notes, decision])
    return fixed


def review_sheet(rows: list[list[str]]) -> list[list[str]]:
    grouped: list[list[list[str]]] = []
    by_folder: dict[str, list[list[str]]] = {}
    for row in rows:
        group = by_folder.get(row[0])
        if group is None:
            group = []
            by_folder[row[0]] = group
            grouped.append(group)
        group.append(row)
    sheet: list[list[str]] = []
    for group in grouped:
        guests: list[str] = []
        hosts: list[str] = []
        for row in group:
            name = row[2].strip()
            decision = row[6].strip()
            if not name or decision == "drop" or not decision:
                continue
            if decision.startswith("host:"):
                hosts.append(name)
            else:
                guests.append(name)
        sheet.append([group[0][1], ", ".join(guests), "", ", ".join(hosts), ""])
    return sheet


def main() -> None:
    rows = load_rows()
    by_folder: dict[str, list[list[str]]] = {}
    for row in rows:
        by_folder.setdefault(row[0], []).append(row)

    people: dict[str, str] = {}
    episode_hosts: dict[str, list[str]] = {}
    episode_guests: dict[str, list[str]] = {}

    for folder, group in by_folder.items():
        kept: list[tuple[str, str, str]] = []
        for row in group:
            name = row[2].strip()
            if not name or norm(name) in DROPPED:
                row[6] = "drop" if name else ""
                continue
            slug = row[4].strip() or slug_for(name)
            row[4] = slug
            kept.append((name, slug, row[5].strip()))
            people.setdefault(slug, name)
        slugs = list(dict.fromkeys(slug for _name, slug, _notes in kept))
        named_org = any(notes == "name-org" for _name, _slug, notes in kept)
        as_hosts = bool(slugs) and not named_org and set(slugs) <= REGULAR_HOSTS
        if as_hosts:
            episode_hosts[folder] = slugs
            episode_guests[folder] = []
            mark = {slug: f"host:{slug}" for slug in slugs}
        else:
            episode_hosts[folder] = []
            episode_guests[folder] = slugs
            mark = {slug: slug for slug in slugs}
        for row in group:
            slug = row[4].strip()
            if row[6] == "drop" or not row[2].strip():
                continue
            row[6] = mark.get(slug, slug)

    created = 0
    for slug, name in sorted(people.items()):
        path = PEOPLE / f"{slug}.md"
        if path.exists():
            continue
        path.write_text(f"---\nslug: {slug}\nname: {name}\n---\n", encoding="utf-8")
        created += 1

    patched = 0
    for folder, hosts in episode_hosts.items():
        path = EPISODES / folder / f"{folder}-episode.yml"
        text = path.read_text(encoding="utf-8")
        block = format_list("hosts", hosts) + "\n" + format_list("guests", episode_guests[folder])
        updated, count = re.subn(r"hosts: \[\]\nguests: \[\]", block, text, count=1)
        if count != 1:
            raise SystemExit(f"{path}: credits block not found")
        path.write_text(updated, encoding="utf-8")
        patched += 1

    with REVIEW.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(REVIEW_HEADER)
        writer.writerows(review_sheet(rows))
    print(f"episodes {patched}")
    print(f"people mentioned {len(people)}")
    print(f"new person files {created}")


if __name__ == "__main__":
    main()
