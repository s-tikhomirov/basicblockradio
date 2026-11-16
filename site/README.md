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

## Publish

A push to `master` builds the site and deploys `site/zola/public/` to GitHub Pages.
A pull request to `master` runs the same build.
`workflow_dispatch` deploys the same way as a push.
The workflow is `.github/workflows/deploy.yml`.
The contributor steps around the pull request are in the repository README, under CI/CD.

The runner installs Python dependencies from `site/requirements.txt`
and Zola 0.22.1, the release the local build uses.
`site/.venv/` and `site/.tools/` stay out of git.
`adapt.py` expects the binary at `site/.tools/zola`.

From the repository root the build command is `python site/zola/adapt.py`.
`base_url` in `site/zola/config.toml` stays `/`,
so pages are served at the root of basicblockradio.com.

The deploy job uploads `site/zola/public/`
and publishes it with the GitHub Pages upload and deploy actions.
That job has `pages: write` and `id-token: write`,
and it uses the `github-pages` environment.

GitHub Pages uses this workflow as its source.
The custom domain is `basicblockradio.com`.
Enforce HTTPS is on for that name.

`site/zola/pending-episodes.txt` lists episode slugs that get a short page
saying «Этот выпуск скоро будет опубликован.»
until that episode is part of the public build.
The address map for old paths is in `docs/website.md`.
