# Site

Zola + thin Python adapter building the public archive from `content/`.
Product contract: `docs/website.md`.

## Layout

- `zola/adapt.py` — build entrypoint: projects `content/` into gitignored
  staging (`zola/.build/`), runs the pinned Zola binary, writes feed,
  sitemap, and robots files alongside the output
- `zola/templates/` — Tera templates
- `zola/pages/` — static page Markdown
  (about, donate, for-sponsors, and the other kept pages)
- `zola/config.toml` — Zola config (`base_url` stays `/`
  so `file://` preview keeps working)
- `shared/site.css` — the single stylesheet, copied to output at build time
- `.tools/` — pinned Zola binary (downloaded release, not a system package)
- `.venv/` — Python env for the adapter (`pip install -r requirements.txt`)

## Build

From the repository root:

```bash
site/.venv/bin/python site/zola/adapt.py
```

Output: `site/zola/public/`.

## Preview

```bash
python3 -m http.server 8000 --directory site/zola/public
```

Or open `site/zola/public/index.html` via `file://`
(embeds need HTTP).
