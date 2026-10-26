#!/usr/bin/env python3
"""Thin adapter: project content/ into a Zola tree, then build."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import Any

import markdown
import yaml

PAGE_SIZE = 8
PUBLIC_STATUSES = frozenset({"ready", "catalog"})
FOLDER_RE = re.compile(r"^(\d{3,})([a-z])?$")

# Player embeds. Libsyn item IDs mined from the Libsyn RSS feed (libsyn:item-id).
def _libsyn_embed(episode_id: int) -> str:
    return (
        f"https://html5-player.libsyn.com/embed/episode/id/{episode_id}/"
        "height/100/width//thumbnail/no/render-playlist/no/"
        "theme/custom/tdest_id/1041254/custom-color/5a51ea"
    )


# Libsyn item IDs mined from the Libsyn RSS feed (libsyn:item-id).
# YouTube IDs are hand-verified only for 221, 220, 219, 200; RSS descriptions
# carry several ambiguous video links, so no YouTube embeds are guessed.
_LIBYSN_IDS = {
    200: 36904775, 201: 37201175, 202: 37293375, 203: 37360490,
    204: 37439240, 205: 37531235, 206: 37881405, 207: 38130610,
    208: 38254855, 209: 38650500, 210: 38975905, 211: 39037865,
    212: 39252045, 213: 39442365, 214: 39666875, 215: 39732875,
    216: 39992260, 217: 40106790, 218: 40868785, 219: 41034615,
    220: 41440480, 221: 41620665, 222: 41956790, 223: 42315795,
}
def youtube_embed(watch_url: Any) -> str:
    if not isinstance(watch_url, str) or not watch_url:
        return ""
    m = re.search(r"[?&]v=([\w-]{6,})", watch_url)
    if not m:
        m = re.search(r"youtu\.be/([\w-]{6,})", watch_url)
    if not m:
        m = re.search(r"/embed/([\w-]{6,})", watch_url)
    if not m:
        return ""
    return f"https://www.youtube-nocookie.com/embed/{m.group(1)}"

STATIC_PAGES: tuple[tuple[str, str], ...] = (
    ("about", "about.md"),
    ("donate", "donate.md"),
    ("for-sponsors", "for-sponsors.md"),
    ("best-of-2020", "best-of-2020.md"),
    ("bb-bonus-rms", "bb-bonus-rms.md"),
    ("ep100an", "ep100an.md"),
)


def stack_dir() -> Path:
    return Path(__file__).resolve().parent


def site_root() -> Path:
    return stack_dir().parent


def repo_root() -> Path:
    return stack_dir().parents[1]


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


def display_date(meta: dict[str, Any]) -> str | None:
    pub = format_date(meta.get("publish_date"))
    if pub:
        return pub
    rec = format_date(meta.get("recording_date"))
    if rec and rec != "unknown":
        return rec
    return None


def load_person_meta(content: Path, slug: str) -> dict[str, Any]:
    path = content / "people" / f"{slug}.md"
    data, _body = split_frontmatter(path.read_text(encoding="utf-8"))
    name = str(data.get("name") or slug)
    links_raw = data.get("links") or {}
    links: dict[str, str] = {}
    if isinstance(links_raw, dict):
        for key, url in links_raw.items():
            if isinstance(url, str) and url:
                links[str(key)] = url
    return {"slug": slug, "name": name, "links": links}


def dump_frontmatter(data: dict[str, Any]) -> str:
    return yaml.safe_dump(
        data,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    ).rstrip() + "\n"


_SHOWNOTES_SECTION = re.compile(
    r"^## Shownotes line[ \t]*\n(.*?)(?=^## |\Z)",
    re.M | re.S,
)
_MD_LINK = re.compile(r"\[[^\]]*\]\((https?://[^)\s]+)\)")


def shownotes_link(body: str) -> str | None:
    match = _SHOWNOTES_SECTION.search(body)
    if not match:
        return None
    link = _MD_LINK.search(match.group(1))
    return link.group(1) if link else None


def active_sponsor_logos(content: Path, latest: int) -> tuple[list[dict[str, str]], list[tuple[Path, str]]]:
    """Sponsors whose paid range includes the latest published episode."""
    sp_dir = content / "sponsorships"
    sponsors: list[dict[str, str]] = []
    copies: list[tuple[Path, str]] = []
    if not sp_dir.is_dir():
        return sponsors, copies
    for path in sorted(sp_dir.glob("*.md")):
        if path.name == "sponsorship-template.md":
            continue
        data, body = split_frontmatter(path.read_text(encoding="utf-8"))
        org = data.get("organization")
        first = data.get("first_episode")
        last = data.get("last_episode")
        logo = data.get("logo")
        if not isinstance(org, str) or not isinstance(first, int) or not isinstance(last, int):
            continue
        if not (first <= latest <= last):
            continue
        if not isinstance(logo, str) or not logo.strip():
            raise SystemExit(f"{path}: active sponsorship is missing logo")
        src = sp_dir / logo
        if not src.is_file():
            raise SystemExit(f"{path}: missing logo file {logo}")
        url = shownotes_link(body)
        if url is None:
            raise SystemExit(f"{path}: Shownotes line needs one markdown link")
        org_path = content / "organizations" / f"{org}.yml"
        org_data = load_yaml(org_path) if org_path.is_file() else {}
        name = org_data.get("name") if isinstance(org_data, dict) else None
        if not isinstance(name, str) or not name.strip():
            name = org
        public_logo = f"sponsors/{src.name}"
        sponsors.append({"name": name, "url": url, "logo": public_logo})
        copies.append((src, public_logo))
    sponsors.sort(key=lambda item: item["name"].casefold())
    return sponsors, copies


def project_articles(
    content: Path, content_out: Path, data_pages: Path
) -> list[tuple[Path, str]]:
    """Publish content/articles as /articles/ and one page per article."""
    root = content / "articles"
    copies: list[tuple[Path, str]] = []
    index_path = root / "index.md"
    if not index_path.is_file():
        return copies
    text = index_path.read_text(encoding="utf-8").strip()
    title = "Статьи"
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break
    html_name = "articles.html"
    (data_pages / html_name).write_text(md_to_html(text), encoding="utf-8")
    write_md(
        content_out / "articles" / "_index.md",
        {
            "title": title,
            "template": "static.html",
            "extra": {"html_file": html_name},
        },
    )
    for folder in sorted(path for path in root.iterdir() if path.is_dir()):
        article = folder / "article.md"
        if not article.is_file():
            continue
        body = article.read_text(encoding="utf-8").strip()
        article_title = folder.name
        for line in body.splitlines():
            if line.startswith("# "):
                article_title = line[2:].strip()
                break
        html_name = f"article-{folder.name}.html"
        (data_pages / html_name).write_text(md_to_html(body), encoding="utf-8")
        write_md(
            content_out / "articles" / folder.name / "_index.md",
            {
                "title": article_title,
                "template": "static.html",
                "extra": {"html_file": html_name},
            },
        )
        for kind in ("images", "files"):
            folder_files = folder / kind
            if not folder_files.is_dir():
                continue
            for item in folder_files.iterdir():
                if item.suffix == ".txt" or not item.is_file():
                    continue
                copies.append((item, f"articles/{folder.name}/{kind}/{item.name}"))
    return copies


def write_md(path: Path, frontmatter: dict[str, Any], body: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = f"---\n{dump_frontmatter(frontmatter)}---\n"
    if body:
        text += body
        if not body.endswith("\n"):
            text += "\n"
    path.write_text(text, encoding="utf-8")


def project(root: Path, build: Path) -> tuple[list[dict[str, Any]], list[tuple[Path, str]]]:
    content = root / "content"
    custom_pages = stack_dir() / "pages"
    zola = stack_dir()

    if build.exists():
        shutil.rmtree(build)
    build.mkdir(parents=True)

    shutil.copy2(zola / "config.toml", build / "config.toml")
    shutil.copytree(zola / "templates", build / "templates")

    content_out = build / "content"
    data_episodes = build / "data" / "episodes"
    data_pages = build / "data" / "pages"
    data_episodes.mkdir(parents=True)
    data_pages.mkdir(parents=True)

    write_md(
        content_out / "_index.md",
        {
            "title": "Выпуски",
            "sort_by": "weight",
            "paginate_by": PAGE_SIZE,
            "paginate_path": "page",
        },
    )

    people: dict[str, dict[str, Any]] = {}
    episodes_meta: list[dict[str, Any]] = []
    image_copies: list[tuple[Path, str]] = []

    def resolve(items: Any) -> list[dict[str, str]]:
        out: list[dict[str, str]] = []
        if not isinstance(items, list):
            return out
        for item in items:
            if not isinstance(item, dict):
                continue
            person_slug = item.get("slug")
            if not isinstance(person_slug, str):
                continue
            if person_slug not in people:
                people[person_slug] = load_person_meta(content, person_slug)
                people[person_slug]["episodes"] = []
                people[person_slug]["is_guest"] = False
                people[person_slug]["guest_episodes"] = []
            out.append({"slug": person_slug, "name": people[person_slug]["name"]})
        return out

    included: list[tuple[Path, dict[str, Any], int, str]] = []
    episodes_dir = content / "episodes"
    for folder in episodes_dir.iterdir():
        folder_match = FOLDER_RE.match(folder.name)
        if not folder.is_dir() or folder_match is None:
            continue
        meta_path = folder / f"{folder.name}-episode.yml"
        if not meta_path.is_file():
            continue
        meta = load_yaml(meta_path)
        if meta.get("status") not in PUBLIC_STATUSES:
            continue
        number = int(folder_match.group(1))
        public_slug = f"e{folder.name}"
        included.append((folder, meta, number, public_slug))

    def sort_date(row: tuple[Path, dict[str, Any], int, str]) -> str:
        _folder, meta, number, _slug = row
        published = format_date(meta.get("publish_date"))
        if published:
            return published
        return _PUBDATES.get(number, "")

    included.sort(key=lambda row: (sort_date(row), row[3]), reverse=True)

    for weight, (folder, meta, number, public_slug) in enumerate(included, start=1):
        hosts = resolve(meta.get("hosts"))
        guests = resolve(meta.get("guests"))

        for ref in hosts:
            people[ref["slug"]]["episodes"].append(
                {
                    "number": number,
                    "slug": public_slug,
                    "title": str(meta["title"]),
                    "role": "ведущий",
                }
            )
        for ref in guests:
            people[ref["slug"]]["is_guest"] = True
            people[ref["slug"]]["guest_episodes"].append(number)
            people[ref["slug"]]["episodes"].append(
                {
                    "number": number,
                    "slug": public_slug,
                    "title": str(meta["title"]),
                    "role": "гость",
                }
            )

        seen: set[str] = set()
        people_order: list[dict[str, str]] = []
        for ref in hosts + guests:
            if ref["slug"] not in seen:
                seen.add(ref["slug"])
                people_order.append(ref)

        shownotes = (folder / f"{folder.name}-shownotes.md").read_text(encoding="utf-8")
        shownotes_html = md_to_html(shownotes.strip())
        (data_episodes / f"{public_slug}-shownotes.html").write_text(
            shownotes_html,
            encoding="utf-8",
        )

        readable_path = folder / f"{folder.name}-readable.md"
        if readable_path.is_file():
            _fm, readable_body = split_frontmatter(
                readable_path.read_text(encoding="utf-8")
            )
            (data_episodes / f"{public_slug}-readable.html").write_text(
                md_to_html(readable_body.strip()),
                encoding="utf-8",
            )

        images = folder / "images"
        if images.is_dir():
            for img in images.iterdir():
                if img.suffix == ".txt" or not img.is_file():
                    continue
                image_copies.append((img, f"{public_slug}/images/{img.name}"))

        item_id = meta.get("libsyn_item_id")
        if not isinstance(item_id, int):
            item_id = _LIBYSN_IDS.get(number)
        libsyn = _libsyn_embed(item_id) if isinstance(item_id, int) else ""
        audio_url = meta.get("audio_url") if isinstance(meta.get("audio_url"), str) else ""
        audio_bytes = meta.get("audio_bytes") if isinstance(meta.get("audio_bytes"), int) else 0
        if not audio_url and number in _AUDIO:
            audio_url, audio_bytes = _AUDIO[number]
        ep_date = display_date(meta)
        ep_excerpt = excerpt(shownotes_html)
        frontmatter: dict[str, Any] = {
            "title": str(meta["title"]),
            "template": "episode.html",
            "weight": weight,
            "extra": {
                "number": number,
                "slug": public_slug,
                "hosts": hosts,
                "guests": guests,
                "people": people_order,
                "youtube_embed": youtube_embed(meta.get("youtube_url")),
                "libsyn_embed": libsyn,
                "description": ep_excerpt,
            },
        }
        if ep_date:
            frontmatter["extra"]["display_date"] = ep_date

        write_md(content_out / f"{public_slug}.md", frontmatter)
        episodes_meta.append(
            {
                "number": number,
                "slug": public_slug,
                "title": str(meta["title"]),
                "date": sort_date((folder, meta, number, public_slug)),
                "excerpt": ep_excerpt,
                "audio_url": audio_url,
                "audio_bytes": audio_bytes,
            }
        )

    write_md(
        content_out / "people" / "_index.md",
        {"title": "People", "render": False},
    )

    for slug, person in sorted(people.items(), key=lambda item: item[0]):
        person_extra: dict[str, Any] = {
            "slug": slug,
            "is_guest": bool(person["is_guest"]),
            "episodes": person["episodes"],
            "guest_episodes": person["guest_episodes"],
        }
        if person["links"]:
            person_extra["links"] = person["links"]
        write_md(
            content_out / "people" / f"{slug}.md",
            {
                "title": person["name"],
                "template": "person.html",
                "extra": person_extra,
            },
        )

    write_md(
        content_out / "all-episodes" / "_index.md",
        {
            "title": "Все выпуски",
            "template": "all-episodes.html",
            "extra": {
                "episodes": [
                    {"slug": ep["slug"], "title": ep["title"]}
                    for ep in episodes_meta
                ],
            },
        },
    )

    guests_list = [
        {
            "slug": p["slug"],
            "name": p["name"],
            "guest_episodes": [
                {"number": e["number"], "slug": e["slug"], "title": e["title"]}
                for e in p["episodes"]
                if e["role"] == "гость"
            ],
            "host_episodes": [
                {"number": e["number"], "slug": e["slug"], "title": e["title"]}
                for e in p["episodes"]
                if e["role"] == "ведущий"
            ],
        }
        for p in sorted(people.values(), key=lambda x: x["name"])
        if p["is_guest"]
    ]
    guests_by_last = sorted(guests_list, key=lambda p: p["name"].split()[-1])
    write_md(
        content_out / "guests" / "_index.md",
        {
            "title": "Гости",
            "template": "guests.html",
            "extra": {"guests": guests_list, "sort_mode": "first"},
        },
    )
    write_md(
        content_out / "guests" / "by-last-name" / "_index.md",
        {
            "title": "Гости",
            "template": "guests.html",
            "extra": {"guests": guests_by_last, "sort_mode": "last"},
        },
    )

    for page_dir, filename in STATIC_PAGES:
        text = (custom_pages / filename).read_text(encoding="utf-8").strip()
        title = filename
        for line in text.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        html_name = f"{page_dir}.html"
        (data_pages / html_name).write_text(md_to_html(text), encoding="utf-8")
        write_md(
            content_out / page_dir / "_index.md",
            {
                "title": title,
                "template": "static.html",
                "extra": {"html_file": html_name},
            },
        )

    latest = max((ep["number"] for ep in episodes_meta), default=None)
    if latest is None:
        sponsors, logo_copies = [], []
    else:
        sponsors, logo_copies = active_sponsor_logos(content, latest)
    (build / "data" / "sidebar.json").write_text(
        json.dumps({"sponsors": sponsors}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    article_copies = project_articles(content, content_out, data_pages)
    print(
        f"Projected {len(episodes_meta)} episodes, {len(people)} people, "
        f"{len(sponsors)} sponsor logos (latest episode {latest}) → {build}"
    )
    return episodes_meta, logo_copies + article_copies + image_copies


SITE_URL = "https://basicblockradio.com"

# Audio enclosures mined from the Libsyn RSS feed (enclosure url + HEAD length).
_AUDIO: dict[int, tuple[str, int]] = {
    200: ("https://traffic.libsyn.com/secure/basicblockradio/BB_200.mp3?dest-id=573859", 84790009),
    201: ("https://traffic.libsyn.com/secure/basicblockradio/BB_201.mp3?dest-id=573859", 117358710),
    202: ("https://traffic.libsyn.com/secure/basicblockradio/BB_202.mp3?dest-id=573859", 45901960),
    203: ("https://traffic.libsyn.com/secure/basicblockradio/BB_203.mp3?dest-id=573859", 45431348),
    204: ("https://traffic.libsyn.com/secure/basicblockradio/BB_204.mp3?dest-id=573859", 51075939),
    205: ("https://traffic.libsyn.com/secure/basicblockradio/BB_205.mp3?dest-id=573859", 55349365),
    206: ("https://traffic.libsyn.com/secure/basicblockradio/BB_206.mp3?dest-id=573859", 44569448),
    207: ("https://traffic.libsyn.com/secure/basicblockradio/BB_207.mp3?dest-id=573859", 40848136),
    208: ("https://traffic.libsyn.com/secure/basicblockradio/BB_208.mp3?dest-id=573859", 35917356),
    209: ("https://traffic.libsyn.com/secure/basicblockradio/BB_209.mp3?dest-id=573859", 56828201),
    210: ("https://traffic.libsyn.com/secure/basicblockradio/basicblockradio-ep210_2025-11-07.mp3?dest-id=573859", 153063522),
    211: ("https://traffic.libsyn.com/secure/basicblockradio/Basicblocradio-ep-211-2025-11-14.mp3?dest-id=573859", 87451835),
    212: ("https://traffic.libsyn.com/secure/basicblockradio/Basicblockradio-Ep-212-25-12-3.mp3?dest-id=573859", 100687417),
    213: ("https://traffic.libsyn.com/secure/basicblockradio/-213___XLN_______.mp3?dest-id=573859", 108979649),
    214: ("https://traffic.libsyn.com/secure/basicblockradio/-214___Messari-2026.__1.___TradFi_ft.__.mp3?dest-id=573859", 108117298),
    215: ("https://traffic.libsyn.com/secure/basicblockradio/-215.mp3?dest-id=573859", 142569802),
    216: ("https://traffic.libsyn.com/secure/basicblockradio/-216______Savant.chat__-__Web3.mp3?dest-id=573859", 86471835),
    217: ("https://traffic.libsyn.com/secure/basicblockradio/-217__Messari-2026.__3._DeAI__DePIN_ft.__.mp3?dest-id=573859", 104769125),
    218: ("https://traffic.libsyn.com/secure/basicblockradio/_218___________.mp3?dest-id=573859", 102267818),
    219: ("https://traffic.libsyn.com/secure/basicblockradio/-219_____Lido_Ethereum__DeFi___.mp3?dest-id=573859", 82066798),
    220: ("https://traffic.libsyn.com/secure/basicblockradio/BB-220_-_.__1___.mp3?dest-id=573859", 98872987),
    221: ("https://traffic.libsyn.com/secure/basicblockradio/-221.mp3?dest-id=573859", 92958179),
    222: ("https://traffic.libsyn.com/secure/basicblockradio/-222___Resolv_______.mp3?dest-id=573859", 93829527),
    223: ("https://traffic.libsyn.com/secure/basicblockradio/-223__DWeb_Camp.____.mp3?dest-id=573859", 102583948),
}

# Publication dates mined from the Libsyn RSS feed (pubDate).
_PUBDATES = {
    200: "2025-06-08", 201: "2025-06-28", 202: "2025-07-06", 203: "2025-07-10",
    204: "2025-07-17", 205: "2025-07-24", 206: "2025-08-19", 207: "2025-09-08",
    208: "2025-09-17", 209: "2025-10-20", 210: "2025-11-10", 211: "2025-11-14",
    212: "2025-12-03", 213: "2025-12-17", 214: "2026-01-09", 215: "2026-01-15",
    216: "2026-02-04", 217: "2026-02-14", 218: "2026-04-14", 219: "2026-04-27",
    220: "2026-05-27", 221: "2026-06-12", 222: "2026-07-03", 223: "2026-08-04",
}


def excerpt(html: str, limit: int = 300) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        cut = text[:limit].rsplit(" ", 1)[0]
        return cut + "…"
    return text


def rfc2822(day: str) -> str:
    dt = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return format_datetime(dt)


def write_rss(out: Path, episodes: list[dict[str, Any]]) -> None:
    import xml.sax.saxutils as sax

    items = []
    for ep in sorted(episodes, key=lambda e: e["date"], reverse=True):
        audio_url = ep.get("audio_url") or ""
        audio_len = ep.get("audio_bytes") or 0
        if not audio_url or not audio_len:
            continue
        items.append(
            "  <item>\n"
            f"    <title>{sax.escape(ep['title'])}</title>\n"
            f"    <link>{SITE_URL}/{ep['slug']}/</link>\n"
            f"    <guid isPermaLink=\"false\">bbr-{ep['slug']}</guid>\n"
            f"    <pubDate>{rfc2822(ep['date'])}</pubDate>\n"
            f"    <description>{sax.escape(ep['excerpt'])}</description>\n"
            "    <enclosure"
            f" url=\"{sax.escape(audio_url)}\""
            f" length=\"{audio_len}\" type=\"audio/mpeg\" />\n"
            "  </item>"
        )
    rss = (
        "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
        "<rss version=\"2.0\">\n"
        "<channel>\n"
        "  <title>Базовый Блок — подкаст про блокчейн</title>\n"
        f"  <link>{SITE_URL}/</link>\n"
        "  <description>Архив выпусков подкаста «Базовый Блок» с полными текстами и расшифровками.</description>\n"
        "  <language>ru</language>\n" + "\n".join(items) + "\n</channel>\n</rss>\n"
    )
    (out / "rss.xml").write_text(rss, encoding="utf-8")


def write_sitemap(out: Path) -> None:
    import xml.sax.saxutils as sax

    urls = []
    for index in sorted(out.rglob("index.html")):
        rel = index.parent.relative_to(out).as_posix()
        loc = SITE_URL + ("/" if rel == "." else f"/{rel}/")
        urls.append(f"  <url><loc>{sax.escape(loc)}</loc></url>")
    sm = (
        "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
        "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    (out / "sitemap.xml").write_text(sm, encoding="utf-8")


def write_robots(out: Path) -> None:
    (out / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n",
        encoding="utf-8",
    )


# Old WordPress paths that point at an episode already in this build.
REDIRECTS: tuple[tuple[str, str, str], ...] = (
    ("for-sponsors-and-advertisers", "for-sponsors/index.html", "/for-sponsors/"),
    ("ep212", "e212/index.html", "/e212/"),
    ("ep099", "e099/index.html", "/e099/"),
    ("https-basicblockradio-com-e214", "e214/index.html", "/e214/"),
    ("https-basicblockradio-com-e215", "e215/index.html", "/e215/"),
    ("best-of-basic-block-1", "best-of-2020/index.html", "/best-of-2020/"),
    (
        "базовый-блок-лучшее-часть-2-из-4",
        "best-of-2020/index.html",
        "/best-of-2020/",
    ),
    (
        "базовый-блок-лучшее-часть-3-из-4",
        "best-of-2020/index.html",
        "/best-of-2020/",
    ),
    ("flash-attacks", "articles/flash-attacks/index.html", "/articles/flash-attacks/"),
    (
        "51-percent-attack",
        "articles/51-percent-attack/index.html",
        "/articles/51-percent-attack/",
    ),
    (
        "bitcoin-reformation",
        "articles/bitcoin-reformation/index.html",
        "/articles/bitcoin-reformation/",
    ),
)


def pending_episode_slugs() -> list[str]:
    path = stack_dir() / "pending-episodes.txt"
    slugs = []
    if not path.is_file():
        return slugs
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            slugs.append(line)
    return slugs


def notice_page(title: str, message: str, home_href: str, css_href: str, logo_href: str) -> str:
    return (
        "<!DOCTYPE html>\n"
        '<html lang="ru">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"  <title>{title}</title>\n"
        '  <meta name="robots" content="noindex">\n'
        f'  <link rel="stylesheet" href="{css_href}">\n'
        "</head>\n"
        "<body>\n"
        '  <div class="wrap">\n'
        '    <header class="site">\n'
        f'      <h1><a href="{home_href}"><img class="logo" src="{logo_href}" alt="Базовый Блок" width="240" height="52"></a></h1>\n'
        "    </header>\n"
        "    <main>\n"
        f"      <p>{message}</p>\n"
        f'      <p><a href="{home_href}">На главную</a></p>\n'
        "    </main>\n"
        "  </div>\n"
        "</body>\n"
        "</html>\n"
    )


def redirect_page(target: str) -> str:
    return (
        "<!DOCTYPE html>\n"
        '<html lang="ru">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'  <meta http-equiv="refresh" content="0; url={target}">\n'
        f'  <link rel="canonical" href="{target}">\n'
        "  <title>Базовый Блок</title>\n"
        '  <meta name="robots" content="noindex">\n'
        "</head>\n"
        "<body>\n"
        f'  <p><a href="{target}">Дальше</a></p>\n'
        "</body>\n"
        "</html>\n"
    )


def write_cutover(out: Path, published: set[str]) -> None:
    """Soon pages, address redirects, and the 404 page."""
    soon = notice_page(
        "Выпуск скоро будет опубликован — Базовый Блок",
        "Этот выпуск скоро будет опубликован.",
        "../index.html",
        "../css/site.css",
        "../logo.png",
    )
    written = 0
    for slug in pending_episode_slugs():
        if slug in published:
            continue
        dest = out / slug / "index.html"
        if dest.exists():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(soon, encoding="utf-8")
        written += 1

    rules = []
    for folder, relative, absolute in REDIRECTS:
        dest = out / folder / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(redirect_page("../" + relative), encoding="utf-8")
        rules.append(f"/{folder} {absolute} 301")
        rules.append(f"/{folder}/ {absolute} 301")
    # Episode numbers with no file (not published yet) go to the main page.
    # Hosts that honor _redirects apply this only when the file is absent.
    rules.append("/e:episode / 302")
    (out / "_redirects").write_text("\n".join(rules) + "\n", encoding="utf-8")

    (out / "404.html").write_text(
        notice_page(
            "Страница не найдена — Базовый Блок",
            "Страница не найдена.",
            "/",
            "/css/site.css",
            "/logo.png",
        ),
        encoding="utf-8",
    )
    print(f"Cutover: {written} soon pages, {len(REDIRECTS)} redirects, 404")


def run_zola(
    build: Path,
    out: Path,
    episodes: list[dict[str, Any]] | None = None,
    logo_copies: list[tuple[Path, str]] | None = None,
) -> None:
    zola_bin = site_root() / ".tools" / "zola"
    if not zola_bin.is_file():
        raise SystemExit(f"missing Zola binary: {zola_bin}")

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    subprocess.run(
        [
            str(zola_bin),
            "--root",
            str(build),
            "build",
            "--output-dir",
            str(out),
            "--force",
        ],
        check=True,
    )

    css_src = site_root() / "shared" / "site.css"
    css_dest = out / "css" / "site.css"
    css_dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(css_src, css_dest)
    shutil.copy2(site_root() / "shared" / "logo.png", out / "logo.png")
    about_dir = out / "about"
    about_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(stack_dir() / "pages" / "about-screenshot.png", about_dir / "about-screenshot.png")
    for src, rel in logo_copies or []:
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)

    # Recipe URL map has / and pagers only; Zola also emits /page/1/.
    page1 = out / "page" / "1"
    if page1.exists():
        shutil.rmtree(page1)

    write_rss(out, episodes or [])
    write_sitemap(out)
    write_robots(out)
    published = {ep["slug"] for ep in episodes or []}
    write_cutover(out, published)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="repository root (default: three levels above this script)",
    )
    parser.add_argument(
        "--build",
        type=Path,
        default=None,
        help="staging directory (default: site/zola/.build)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="output directory (default: site/zola/public)",
    )
    args = parser.parse_args()
    root = args.root.resolve() if args.root else repo_root()
    zola = stack_dir()
    build = args.build.resolve() if args.build else zola / ".build"
    out = args.out.resolve() if args.out else zola / "public"

    episodes, logo_copies = project(root, build)
    run_zola(build, out, episodes, logo_copies)
    print(f"Built → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
