#!/usr/bin/env python3
"""Pull episodes before 200 from WordPress, the Libsyn RSS, and the audio playlist.

Writes content/episodes/NNN as status catalog.
Hosts and guests stay empty.
People guesses go to content/people/historical-review.csv.
"""

from __future__ import annotations

import csv
import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
EPISODES = ROOT / "content" / "episodes"
PEOPLE = ROOT / "content" / "people"
REVIEW = PEOPLE / "historical-review.csv"
LOG = PEOPLE / "catalog-import-log.txt"
PENDING = ROOT / "site" / "zola" / "pending-episodes.txt"
PLAYLIST = "PLU_YQeud2Sg4aasRHsI11tTyq4nF8Tk4X"
WP = "https://basicblockradio.com/wp-json/wp/v2/posts"
RSS_URL = "https://basicblockradio.libsyn.com/rss"
UA = "Mozilla/5.0 (compatible; basicblockradio-catalog/1.0)"

FOLDER_RE = re.compile(r"^(\d{3,})([a-z])?$")
TITLE_KEY_RE = re.compile(r"ББ[- ]0*(\d+)([a-z])?(?![0-9a-z])", re.I)
IFRAME_RE = re.compile(r"<iframe\b[^>]*>\s*</iframe>", re.I)
IMG_RE = re.compile(r"<img\b[^>]*>", re.I)
P_RE = re.compile(r"<p\b[^>]*>[\s\S]*?</p>", re.I)
HREF_RE = re.compile(r"""href\s*=\s*(["'])(.*?)\1""", re.I)
YT_EMBED_RE = re.compile(r"youtube(?:-nocookie)?\.com/embed/([\w-]{11})")
LIBSYN_RE = re.compile(r"libsyn\.com/embed/episode/id/(\d+)")
CONTENT_NS = {"content": "http://purl.org/rss/1.0/modules/content/"}


def fetch(url: str, data: bytes | None = None, headers: dict[str, str] | None = None) -> bytes:
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read()


def folder_key_from_title(title: str) -> str | None:
    match = TITLE_KEY_RE.search(title)
    if match is None:
        return None
    return f"{int(match.group(1)):03d}{match.group(2) or ''}"


def folder_from_wp_slug(slug: str) -> str | None:
    match = re.fullmatch(r"e(\d+)([a-z]?)", slug)
    if match:
        return f"{int(match.group(1)):03d}{match.group(2)}"
    match = re.fullmatch(r"ep(\d+)", slug)
    if match:
        return f"{int(match.group(1)):03d}"
    return None


def plain(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    text = html.unescape(text).replace("\xa0", " ")
    return re.sub(r"\s+", " ", text).strip()


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def load_wp_posts() -> list[dict]:
    posts: list[dict] = []
    for page in range(1, 6):
        url = f"{WP}?per_page=100&page={page}&_fields=slug,date,title,content"
        try:
            batch = json.loads(fetch(url))
        except urllib.error.HTTPError as exc:
            if exc.code == 400 and posts:
                break
            raise
        if not batch:
            break
        posts.extend(batch)
    return posts


def load_rss() -> dict[str, dict[str, str | int]]:
    root = ET.fromstring(fetch(RSS_URL))
    found: dict[str, dict[str, str | int]] = {}
    for item in root.find("channel").findall("item"):
        title = item.findtext("title") or ""
        key = folder_key_from_title(title)
        if key is None:
            continue
        enclosure = item.find("enclosure")
        url = enclosure.get("url") if enclosure is not None else ""
        length = enclosure.get("length") if enclosure is not None else ""
        found.setdefault(key, {"title": title, "url": url or "", "length": length or ""})
    return found


def playlist_videos() -> list[tuple[str, str]]:
    page = fetch(
        f"https://www.youtube.com/playlist?list={PLAYLIST}&hl=ru"
    ).decode("utf-8", "replace")
    match = re.search(r"ytInitialData\s*=\s*", page)
    if match is None:
        raise SystemExit("playlist page has no ytInitialData")
    data, _end = json.JSONDecoder().raw_decode(page, match.end())
    key_match = re.search(r'"INNERTUBE_API_KEY":"([^"]+)"', page)
    version_match = re.search(r'"INNERTUBE_CLIENT_VERSION":"([^"]+)"', page)
    if key_match is None or version_match is None:
        raise SystemExit("playlist page has no Innertube key")
    api_key = key_match.group(1)
    version = version_match.group(1)
    videos: list[tuple[str, str]] = []
    seen: set[str] = set()

    def take(node: object) -> None:
        if isinstance(node, dict):
            title = ""
            metadata = node.get("metadata")
            if isinstance(metadata, dict):
                title = (
                    metadata.get("lockupMetadataViewModel", {})
                    .get("title", {})
                    .get("content", "")
                )
            content_id = node.get("contentId")
            if isinstance(content_id, str) and isinstance(title, str) and title:
                if content_id not in seen:
                    seen.add(content_id)
                    videos.append((content_id, title))
            for value in node.values():
                take(value)
        elif isinstance(node, list):
            for value in node:
                take(value)

    def continuation(node: object) -> str | None:
        found: list[str] = []

        def walk(inner: object) -> None:
            if isinstance(inner, dict):
                token = inner.get("token")
                request = inner.get("request")
                if (
                    isinstance(token, str)
                    and len(token) > 40
                    and request == "CONTINUATION_REQUEST_TYPE_BROWSE"
                ):
                    found.append(token)
                for value in inner.values():
                    walk(value)
            elif isinstance(inner, list):
                for value in inner:
                    walk(value)

        walk(node)
        return found[0] if found else None

    take(data)
    token = continuation(data)
    while token:
        body = json.dumps(
            {
                "context": {
                    "client": {
                        "clientName": "WEB",
                        "clientVersion": version,
                        "hl": "ru",
                        "gl": "RU",
                    }
                },
                "continuation": token,
            }
        ).encode()
        payload = json.loads(
            fetch(
                f"https://www.youtube.com/youtubei/v1/browse?key={api_key}&prettyPrint=false",
                data=body,
                headers={"Content-Type": "application/json"},
            )
        )
        before = len(videos)
        take(payload)
        token = continuation(payload) if len(videos) > before else None
    return videos


def oembed_title(video_id: str, cache: dict[str, str]) -> str:
    if video_id in cache:
        return cache[video_id]
    url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
    try:
        payload = json.loads(fetch(url))
        title = str(payload.get("title") or "")
    except Exception:
        title = ""
    cache[video_id] = title
    return title


def rewrite_href(url: str) -> str:
    match = re.match(
        r"https?://(?:www\.)?basicblockradio\.com(?P<path>/[^?#]*)?(?P<query>\?[^#]*)?(?P<hash>#.*)?$",
        url,
        re.I,
    )
    if match is None or match.group("query"):
        return url
    path = match.group("path") or "/"
    if path.startswith("/wp-"):
        return url
    episode = re.fullmatch(r"/ep(\d+)/?", path)
    if episode:
        path = f"/e{int(episode.group(1)):03d}/"
    episode = re.fullmatch(r"/e(\d+)([a-z]?)/?", path)
    if episode:
        path = f"/e{int(episode.group(1)):03d}{episode.group(2)}/"
    fragment = match.group("hash") or ""
    if path == "/":
        return "../index.html" + fragment
    return ".." + path.rstrip("/") + "/index.html" + fragment


def strip_iframes(source: str, drop_src: re.Pattern[str]) -> str:
    def keep(match: re.Match[str]) -> str:
        tag = match.group(0)
        if drop_src.search(tag):
            return ""
        return tag

    return IFRAME_RE.sub(keep, source)


def drop_yoki(source: str) -> tuple[str, list[str]]:
    removed: list[str] = []

    def keep(match: re.Match[str]) -> str:
        block = match.group(0)
        if re.search(r"yoki|йоки", block, re.I):
            removed.append(plain(block))
            return ""
        return block

    return P_RE.sub(keep, source), removed


def save_images(folder: Path, source: str, notes: list[str]) -> str:
    images = folder / "images"
    written: list[str] = []
    index = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal index
        tag = match.group(0)
        src_match = re.search(r"""\bsrc=(["'])(.*?)\1""", tag, re.I)
        if src_match is None:
            return tag
        src = html.unescape(src_match.group(2)).strip()
        if src.startswith("//"):
            src = "https:" + src
        parts = urllib.parse.urlsplit(src)
        src = urllib.parse.urlunsplit(
            (
                parts.scheme or "https",
                parts.netloc,
                urllib.parse.quote(parts.path, safe="/%"),
                parts.query,
                "",
            )
        )
        if "wp-content/uploads" not in src:
            return tag
        index += 1
        suffix = Path(src.split("?", 1)[0]).suffix.lower()
        if suffix not in {".png", ".jpg", ".jpeg", ".gif", ".webp"}:
            suffix = ".png"
        name = f"{index:02d}{suffix}"
        dest = images / name
        try:
            dest.write_bytes(fetch(src))
        except Exception as exc:
            notes.append(f"image download failed {src} ({exc})")
            return tag
        alt_match = re.search(r"""\balt=(["'])(.*?)\1""", tag, re.I)
        alt = html.unescape(alt_match.group(2)) if alt_match else ""
        written.append(f"{name}\t{dest.stat().st_size}\t{alt}\t{src}")
        alt_attr = f' alt="{html.escape(alt, quote=True)}"' if alt else ""
        return f'<img src="images/{name}"{alt_attr}>'

    images.mkdir(parents=True, exist_ok=True)
    updated = IMG_RE.sub(replace, source)
    if written:
        (images / "sources.txt").write_text("\n".join(written) + "\n", encoding="utf-8")
    elif images.is_dir() and not any(images.iterdir()):
        images.rmdir()
    return updated


def tidy(source: str) -> str:
    source = re.sub(r"<!--\s*iframe plugin.*?-->", "", source, flags=re.I)
    source = re.sub(
        r"<a\b[^>]*directory\.libsyn\.com[^>]*>\s*</a>",
        "",
        source,
        flags=re.I,
    )
    previous = None
    while previous != source:
        previous = source
        source = re.sub(r"<(p|div|figure)\b[^>]*>\s*</\1>", "", source, flags=re.I)
        source = re.sub(r"<p>\s*(?:<br\s*/?>|&nbsp;|\s)*</p>", "", source, flags=re.I)
    return source.strip()


def norm_name(value: str) -> str:
    text = value.casefold().replace("ё", "е")
    text = re.sub(r"[^0-9a-zа-я ]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def split_people(chunk: str) -> list[str]:
    parts = re.split(r"\s*,\s*|\s+и\s+", chunk.strip())
    return [part.strip(" .") for part in parts if part.strip(" .")]


def propose_people(title: str) -> list[tuple[str, str, str]]:
    match = re.match(r"^ББ-[^:]+:\s*(?P<rest>.*)$", title)
    if match is None:
        return [("", "", "title has no colon")]
    rest = match.group("rest").strip()
    rows: list[tuple[str, str, str]] = []
    feature = re.search(r"(?:feat\.?|ft\.?)\s+([^)]+)", rest, re.I)
    if feature:
        for name in split_people(feature.group(1).strip(" )")):
            rows.append((name, "", "feat"))
    named = re.match(
        r"(?P<names>.+?)\s+\((?P<org>[^)]+)\)\s+(?:о|об|про)\b",
        rest,
    )
    if named and not re.search(r"feat\.?|ft\.?", named.group("org"), re.I):
        for name in split_people(named.group("names")):
            rows.append((name, named.group("org").strip(), "name-org"))
    if rows:
        unique: list[tuple[str, str, str]] = []
        seen: set[tuple[str, str]] = set()
        for row in rows:
            key = (norm_name(row[0]), norm_name(row[1]))
            if key in seen or not row[0]:
                continue
            seen.add(key)
            unique.append(row)
        return unique
    loose = re.match(r"(?P<names>[A-ZА-ЯЁ][^:]{0,80}?)\s+(?:on|о|об|про)\b", rest)
    if loose and rest[:1].isupper():
        chunk = re.sub(r"^[^,]+\u0021\s*", "", loose.group("names").strip())
        return [(name, "", "unsure") for name in split_people(chunk)]
    return [("", "", "no guest in title")]


def load_existing_people() -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for path in sorted(PEOPLE.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^name:\s*(.+)$", text, re.M)
        if match is None:
            continue
        found.append((path.stem, match.group(1).strip().strip('"')))
    return found


def match_person(name: str, people: list[tuple[str, str]]) -> str:
    wanted = norm_name(name)
    if not wanted:
        return ""
    hits = [slug for slug, existing in people if norm_name(existing) == wanted]
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        return "ambiguous:" + ",".join(hits)
    return ""


def write_episode(folder: str, number: int, letter: str, title: str, day: str, fields: dict[str, object], body: str) -> None:
    dest = EPISODES / folder
    dest.mkdir(parents=True, exist_ok=True)
    yml_path = dest / f"{folder}-episode.yml"
    credits = "hosts: []\n\nguests: []"
    if yml_path.is_file():
        old = yml_path.read_text(encoding="utf-8")
        kept = re.search(r"hosts:.*?(?=\nurl:)", old, re.S)
        if kept and "slug:" in kept.group(0):
            credits = kept.group(0).rstrip()
    lines = [
        f"episode: {number}",
        f"title: {yaml_string(title)}",
        "status: catalog",
        "",
        "recording_date: unknown",
        f"publish_date: {day}",
        "",
        credits,
        "",
        f"url: https://basicblockradio.com/e{folder}/",
    ]
    if letter:
        lines.append(f"variant: {letter}")
    youtube = fields.get("youtube_url")
    if isinstance(youtube, str) and youtube:
        lines.append(f"youtube_url: {yaml_string(youtube)}")
    libsyn = fields.get("libsyn_item_id")
    if isinstance(libsyn, int):
        lines.append(f"libsyn_item_id: {libsyn}")
    audio_url = fields.get("audio_url")
    audio_bytes = fields.get("audio_bytes")
    if isinstance(audio_url, str) and audio_url and isinstance(audio_bytes, int):
        lines.append(f"audio_url: {yaml_string(audio_url)}")
        lines.append(f"audio_bytes: {audio_bytes}")
    lines.append("")
    (dest / f"{folder}-episode.yml").write_text("\n".join(lines), encoding="utf-8")
    (dest / f"{folder}-shownotes.md").write_text(title + "\n\n" + body.strip() + "\n", encoding="utf-8")


def sheet_field(value: str) -> str:
    return value.replace("\n", " ").strip()


def write_review(rows: list[list[str]]) -> None:
    with REVIEW.open("w", encoding="utf-8-sig", newline="") as handle:
        csv.writer(handle).writerows(rows)


def main() -> None:
    posts = load_wp_posts()
    rss = load_rss()
    playlist = playlist_videos()
    by_folder: dict[str, list[tuple[str, str]]] = {}
    for video_id, title in playlist:
        key = folder_key_from_title(title)
        if key is None:
            continue
        by_folder.setdefault(key, []).append((video_id, title))
    people = load_existing_people()
    titles_cache: dict[str, str] = {}
    log: list[str] = []
    review_rows: list[list[str]] = [[
        "folder",
        "title",
        "guessed_name",
        "source",
        "existing_slug",
    ]]
    imported: list[str] = []

    for post in posts:
        folder = folder_from_wp_slug(post["slug"])
        if folder is None:
            continue
        match = FOLDER_RE.match(folder)
        if match is None:
            continue
        number = int(match.group(1))
        letter = match.group(2) or ""
        if number >= 200:
            continue
        title = plain(post["title"]["rendered"])
        expected = f"ББ-{folder}:"
        if not title.startswith(expected):
            parsed = re.match(r"ББ[- ]0*(\d+)([a-z])?:\s*(.*)$", title, re.I)
            if parsed and f"{int(parsed.group(1)):03d}{parsed.group(2) or ''}" == folder:
                title = f"{expected} {parsed.group(3).strip()}".strip()
                log.append(f"{folder}\ttitle prefix aligned to {expected}")
            else:
                log.append(f"{folder}\ttitle does not start with {expected}: {title}")
        day = str(post["date"])[:10]
        source = post["content"]["rendered"]
        notes: list[str] = []
        embed_ids = list(dict.fromkeys(YT_EMBED_RE.findall(source)))
        chosen = ""
        matched_embeds: list[str] = []
        for video_id in embed_ids:
            embed_title = oembed_title(video_id, titles_cache)
            if folder_key_from_title(embed_title) == folder:
                matched_embeds.append(video_id)
            elif embed_title:
                notes.append(f"embed {video_id} is {embed_title}")
            else:
                notes.append(f"embed {video_id} has no oEmbed title")
        if len(matched_embeds) == 1:
            chosen = matched_embeds[0]
        elif len(matched_embeds) > 1:
            notes.append("several episode embeds: " + ", ".join(matched_embeds))
        playlist_hits = by_folder.get(folder, [])
        playlist_ids = [video_id for video_id, _title in playlist_hits]
        if not chosen and len(playlist_ids) == 1:
            chosen = playlist_ids[0]
            notes.append("youtube from audio playlist")
        elif not chosen and len(playlist_ids) > 1:
            notes.append("playlist has several videos: " + ", ".join(playlist_ids))
        elif not chosen and not playlist_ids:
            notes.append("no youtube url")
        elif chosen and playlist_ids and chosen not in playlist_ids:
            notes.append("playlist id differs: " + ", ".join(playlist_ids))
        libsyn_ids = list(dict.fromkeys(LIBSYN_RE.findall(source)))
        libsyn_item: int | None = None
        if len(libsyn_ids) == 1:
            libsyn_item = int(libsyn_ids[0])
        elif len(libsyn_ids) > 1:
            libsyn_item = int(libsyn_ids[0])
            notes.append("several libsyn ids: " + ", ".join(libsyn_ids))
        else:
            notes.append("no libsyn player")
        audio = rss.get(folder)
        audio_url = ""
        audio_bytes = 0
        if audio and audio["url"] and str(audio["length"]).isdigit():
            audio_url = str(audio["url"])
            audio_bytes = int(audio["length"])
        elif audio:
            notes.append("rss item has no enclosure length")
        else:
            notes.append("no rss item")
        drop = []
        if chosen:
            drop.append(re.escape(chosen))
        drop.append(r"libsyn\.com")
        cleaned = strip_iframes(source, re.compile("|".join(drop), re.I))
        cleaned, yoki_blocks = drop_yoki(cleaned)
        for block in yoki_blocks:
            notes.append("removed yoki paragraph: " + block[:180])
        cleaned = HREF_RE.sub(
            lambda m: f'href="{rewrite_href(m.group(2).strip())}"',
            cleaned,
        )
        episode_dir = EPISODES / folder
        episode_dir.mkdir(parents=True, exist_ok=True)
        cleaned = save_images(episode_dir, cleaned, notes)
        cleaned = tidy(cleaned)
        fields: dict[str, object] = {}
        if chosen:
            fields["youtube_url"] = f"https://www.youtube.com/watch?v={chosen}"
        if libsyn_item is not None:
            fields["libsyn_item_id"] = libsyn_item
        if audio_url and audio_bytes:
            fields["audio_url"] = audio_url
            fields["audio_bytes"] = audio_bytes
        write_episode(folder, number, letter, title, day, fields, cleaned)
        imported.append(folder)
        for name, _org, kind in propose_people(title):
            review_rows.append([
                sheet_field(part)
                for part in (
                    folder,
                    title,
                    name,
                    {
                        "name-org": "title names a person and an organization",
                        "unsure": "title names a person",
                        "feat": "feat. credit",
                        "no guest in title": "title names no guest",
                    }.get(kind, kind),
                    match_person(name, people),
                )
            ])
        for note in notes:
            log.append(f"{folder}\t{note}")

    write_review(review_rows)
    LOG.write_text("\n".join(log) + "\n", encoding="utf-8")
    published = {f"e{folder}" for folder in imported}
    published.add("ep099")
    kept = []
    for line in PENDING.read_text(encoding="utf-8").splitlines():
        if line.strip() in published:
            continue
        kept.append(line)
    PENDING.write_text("\n".join(kept).rstrip() + "\n", encoding="utf-8")
    print(f"imported {len(imported)} episodes")
    print(f"playlist videos {len(playlist)}")
    print(f"review rows {len(review_rows) - 1}")
    print(f"log lines {len(log)}")


if __name__ == "__main__":
    main()
