#!/usr/bin/env python3
"""Thin adapter: project content/ into a Zola tree, then build."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import Any

import markdown
import yaml

EPISODE_NUMBERS = tuple(range(223, 199, -1))  # full catalog, reverse numeric sort
PAGE_SIZE = 8

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


def write_md(path: Path, frontmatter: dict[str, Any], body: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = f"---\n{dump_frontmatter(frontmatter)}---\n"
    if body:
        text += body
        if not body.endswith("\n"):
            text += "\n"
    path.write_text(text, encoding="utf-8")


def project(root: Path, build: Path) -> list[dict[str, Any]]:
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

    for weight, number in enumerate(EPISODE_NUMBERS, start=1):
        folder = content / "episodes" / str(number)
        meta = load_yaml(folder / f"{number}-episode.yml")

        def resolve(items: Any) -> list[dict[str, str]]:
            out: list[dict[str, str]] = []
            if not isinstance(items, list):
                return out
            for item in items:
                if not isinstance(item, dict):
                    continue
                slug = item.get("slug")
                if not isinstance(slug, str):
                    continue
                if slug not in people:
                    people[slug] = load_person_meta(content, slug)
                    people[slug]["episodes"] = []
                    people[slug]["is_guest"] = False
                    people[slug]["guest_episodes"] = []
                out.append({"slug": slug, "name": people[slug]["name"]})
            return out

        hosts = resolve(meta.get("hosts"))
        guests = resolve(meta.get("guests"))

        for ref in hosts:
            people[ref["slug"]]["episodes"].append(
                {
                    "number": number,
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

        shownotes = (folder / f"{number}-shownotes.md").read_text(encoding="utf-8")
        shownotes_html = md_to_html(shownotes.strip())
        (data_episodes / f"e{number}-shownotes.html").write_text(
            shownotes_html,
            encoding="utf-8",
        )

        readable_path = folder / f"{number}-readable.md"
        if readable_path.is_file():
            _fm, readable_body = split_frontmatter(
                readable_path.read_text(encoding="utf-8")
            )
            (data_episodes / f"e{number}-readable.html").write_text(
                md_to_html(readable_body.strip()),
                encoding="utf-8",
            )

        embeds = {"libsyn": _libsyn_embed(_LIBYSN_IDS[number])} if number in _LIBYSN_IDS else {}
        ep_date = display_date(meta)
        ep_excerpt = excerpt(shownotes_html)
        frontmatter: dict[str, Any] = {
            "title": str(meta["title"]),
            "template": "episode.html",
            "weight": weight,
            "extra": {
                "number": number,
                "hosts": hosts,
                "guests": guests,
                "people": people_order,
                "youtube_embed": youtube_embed(meta.get("youtube_url")),
                "libsyn_embed": embeds.get("libsyn", ""),
                "description": ep_excerpt,
            },
        }
        if ep_date:
            frontmatter["extra"]["display_date"] = ep_date

        write_md(content_out / f"e{number}.md", frontmatter)
        episodes_meta.append(
            {
                "number": number,
                "title": str(meta["title"]),
                "date": _PUBDATES[number],
                "excerpt": ep_excerpt,
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

    guests_list = [
        {
            "slug": p["slug"],
            "name": p["name"],
            "guest_episodes": [
                {"number": e["number"], "title": e["title"]}
                for e in p["episodes"]
                if e["role"] == "гость"
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

    print(
        f"Projected {len(episodes_meta)} episodes, {len(people)} people → {build}"
    )
    return episodes_meta


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
        audio_url, audio_len = _AUDIO[ep["number"]]
        items.append(
            "  <item>\n"
            f"    <title>{sax.escape(ep['title'])}</title>\n"
            f"    <link>{SITE_URL}/e{ep['number']}/</link>\n"
            f"    <guid isPermaLink=\"false\">bbr-{ep['number']}</guid>\n"
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


def run_zola(
    build: Path, out: Path, episodes: list[dict[str, Any]] | None = None
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

    # Recipe URL map has / and pagers only; Zola also emits /page/1/.
    page1 = out / "page" / "1"
    if page1.exists():
        shutil.rmtree(page1)

    write_rss(out, episodes or [])
    write_sitemap(out)
    write_robots(out)


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

    episodes = project(root, build)
    run_zola(build, out, episodes)
    print(f"Built → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
