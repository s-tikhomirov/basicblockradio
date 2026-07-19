# Site stack bake-off

Isolated experiment trees for comparing static site generators.
Recipe: `docs/site-stack-bakeoff.md`.

Tools and build output stay gitignored under this directory
(`.venv/`, `.tools/`, `**/public/`, `**/.build/`).

## Python environment

```bash
cd site/bakeoff
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

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

## Wipe tools

```bash
rm -rf site/bakeoff/.venv site/bakeoff/.tools
rm -rf site/bakeoff/**/public site/bakeoff/**/.build
```
