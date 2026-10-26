# Website migration

Last updated: 2026-10-26

Status key: settled means the migration follows this until explicitly changed.
Open means decide before the domain cutover.

This file is the plan for serving basicblockradio.com
from the static archive in this repo.
Product contract: `docs/website.md`.

## Where things stand

WordPress is the live site.
It holds 235 posts,
from `e000` (2019-01-30) through episode 223.

The static site is the Zola build under `site/zola/`.
It publishes episodes with `status: ready`.
That set is episodes 200–223.
Episode 224 is in the repo as `readable-reviewed`,
so the build leaves it out until that status changes.

Three of the ready episodes are on WordPress under a slug
other than `/eNNN/`.
The episode files already name the canonical page:

- episode 212 is live at `/ep212/`, canonical `https://basicblockradio.com/e212/`
- episode 214 is live at `/https-basicblockradio-com-e214/`, canonical `/e214/`
- episode 215 is live at `/https-basicblockradio-com-e215/`, canonical `/e215/`

Episodes before 200 are in the build with status `catalog`.
`/ep099/` redirects to `/e099/`.
`/e106b/`, `/e107b/`, and `/e119b/` stay at those addresses.

Listening stays on the Libsyn RSS.
Both sites already point subscribers there.
The static build also writes `/rss.xml`.

## Settled

Decided 2026-10-26, together with the product contract.

The public site is static HTML generated from `content/`.
Publishing is a rebuild of the repo.
The public host has no admin login.

These WordPress behaviors end at cutover:

- Tags.
- Comments.
  The live site has no published comments.
  Forms still open on older posts close with WordPress.
- Query search at `/?s=`.
  A later in-site search stays parked in `_tasks/tasks.md`.
- The «Предложить тему» page (`/suggest/`) and its Google Form.
- Episode rubrics (Лекция, Конференция, Проект, and the rest).
  The product contract already leaves topics and format rubrics out of this version.

The static site already has the home feed,
episode pages with show notes, readable text, and YouTube and Libsyn players,
the guests index, person pages,
and the about, donate, and for-sponsors pages.
The menu includes Чат, linking to `https://t.me/basicblockradio_chat`.
The listen sidebar keeps Apple Podcasts, Google Podcasts, Spotify,
Яндекс Музыка, YouTube, and the Libsyn RSS.
The donate page keeps Patreon, Boosty, and the BTC and ETH addresses.
Sponsor lines inside show notes stay in the episode body.

Every page links to Patreon and Boosty.
A sponsor logo is shown with it
while the highest episode number in the public build
falls inside that sponsorship's `first_episode`..`last_episode`.
The logo file and the paid range live on the sponsorship
(`content/sponsorships/`, field `logo`).
The image links to the URL in that file's `Shownotes line`.

Episodes before 200 publish as `catalog`: show notes and the page URL.
Guest names on those episodes are a guess from the title.
The review of those names is a separate pass, below.

## Old addresses

Settled 2026-10-26.
The build writes the pages and a `_redirects` file.

- `/for-sponsors-and-advertisers/` redirects to `/for-sponsors/`
- `/all-episodes/` redirects to the main page
- `/ep212/` redirects to `/e212/`
- `/https-basicblockradio-com-e214/` redirects to `/e214/`
- `/https-basicblockradio-com-e215/` redirects to `/e215/`
- `/best-of-basic-block-1/` redirects to `/best-of-2020/`
- `/базовый-блок-лучшее-часть-2-из-4/` redirects to `/best-of-2020/`
- `/базовый-блок-лучшее-часть-3-из-4/` redirects to `/best-of-2020/`
- `/flash-attacks/` redirects to `/articles/flash-attacks/`
- `/51-percent-attack/` redirects to `/articles/51-percent-attack/`
- `/bitcoin-reformation/` redirects to `/articles/bitcoin-reformation/`
- An older episode that is not in the build yet
  (`site/zola/pending-episodes.txt`)
  is a page that says «Этот выпуск скоро будет опубликован.»
  and links to the main page
- An episode path with no such page,
  including episodes that have not been published,
  redirects to the main page
- Any other address is the 404 page:
  «Страница не найдена.» and a link to the main page.
  That includes `/suggest/` and `/feed/`.

## Kept pages

Settled 2026-10-26.

The about page shows the listener-review screenshot
saved at `site/zola/pages/about-screenshot.png`.

`/best-of-2020/` is one page made from the three published parts of «Лучшее» (2020).
WordPress announced four parts.
Part 4 is not on the site.
The old addresses redirect to `/best-of-2020/`:

- `/best-of-basic-block-1/`
- `/базовый-блок-лучшее-часть-2-из-4/`
- `/базовый-блок-лучшее-часть-3-из-4/`

`/bb-bonus-rms/` and `/ep100an/` stay at those addresses.
They are not in the menu.

### Stallman videos

`/bb-bonus-rms/` offers two files that WordPress hosts today:

- `stallman.mp4`, 229 MB
- `stallman_hq.mp4`, 2.1 GB

The bonus page keeps those WordPress addresses for now.
These files stay out of git.

Moving them off WordPress is a later step, before WordPress stops serving uploads.
Copy them once onto the public host
at `/files/bb-bonus-rms/stallman.mp4` and `/files/bb-bonus-rms/stallman_hq.mp4`.
The bonus page then links to those paths.

A host that refuses a 2 GB file, or bills heavily for that download,
serves the same paths from Cloudflare R2.
R2 does not charge for egress, which matters for a 2 GB file.
Backblaze B2 is the same shape of store and does charge for egress.

## Articles

Settled 2026-10-26.
The section is «Статьи», at `/articles/`, and it is in the header menu.

- `/articles/flash-attacks/`
- `/articles/51-percent-attack/`
- `/articles/bitcoin-reformation/`

The old root addresses redirect there.
Images live in each article's `images/` folder,
numbered in the order they appear.
`images/sources.txt` records the filename, the caption, and the address the file was saved from.
The Bitcoin Reformation PDF and EPUB live in
`content/articles/bitcoin-reformation/files/`.

## Color

Settled 2026-10-26.
The site keeps its current fonts and its current colors.

## Historical credits

Catalog episodes include guest names taken from the episode title.
When every name in that title is a regular host and the title names no organization, those names are filed as hosts.
The other catalog episodes have an empty host list.
Companies named in the title stay in the show notes.
The review list covers guest names and hosts.

`content/people/historical-review.csv` is the working list for this pass.
Each row is one episode.
`guests` and `hosts` hold names taken from the title.
A blank name cell means the title yielded no name on that side.
`guests status` and `hosts status` stay empty until review.
`OK` in a status cell means that side is reviewed.
A row is finished when both status cells are `OK`.
The pass corrects guest names that came from the title and fills in the host of each episode.

## Cutover

1. Episodes before 200 are in the build as `catalog`.
   Guest names are the title guess recorded in `content/people/historical-review.csv`.
   Host names for those episodes are still part of that review.
2. The articles section is already in the build,
   including redirects from the old root addresses.
3. The bonus page still links to the WordPress copies of
   `stallman.mp4` and `stallman_hq.mp4`.
   Moving those files is a later step, before WordPress stops serving uploads.
4. Build the static site and serve it at basicblockradio.com.
5. Retire WordPress as the public host.
   The build already includes the address redirects, the soon pages, and the 404.
