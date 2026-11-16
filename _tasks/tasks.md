# Tasks

## Raw Ideas

- Shorts: optional `content/episodes/templates/shorts-template.md`
  mirroring the skill frontmatter if editors want a file scaffold beside shownotes.
- Website search (Ctrl+K): after the public archive launches,
  an in-site command palette to search episodes, people, and later topics.
  Build-time index over repo content is enough.
- Privacy-preserving metrics (only if ever needed):
  server log aggregates or a self-hosted, cookieless counter.
  Default remains no metrics (see `docs/website.md`).
- Self-hosted audio: store MP3s on own object storage / CDN
  and point RSS enclosures there.
- Episode artwork automation:
  scripts or agent skills to speed cover generation from template + guest photo + title.
  Keep out of `site/` static HTML build.
- Topics: curated topic vocabulary and episode filters after v1.
- Related episodes (`related_episodes` or derived "also appeared in"):
  postpone past v1.
- Website track as separate projects if ever:
  internal CMS, finance or sponsor accounting, manager control plane.
- Dogfood decentralized tech for the podcast:
  static site on IPFS with a domain gateway;
  mirror audio or archive blobs on decentralized storage
  while keeping conventional hosting.
- Decentralized social presence:
  evaluate Mastodon, Bluesky, or similar alongside Telegram.

## Todo

- Stallman videos for `/bb-bonus-rms/`.
  The page links to `https://basicblockradio.com/wp-content/uploads/stallman.mp4`
  (229 MB) and `stallman_hq.mp4` (2.1 GB).
  On 2026-11-16 those URLs answered 404.
  Recover the files from the WordPress host.
  They stay out of git.
  Publish them at `/files/bb-bonus-rms/stallman.mp4` and `/files/bb-bonus-rms/stallman_hq.mp4`.
  A host that refuses a 2 GB file, or bills heavily for that download,
  serves the same paths from Cloudflare R2.
  R2 does not charge for egress, which matters for a 2 GB file.
  Then point the bonus page at those paths.
  After the files are copied, the WordPress host can be turned off.
- DNS hosting.
  The domain is published by Yandex DNS (`dns1.yandex.net`, `dns2.yandex.net`).
  Move it to another DNS host.
  The new host publishes the records that answer today,
  and the nameservers change after those records answer.
  - apex `A`: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
  - `www` `CNAME` to `s-tikhomirov.github.io`
  - GitHub Pages verification `TXT` at `_github-pages-challenge-s-tikhomirov`
    (`ca43c91017127a86db043b979aa92a`)
  - `MX` `10 mx.yandex.net`
  - SPF `TXT` `v=spf1 redirect=_spf.yandex.net`
  - Google site-verification `TXT`
    `google-site-verification=95bCZeEJuBqgDXXMjxcgJC2-y1eUWmzVKsEpzKvkQME`
  - DKIM `TXT` at `mail._domainkey`
    (`v=DKIM1; k=rsa; t=s; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCgdZmMj0+vjxR6ZsAhFVy6aphueULK2ZCia8zTa9tDnvoUBZYfLPjkKxvm3NySC/Py1/zsG5EQQF7DsYvQRmDRgxZQsH5ZkFLplbCGsU4u7NZRRrrhq31y/FY6FFJYvklgDQIFWcxP/i+/oZdV+32p3YjPVDPQ5yb19cGP/NvIuQIDAQAB`)
  Add the apex `AAAA` records from GitHub's custom-domain guide.
  `https://www.basicblockradio.com/` presents a certificate for `*.github.io`.
  Give `www` a certificate that matches that name.
  `http://www.basicblockradio.com/` redirects to `https://basicblockradio.com/`.
- Catalog credit review for episode 193b.
  In `content/people/historical-review.csv` the guests and hosts status cells are empty.
  `OK` in a status cell means that side is reviewed.
  The row is finished when both status cells are `OK`.
  The filing rule is in `docs/content-model.md`.
- License: how to license a repository with content and code (scripts).
  CC-BY is not well suited for code.
  Add a separate license for scripts if needed.
- Scripts: runnable from any working directory
  with stable repo-root resolution.

## In Progress

## Done

- RSS: podcast RSS feed generated from repo content
  (`/rss.xml` in the Zola build; metadata + enclosure URLs).
- Episode file naming and title canon:
  enforced by `scripts/check_content.py`
  (see `docs/content-model.md`).

## Wontfix

- People bios auto-injected into show notes or about pages.
  Rejected for v1 as too rigid.
  Keep episode- and podcast-level prose hand-written.
