#!/usr/bin/env python3
"""Bake-off site: custom Python + Jinja from content/."""

from __future__ import annotations

import argparse
import math
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

EPISODE_NUMBERS = (221, 220, 219, 200)
PAGE_SIZE = 8

# Site chrome (bake-off). Internal targets use site paths; externals are absolute.
# Labels follow the live menu, plus Гости; order as agreed for the new archive.
NAV_ITEMS: list[dict[str, str]] = [
    {"label": "Выпуски", "target": ""},
    {"label": "Гости", "target": "guests"},
    {"label": "О подкасте", "target": "about"},
    {"label": "Поддержать", "target": "donate"},
    {"label": "Для спонсоров", "target": "for-sponsors"},
]

# Static chrome pages: (URL dir, markdown file under custom/pages/).
STATIC_PAGES: tuple[tuple[str, str], ...] = (
    ("about", "about.md"),
    ("donate", "donate.md"),
    ("for-sponsors", "for-sponsors.md"),
)

# Sidebar “Слушать подкаст” — URLs from https://basicblockradio.com/ (2026-07).
LISTEN_LINKS: list[dict[str, str]] = [
    {
        "label": "Apple Podcasts",
        "href": "https://podcasts.apple.com/ru/podcast/id1289965366",
    },
    {
        "label": "Google Podcasts",
        "href": (
            "https://podcasts.google.com/?feed="
            "aHR0cDovL2Jhc2ljYmxvY2tyYWRpby5saWJzeW4uY29tL3Jzcw"
        ),
    },
    {
        "label": "Spotify",
        "href": "https://open.spotify.com/show/4flYcruRigqZVPYBZRtMHa",
    },
    {
        "label": "Яндекс Музыка",
        "href": "https://music.yandex.ru/album/7638583",
    },
    {
        "label": "YouTube",
        "href": "https://www.youtube.com/channel/UC95bSmaFa7R33GOyi6VfyGQ",
    },
    {
        "label": "RSS",
        "href": "https://basicblockradio.libsyn.com/rss",
    },
]

# Bake-off only: real embeds from the current public pages, so we can
# judge YouTube + Libsyn players visually. Not part of the content model.
EMBEDS: dict[int, dict[str, str]] = {
    221: {
        "youtube": "https://www.youtube.com/embed/cUzzBAmCxcE",
        # width left empty (same as live WP embeds); size via CSS.
        "libsyn": (
            "https://html5-player.libsyn.com/embed/episode/id/41620665/"
            "height/100/width//thumbnail/no/render-playlist/no/"
            "theme/custom/tdest_id/1041254/custom-color/5a51ea"
        ),
    },
    220: {
        "youtube": "https://www.youtube.com/embed/BXp9PYwGB7A",
        "libsyn": (
            "https://html5-player.libsyn.com/embed/episode/id/41440480/"
            "height/100/width//thumbnail/no/render-playlist/no/"
            "theme/custom/tdest_id/1041254/custom-color/5a51ea"
        ),
    },
    219: {
        "youtube": "https://www.youtube.com/embed/rR6uApdr2aY",
        "libsyn": (
            "https://html5-player.libsyn.com/embed/episode/id/41034615/"
            "height/100/width//thumbnail/no/render-playlist/no/"
            "theme/custom/tdest_id/1041254/custom-color/5a51ea"
        ),
    },
    200: {
        "youtube": "https://www.youtube.com/embed/UzMZsiu-tSU",
        "libsyn": (
            "https://html5-player.libsyn.com/embed/episode/id/36904775/"
            "height/100/width//thumbnail/no/render-playlist/no/"
            "theme/custom/tdest_id/1041254/custom-color/5a51ea"
        ),
    },
}


@dataclass
class PersonRef:
    slug: str
    name: str


@dataclass
class Episode:
    number: int
    title: str
    recording_date: str | None
    publish_date: str | None
    hosts: list[PersonRef]
    guests: list[PersonRef]
    shownotes_html: str
    readable_html: str
    youtube_embed: str | None = None
    libsyn_embed: str | None = None
    people: list[PersonRef] = field(default_factory=list)


@dataclass
class Person:
    slug: str
    name: str
    links: dict[str, str]
    episodes: list[dict[str, Any]] = field(default_factory=list)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def bakeoff_root() -> Path:
    return Path(__file__).resolve().parents[1]


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    data = yaml.safe_load(raw) or {}
    if not isinstance(data, dict):
        data = {}
    return data, body


def md_to_html(text: str) -> str:
    return markdown.markdown(
        text,
        extensions=["extra", "sane_lists"],
        output_format="html",
    )


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected mapping")
    return data


def format_date(value: Any) -> str | None:
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def rel_url(page_dir: str, target: str) -> str:
    """Relative href from page_dir ('' | 'e221' | 'page/2' | 'people/x') to target.

    Page links end in index.html so file:// navigation works in Chrome
    (browsers do not map directory URLs to index.html without an HTTP server).
    """
    if page_dir:
        prefix = "../" * (page_dir.count("/") + 1)
    else:
        prefix = ""

    if target in ("", "."):
        return f"{prefix}index.html" if prefix else "index.html"

    # Assets keep their filename; HTML pages are directories with index.html.
    if "." in Path(target).name:
        return f"{prefix}{target}"
    return f"{prefix}{target}/index.html"


def load_person(content: Path, slug: str) -> Person:
    path = content / "people" / f"{slug}.md"
    text = path.read_text(encoding="utf-8")
    data, _body = split_frontmatter(text)
    name = str(data.get("name") or slug)
    links_raw = data.get("links") or {}
    links: dict[str, str] = {}
    if isinstance(links_raw, dict):
        for key, url in links_raw.items():
            if isinstance(url, str) and url:
                links[str(key)] = url
    return Person(slug=slug, name=name, links=links)


def load_episode(content: Path, number: int, people: dict[str, Person]) -> Episode:
    folder = content / "episodes" / str(number)
    meta = load_yaml(folder / f"{number}-episode.yml")

    def resolve(items: Any, field_name: str) -> list[PersonRef]:
        if not isinstance(items, list):
            raise ValueError(f"episode {number}: {field_name} must be a list")
        out: list[PersonRef] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            slug = item.get("slug")
            if not isinstance(slug, str):
                continue
            if slug not in people:
                people[slug] = load_person(content, slug)
            out.append(PersonRef(slug=slug, name=people[slug].name))
        return out

    hosts = resolve(meta.get("hosts"), "hosts")
    guests = resolve(meta.get("guests"), "guests")

    shownotes = (folder / f"{number}-shownotes.md").read_text(encoding="utf-8")
    readable_path = folder / f"{number}-readable.md"
    readable_html = ""
    if readable_path.is_file():
        _fm, readable_body = split_frontmatter(
            readable_path.read_text(encoding="utf-8")
        )
        readable_html = md_to_html(readable_body.strip())

    seen: set[str] = set()
    people_order: list[PersonRef] = []
    for ref in hosts + guests:
        if ref.slug not in seen:
            seen.add(ref.slug)
            people_order.append(ref)

    embeds = EMBEDS.get(number, {})
    return Episode(
        number=number,
        title=str(meta["title"]),
        recording_date=format_date(meta.get("recording_date")),
        publish_date=format_date(meta.get("publish_date")),
        hosts=hosts,
        guests=guests,
        shownotes_html=md_to_html(shownotes.strip()),
        readable_html=readable_html,
        youtube_embed=embeds.get("youtube"),
        libsyn_embed=embeds.get("libsyn"),
        people=people_order,
    )


def attach_person_episodes(episodes: list[Episode], people: dict[str, Person]) -> None:
    for ep in episodes:
        for ref in ep.hosts:
            people[ref.slug].episodes.append(
                {"number": ep.number, "title": ep.title, "role": "ведущий"}
            )
        for ref in ep.guests:
            people[ref.slug].episodes.append(
                {"number": ep.number, "title": ep.title, "role": "гость"}
            )


def write_page(path: Path, html: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def load_static_page(pages_dir: Path, filename: str) -> tuple[str, str]:
    text = (pages_dir / filename).read_text(encoding="utf-8").strip()
    title = filename
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    return title, md_to_html(text)


def build(root: Path, out: Path) -> None:
    content = root / "content"
    custom_dir = Path(__file__).resolve().parent
    templates_dir = custom_dir / "templates"
    pages_dir = custom_dir / "pages"
    shared_css = bakeoff_root() / "shared" / "site.css"

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    css_dest = out / "css" / "site.css"
    css_dest.parent.mkdir(parents=True)
    shutil.copy2(shared_css, css_dest)

    people: dict[str, Person] = {}
    episodes = [load_episode(content, n, people) for n in EPISODE_NUMBERS]
    attach_person_episodes(episodes, people)

    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    def render(template_name: str, page_dir: str, **ctx: Any) -> str:
        tmpl = env.get_template(template_name)

        def nav_href(item: dict[str, str]) -> str:
            if "href" in item:
                return item["href"]
            return rel_url(page_dir, item["target"])

        return tmpl.render(
            rel=lambda target: rel_url(page_dir, target),
            nav_items=NAV_ITEMS,
            nav_href=nav_href,
            listen_links=LISTEN_LINKS,
            **ctx,
        )

    page_count = max(1, math.ceil(len(episodes) / PAGE_SIZE))
    for page_number in range(1, page_count + 1):
        start = (page_number - 1) * PAGE_SIZE
        chunk = episodes[start : start + PAGE_SIZE]
        prev_page = page_number - 1 if page_number > 1 else None
        next_page = page_number + 1 if page_number < page_count else None
        if page_number == 1:
            page_dir = ""
            dest = out / "index.html"
        else:
            page_dir = f"page/{page_number}"
            dest = out / "page" / str(page_number) / "index.html"
        html = render(
            "feed.html",
            page_dir,
            episodes=chunk,
            page_number=page_number,
            prev_page=prev_page,
            next_page=next_page,
        )
        write_page(dest, html)

    for ep in episodes:
        page_dir = f"e{ep.number}"
        html = render("episode.html", page_dir, episode=ep)
        write_page(out / page_dir / "index.html", html)

    for person in sorted(people.values(), key=lambda p: p.slug):
        page_dir = f"people/{person.slug}"
        html = render("person.html", page_dir, person=person)
        write_page(out / "people" / person.slug / "index.html", html)

    guests_by_first = [
        p
        for p in sorted(people.values(), key=lambda x: x.name)
        if any(ep.get("role") == "гость" for ep in p.episodes)
    ]
    guests_by_last = sorted(
        guests_by_first, key=lambda x: x.name.split()[-1]
    )
    html = render("guests.html", "guests", guests=guests_by_first, sort_mode="first")
    write_page(out / "guests" / "index.html", html)
    html = render(
        "guests.html", "guests/by-last-name", guests=guests_by_last, sort_mode="last"
    )
    write_page(out / "guests" / "by-last-name" / "index.html", html)

    for page_dir, filename in STATIC_PAGES:
        page_title, page_html = load_static_page(pages_dir, filename)
        html = render(
            "page.html",
            page_dir,
            page_title=page_title,
            page_html=page_html,
        )
        write_page(out / page_dir / "index.html", html)

    print(f"Built {len(episodes)} episodes, {len(people)} people → {out}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="repository root (default: three levels above this script)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="output directory (default: site/bakeoff/custom/public)",
    )
    args = parser.parse_args()
    root = args.root.resolve() if args.root else repo_root()
    out = args.out.resolve() if args.out else Path(__file__).resolve().parent / "public"
    build(root, out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
