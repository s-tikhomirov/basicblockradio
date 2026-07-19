# Shared bake-off assets

`site.css` is the single stylesheet for Hugo, Zola, Pelican, and custom Jinja.
Freeze and agree on this file before implementing (or re-implementing) stacks.

Each build must copy it to `public/css/site.css`.
Static chrome Markdown for about / donate / for-sponsors lives under
`site/bakeoff/custom/pages/` and should be reused by every stack.
