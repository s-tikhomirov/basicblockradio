#!/usr/bin/env python3
"""Deterministic content-model checker for Basic Block Radio."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

import yaml

PERSON_LINK_KEYS = frozenset({"website", "x", "github", "telegram", "linkedin"})
EPISODE_TOP_KEYS = frozenset(
    {
        "episode",
        "title",
        "status",
        "recording_date",
        "publish_date",
        "hosts",
        "guests",
        "url",
        "youtube_url",
        "variant",
        "libsyn_item_id",
        "audio_url",
        "audio_bytes",
    }
)
STATUS_VALUES = frozenset(
    {
        "draft",
        "transcript-reviewed",
        "readable-reviewed",
        "ready",
        "catalog",
    }
)
PUBLIC_STATUSES = frozenset({"ready", "catalog"})
FOLDER_RE = re.compile(r"^(\d{3,})([a-z])?$")
ARTIFACT_SUFFIXES = (
    "episode.yml",
    "shownotes.md",
    "transcript.md",
    "transcript-no-timestamps.md",
    "timestamps-source.md",
    "readable.md",
    "shorts.md",
    "raw.srt",
    "raw-undiaried.srt",
    "raw-diarized.txt",
)
EXTRA_EPISODE_FILES = frozenset({"STRUCTURE.md", "README.md"})
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL_RE = re.compile(r"^https?://\S+$")


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_yaml(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def split_frontmatter(text: str) -> tuple[dict[str, Any] | None, str, list[str]]:
    """Return (data, body, errors). data is None if frontmatter is missing/invalid."""
    errors: list[str] = []
    if not text.startswith("---\n") and text != "---":
        return None, text, ["missing YAML frontmatter"]
    end = text.find("\n---\n", 4)
    if end == -1:
        if text.endswith("\n---"):
            raw = text[4:-4]
            body = ""
        else:
            return None, text, ["unterminated YAML frontmatter"]
    else:
        raw = text[4:end]
        body = text[end + 5 :]
    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        return None, text, [f"invalid YAML frontmatter: {exc}"]
    if not isinstance(data, dict):
        return None, body, ["frontmatter must be a mapping"]
    return data, body, errors


_SHOWNOTES_SECTION = re.compile(
    r"^## Shownotes line[ \t]*\n(.*?)(?=^## |\Z)",
    re.M | re.S,
)
_MD_LINK = re.compile(r"\[[^\]]*\]\((https?://[^)\s]+)\)")
LOGO_SUFFIXES = frozenset({".png", ".svg", ".webp", ".jpg", ".jpeg"})


def shownotes_link(body: str) -> str | None:
    match = _SHOWNOTES_SECTION.search(body)
    if not match:
        return None
    link = _MD_LINK.search(match.group(1))
    return link.group(1) if link else None


def parse_iso_date(value: str) -> date | None:
    if not ISO_DATE_RE.match(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


class Checker:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.content = root / "content"
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, path: Path, message: str) -> None:
        rel = path.relative_to(self.root) if path.is_relative_to(self.root) else path
        self.errors.append(f"{rel}: {message}")

    def warn(self, path: Path, message: str) -> None:
        rel = path.relative_to(self.root) if path.is_relative_to(self.root) else path
        self.warnings.append(f"{rel}: {message}")

    def run(self) -> int:
        if not self.content.is_dir():
            self.error(self.content, "missing content/ directory")
            return self.finish()

        people_slugs = self.check_people()
        org_slugs = self.check_organizations()
        self.check_sponsorships(org_slugs)
        self.check_episodes(people_slugs, org_slugs)
        return self.finish()

    def finish(self) -> int:
        for w in self.warnings:
            print(f"warning: {w}", file=sys.stderr)
        for e in self.errors:
            print(f"error: {e}", file=sys.stderr)
        print(
            f"{len(self.errors)} error(s), {len(self.warnings)} warning(s)",
            file=sys.stderr,
        )
        return 1 if self.errors else 0

    def check_people(self) -> set[str]:
        people_dir = self.content / "people"
        slugs: set[str] = set()
        if not people_dir.is_dir():
            self.error(people_dir, "missing directory")
            return slugs
        for path in sorted(people_dir.glob("*.md")):
            slug = path.stem
            if not SLUG_RE.match(slug):
                self.error(path, f"invalid slug filename {slug!r}")
                continue
            text = path.read_text(encoding="utf-8")
            data, _body, fm_errors = split_frontmatter(text)
            for err in fm_errors:
                self.error(path, err)
            if data is None:
                continue
            fm_slug = data.get("slug")
            if fm_slug != slug:
                self.error(path, f"frontmatter slug {fm_slug!r} != filename {slug!r}")
            if "name" not in data or not str(data.get("name", "")).strip():
                self.error(path, "frontmatter missing name")
            unknown = set(data) - {"slug", "name", "links"}
            if unknown:
                self.error(path, f"unknown frontmatter keys: {sorted(unknown)}")
            links = data.get("links")
            if links is not None:
                if not isinstance(links, dict):
                    self.error(path, "links must be a mapping")
                else:
                    bad = set(links) - PERSON_LINK_KEYS
                    if bad:
                        self.error(path, f"links unknown keys: {sorted(bad)}")
                    for key, url in links.items():
                        if key not in PERSON_LINK_KEYS:
                            continue
                        if not isinstance(url, str) or not URL_RE.match(url):
                            self.error(path, f"links.{key} must be an http(s) URL")
            slugs.add(slug)
        return slugs

    def check_organizations(self) -> set[str]:
        org_dir = self.content / "organizations"
        slugs: set[str] = set()
        if not org_dir.is_dir():
            self.error(org_dir, "missing directory")
            return slugs
        for path in sorted(org_dir.glob("*.yml")):
            slug = path.stem
            if not SLUG_RE.match(slug):
                self.error(path, f"invalid slug filename {slug!r}")
                continue
            try:
                data = load_yaml(path)
            except yaml.YAMLError as exc:
                self.error(path, f"invalid YAML: {exc}")
                continue
            if not isinstance(data, dict):
                self.error(path, "must be a mapping")
                continue
            if data.get("slug") != slug:
                self.error(path, f"slug {data.get('slug')!r} != filename {slug!r}")
            if "name" not in data or not str(data.get("name", "")).strip():
                self.error(path, "missing name")
            if "url" in data and data["url"] is not None:
                if not isinstance(data["url"], str) or not URL_RE.match(data["url"]):
                    self.error(path, f"invalid url: {data['url']!r}")
            unknown = set(data) - {"slug", "name", "url"}
            if unknown:
                self.error(path, f"unknown keys: {sorted(unknown)}")
            slugs.add(slug)
        return slugs

    def check_sponsorships(self, org_slugs: set[str]) -> None:
        sp_dir = self.content / "sponsorships"
        if not sp_dir.is_dir():
            self.error(sp_dir, "missing directory")
            return
        for path in sorted(sp_dir.glob("*.md")):
            if path.name == "sponsorship-template.md":
                continue
            text = path.read_text(encoding="utf-8")
            data, body, fm_errors = split_frontmatter(text)
            for err in fm_errors:
                self.error(path, err)
            if data is None:
                continue
            org = data.get("organization")
            first = data.get("first_episode")
            last = data.get("last_episode")
            unknown = set(data) - {
                "organization",
                "first_episode",
                "last_episode",
                "logo",
            }
            if unknown:
                self.error(path, f"unknown frontmatter keys: {sorted(unknown)}")
            if not isinstance(org, str) or not SLUG_RE.match(org):
                self.error(path, f"invalid organization: {org!r}")
            elif org not in org_slugs:
                self.error(path, f"unknown organization slug {org!r}")
            if not isinstance(first, int) or not isinstance(last, int):
                self.error(path, "first_episode and last_episode must be integers")
                continue
            if first > last:
                self.error(path, f"first_episode {first} > last_episode {last}")
            expected = f"{org}-{first}-{last}.md"
            if path.name != expected:
                self.error(path, f"filename should be {expected}")
            self.check_sponsorship_logo(path, sp_dir, data.get("logo"))
            if shownotes_link(body) is None:
                self.error(path, "Shownotes line needs one markdown link")

    def check_sponsorship_logo(self, path: Path, sp_dir: Path, logo: Any) -> None:
        if not isinstance(logo, str) or not logo.strip():
            self.error(path, "missing logo")
            return
        rel = Path(logo)
        if rel.is_absolute() or ".." in rel.parts or "\\" in logo:
            self.error(path, f"invalid logo path: {logo!r}")
            return
        logo_path = sp_dir / rel
        if not logo_path.is_file():
            self.error(path, f"missing logo file {logo}")
            return
        if logo_path.suffix.lower() not in LOGO_SUFFIXES:
            self.error(path, f"unsupported logo type {logo_path.suffix}")

    def check_episodes(self, people_slugs: set[str], org_slugs: set[str]) -> None:
        episodes_dir = self.content / "episodes"
        if not episodes_dir.is_dir():
            self.error(episodes_dir, "missing directory")
            return
        for path in sorted(episodes_dir.iterdir()):
            if not path.is_dir():
                continue
            if path.name == "templates":
                continue
            if path.name.startswith("."):
                continue
            if FOLDER_RE.match(path.name) is None:
                self.error(path, "episode folder name must be a number, optional letter")
                continue
            self.check_episode_folder(path, people_slugs, org_slugs)

    def check_episode_folder(
        self,
        folder: Path,
        people_slugs: set[str],
        org_slugs: set[str],
    ) -> None:
        match = FOLDER_RE.match(folder.name)
        if match is None:
            self.error(folder, "episode folder name must be a number, optional letter")
            return
        number = int(match.group(1))
        letter = match.group(2) or ""
        prefix = f"{folder.name}-"
        present: set[str] = set()
        for path in sorted(folder.iterdir()):
            if path.name.startswith("."):
                continue
            if path.is_dir():
                if path.name == "images":
                    self.check_episode_images(path)
                    continue
                self.error(path, "unexpected subdirectory (use .chunks/ only, gitignored)")
                continue
            if path.name in EXTRA_EPISODE_FILES:
                continue
            if not path.name.startswith(prefix):
                self.error(path, f"filename must start with {prefix}")
                continue
            suffix = path.name[len(prefix) :]
            if suffix not in ARTIFACT_SUFFIXES:
                self.error(
                    path,
                    f"unknown artifact; expected one of: {', '.join(ARTIFACT_SUFFIXES)}",
                )
                continue
            present.add(suffix)

        yml_path = folder / f"{folder.name}-episode.yml"
        if "episode.yml" not in present:
            self.error(folder, f"missing {number}-episode.yml")
            return

        try:
            data = load_yaml(yml_path)
        except yaml.YAMLError as exc:
            self.error(yml_path, f"invalid YAML: {exc}")
            return
        if not isinstance(data, dict):
            self.error(yml_path, "must be a mapping")
            return

        unknown = set(data) - EPISODE_TOP_KEYS
        if unknown:
            self.error(yml_path, f"unknown keys: {sorted(unknown)}")

        if data.get("episode") != number:
            self.error(yml_path, f"episode: {data.get('episode')!r} != {number}")
        variant = data.get("variant") or ""
        if not isinstance(variant, str) or variant != letter:
            self.error(yml_path, f"variant {variant!r} != folder letter {letter!r}")

        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            self.error(yml_path, "title must be a non-empty string")
            title = None
        else:
            expected_prefix = f"ББ-{folder.name}:"
            if not title.startswith(expected_prefix):
                self.error(yml_path, f"title must start with {expected_prefix!r}")

        status = data.get("status")
        if status not in STATUS_VALUES:
            self.error(yml_path, f"status must be one of {sorted(STATUS_VALUES)}")

        rec = data.get("recording_date")
        if rec != "unknown":
            if not isinstance(rec, (str, date)):
                self.error(yml_path, "recording_date must be YYYY-MM-DD or unknown")
            elif isinstance(rec, str) and parse_iso_date(rec) is None:
                self.error(yml_path, f"invalid recording_date: {rec!r}")

        if "publish_date" in data and data["publish_date"] is not None:
            pub = data["publish_date"]
            if not isinstance(pub, (str, date)):
                self.error(yml_path, "publish_date must be YYYY-MM-DD")
            elif isinstance(pub, str) and parse_iso_date(pub) is None:
                self.error(yml_path, f"invalid publish_date: {pub!r}")

        self.check_appearances(yml_path, data.get("hosts"), "hosts", people_slugs, org_slugs, False)
        self.check_appearances(yml_path, data.get("guests"), "guests", people_slugs, org_slugs, True)
        self.check_episode_url(yml_path, data.get("url"), status)
        self.check_optional_url(yml_path, data.get("youtube_url"), "youtube_url")
        self.check_libsyn_item_id(yml_path, data.get("libsyn_item_id"))
        self.check_audio(yml_path, data.get("audio_url"), data.get("audio_bytes"))

        shownotes = folder / f"{folder.name}-shownotes.md"
        transcript = folder / f"{folder.name}-transcript.md"
        readable = folder / f"{folder.name}-readable.md"
        if status == "catalog" and not shownotes.is_file():
            self.error(folder, f"shownotes required when status is catalog ({folder.name}-shownotes.md)")
        if status == "transcript-reviewed" and not transcript.is_file():
            self.error(
                folder,
                f"transcript required when status is transcript-reviewed ({number}-transcript.md)",
            )
        if status in {"readable-reviewed", "ready"}:
            if not transcript.is_file():
                self.error(
                    folder,
                    f"transcript required when status is {status} ({number}-transcript.md)",
                )
            if not readable.is_file():
                self.error(
                    folder,
                    f"readable required when status is {status} ({number}-readable.md)",
                )
        if status == "ready" and not shownotes.is_file():
            self.error(folder, f"shownotes required when status is ready ({number}-shownotes.md)")
        if shownotes.is_file():
            first = shownotes_first_line(shownotes)
            if title is not None and first != title:
                self.error(
                    shownotes,
                    f"first line {first!r} != title {title!r}",
                )

        if "readable.md" in present and "transcript.md" not in present:
            self.error(folder, "readable.md implies transcript.md")
        if "shorts.md" in present and "transcript.md" not in present:
            self.error(folder, "shorts.md implies transcript.md")

        for kind in ("transcript.md", "readable.md", "shorts.md"):
            if kind not in present:
                continue
            self.check_speech_file(folder / f"{folder.name}-{kind}", number, kind)

    def check_appearances(
        self,
        path: Path,
        value: Any,
        field: str,
        people_slugs: set[str],
        org_slugs: set[str],
        allow_org: bool,
    ) -> None:
        if value is None:
            self.error(path, f"missing {field}")
            return
        if not isinstance(value, list):
            self.error(path, f"{field} must be a list")
            return
        for i, item in enumerate(value):
            if not isinstance(item, dict):
                self.error(path, f"{field}[{i}] must be a mapping")
                continue
            allowed = {"slug", "organization"} if allow_org else {"slug"}
            unknown = set(item) - allowed
            if unknown:
                self.error(path, f"{field}[{i}] unknown keys: {sorted(unknown)}")
            if not allow_org and "organization" in item:
                self.error(path, f"{field}[{i}] organization only allowed on guests")
            slug = item.get("slug")
            if not isinstance(slug, str) or not SLUG_RE.match(slug):
                self.error(path, f"{field}[{i}] invalid slug: {slug!r}")
            elif slug not in people_slugs:
                self.error(path, f"{field}[{i}] unknown person slug {slug!r}")
            org = item.get("organization")
            if org is not None:
                if not isinstance(org, str) or not SLUG_RE.match(org):
                    self.error(path, f"{field}[{i}] invalid organization: {org!r}")
                elif org not in org_slugs:
                    self.error(path, f"{field}[{i}] unknown organization slug {org!r}")

    def check_episode_url(self, path: Path, value: Any, status: Any) -> None:
        if value is None or value == "":
            if status == "ready":
                self.error(path, f"url is required when status is {status}")
            return
        if not isinstance(value, str) or not URL_RE.match(value):
            self.error(path, "url must be an http(s) URL")

    def check_libsyn_item_id(self, path: Path, value: Any) -> None:
        if value is None or value == "":
            return
        if not isinstance(value, int) or value <= 0:
            self.error(path, f"libsyn_item_id must be a positive integer, got {value!r}")

    def check_audio(self, path: Path, url: Any, size: Any) -> None:
        has_url = url not in (None, "")
        has_size = size not in (None, "")
        if has_url != has_size:
            self.error(path, "audio_url and audio_bytes are set together")
            return
        if not has_url:
            return
        if not isinstance(url, str) or not URL_RE.match(url):
            self.error(path, "audio_url must be an http(s) URL")
        if not isinstance(size, int) or size <= 0:
            self.error(path, f"audio_bytes must be a positive integer, got {size!r}")

    def check_episode_images(self, path: Path) -> None:
        allowed = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
        for child in sorted(path.iterdir()):
            if child.name == "sources.txt":
                continue
            if child.is_dir() or child.suffix.lower() not in allowed:
                self.error(child, "unexpected file in images/")

    def check_optional_url(self, path: Path, value: Any, field: str) -> None:
        if value is None or value == "":
            return
        if not isinstance(value, str) or not URL_RE.match(value):
            self.error(path, f"{field} must be an http(s) URL")

    def check_speech_file(self, path: Path, number: int, kind: str) -> None:
        text = path.read_text(encoding="utf-8")
        data, _body, fm_errors = split_frontmatter(text)
        for err in fm_errors:
            self.error(path, err)
        if data is None:
            return
        if data.get("episode") != number:
            self.error(path, f"episode: {data.get('episode')!r} != {number}")
        if kind == "shorts.md":
            allowed = {"episode", "source"}
            source = data.get("source")
            expected_source = f"{number}-transcript.md"
            if source != expected_source:
                self.error(path, f"source must be {expected_source!r}")
        else:
            allowed = {"episode"}
        unknown = set(data) - allowed
        if unknown:
            self.error(path, f"unknown frontmatter keys: {sorted(unknown)}")


def shownotes_first_line(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            return line.strip()
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="repository root (default: parent of scripts/)",
    )
    args = parser.parse_args()
    root = args.root.resolve() if args.root else repo_root()
    return Checker(root).run()


if __name__ == "__main__":
    sys.exit(main())
