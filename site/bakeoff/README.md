# Site stack bake-off

Isolated experiment trees for comparing static site generators.
Recipe: `docs/site-stack-bakeoff.md`.

Tools and build output stay gitignored under this directory
(`.venv/`, `.tools/`, `**/public/`, `**/.build/`).

## Install tools (local only)

From repo root:

```bash
cd site/bakeoff
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Hugo and Zola binaries live in `.tools/` (downloaded release archives, not
system packages). Expected layout after install:

```text
site/bakeoff/.tools/hugo
site/bakeoff/.tools/zola
site/bakeoff/.venv/          # Jinja + Pelican + deps
```

Verify:

```bash
site/bakeoff/.tools/hugo version
site/bakeoff/.tools/zola --version
site/bakeoff/.venv/bin/pelican --version
site/bakeoff/.venv/bin/python -c 'import jinja2, yaml, markdown; print(jinja2.__version__, yaml.__version__, markdown.__version__)'
```

Pinned at install time (re-download if you wipe `.tools/`):

- Hugo `v0.164.0` linux/amd64
- Zola `v0.22.1` x86_64-unknown-linux-gnu
- Pelican `4.12.0` (plus Jinja2, PyYAML, Markdown from `requirements.txt`)

## Custom Python + Jinja

```bash
site/bakeoff/.venv/bin/python site/bakeoff/custom/build.py
```

Output: `site/bakeoff/custom/public/`.

Preview (optional local server):

```bash
python3 -m http.server 8000 --directory site/bakeoff/custom/public
```

Or open `site/bakeoff/custom/public/index.html` via `file://`.

## Other stacks

Hugo, Zola, and Pelican trees are not implemented yet.
Use `.tools/hugo`, `.tools/zola`, and `.venv/bin/pelican` when they are.

## Wipe tools

```bash
rm -rf site/bakeoff/.venv site/bakeoff/.tools
rm -rf site/bakeoff/custom/public site/bakeoff/hugo/public \
       site/bakeoff/zola/public site/bakeoff/pelican/public
rm -rf site/bakeoff/**/.build
```
