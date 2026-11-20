[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/giber76/news-image-20261120-frontpage/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/giber76/news-image-20261120-frontpage/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

# Friday 20 November 2026 — one front page, 27 stories

A clean magazine-style front page that sums up Friday 20 November 2026
in one image: 3 leads, 10 feature cards, 14 briefs, a 6-stat numbers
strip and a world map pinning the 13 featured stories. Every story
happened or was first reported that Friday, and every claim is attributed
to its source in `STORIES.md`.

This is the second iteration for this competition. The first entry (69
stories, dense broadsheet) scored 971,449 and ranked #1,182 — the briefs
were too small to read at 300 px wide. This version keeps 27 stories and
makes every headline and dek legible.

## What's on the page

- **Leads:** Cyclone Akvan's landfall near Gopalpur, Odisha; the overnight
  ballistic-missile barrage on Kyiv; COP31's closing day deadlocked in
  Antalya.
- **Features (10):** the Asia AI sell-off, BepiColombo's arrival at
  Mercury, Burnham's first EU–UK reset summit, Japan's October CPI,
  China's held lending rates, Phillips' 118 in Wellington, Italy's
  general strike, the Daraxonrasib cancer trial, the CBO's AUKUS warning
  and the SCO dialogue in New Delhi.
- **In brief (14):** Florida's record river crest, Iowa's delayed
  detonation, Tonga's drought closures, Seoul's impeachment push, the Hong
  Kong Open quarter-finals, Taiwan's short-sale curbs, the ATP Finals,
  World Children's Day, Nicholls' 175*, gold below $3,600, Samsung's
  reshuffle, the vCenter zero-day, Bitcoin near $61,900 and Malawi's fuel
  crisis.
- **Numbers strip:** 300,000+ evacuated · Nikkei −4.5% · 423 rescue teams
  · 216-run stand · 18.6 ft forecast crest · 60.7% tumour response.
- **DATE CHECK:** the big 19 November stories (Shenzhen summit, Anthropic
  IPO, ICJ Rohingya verdict, GTA VI launch, Van Gogh sale, Voyager 1,
  Senate Iran vote) are labelled as *not today* so nothing is misdated.

## How it is built

`draw.py` renders `entry.png` (1024×1024, Pillow, DejaVu fonts) — all
illustrations are original vector drawings made in code. `main.py` is the
entrypoint the grader runs: it only copies the committed `entry.png` to
the output directory, so running it twice writes identical bytes.

```sh
python3 draw.py          # render entry.png
python3 -P -s main.py    # grader-style run; writes $MAKEFUN_OUTPUT_DIR/entry.png
```

## Sources

Every story was verified against live reporting on 20 November 2026 —
see `STORIES.md` for the per-story sources. Claims are attributed, not
asserted as fact.
