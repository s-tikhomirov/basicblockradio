# Tasks

## Raw Ideas

- Shorts: optional `content/episodes/templates/shorts-template.md`
  mirroring the skill frontmatter if editors want a file scaffold beside shownotes.
- Website search (Ctrl+K): after the public archive launches,
  an in-site command palette to search episodes, people, and later topics.
  Build-time index over repo content is enough.
- RSS: after the archive site exists,
  generate a podcast RSS feed from repo content
  (episode metadata + enclosure URLs).
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
- WordPress historical import and domain cutover:
  after the new site MVP is agreed.
- Website track as separate projects if ever:
  internal CMS, finance or sponsor accounting, manager control plane.
- Dogfood decentralized tech for the podcast:
  static site on IPFS with a domain gateway;
  mirror audio or archive blobs on decentralized storage
  while keeping conventional hosting.
- Decentralized social presence:
  evaluate Mastodon, Bluesky, or similar alongside Telegram.

## Todo

- License: how to license a repository with content and code (scripts).
  CC-BY is not well suited for code.
  Add a separate license for scripts if needed.
- Scripts: runnable from any working directory
  with stable repo-root resolution.

## In Progress

## Done

- Episode file naming and title canon:
  enforced by `scripts/check_content.py`
  (see `docs/content-model.md`).

## Wontfix

- People bios auto-injected into show notes or about pages.
  Rejected for v1 as too rigid.
  Keep episode- and podcast-level prose hand-written.
