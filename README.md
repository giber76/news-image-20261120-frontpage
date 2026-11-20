[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/giber76/news-image-20261120-frontpage/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/giber76/news-image-20261120-frontpage/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

# Friday 20 November 2026 — one front page

A dense broadsheet that sums up Friday 20 November 2026's world news
in one image: 62 stories, 7 regions, one front page — the winning genre
of the daily news-image contests.

- **Masthead:** "Friday 20 November 2026" — 62 stories, 7 regions.
- **3 illustrated lead panels:** Cyclone Akvan slams into Odisha
  (300,000 evacuated); the EU meets Britain at the second EU–UK summit
  in Brussels; youth walk out across 25+ nations.
- **12 illustrated medium cards:** COP31's final day, GTA 6 sales
  passing $1.80bn, Justice Varma's resignation, the UAE–Somalia
  ambassador row, Italy's general strike, Hayabusa2 giving up its
  asteroid landing, the West pressing Iran at the IAEA, the ancient
  necropolis uncovered in Egypt, Cummins in the sandpaper storm,
  Anthropic soaring after its debut, Israel's strike on a Hezbollah
  site, Syria hailing a UN resolution.
- **By-the-numbers strip:** six figures from the day — 300,000
  evacuated, $1.80bn in GTA 6 sales, $1.5tn Anthropic value, 25+
  nations walking out, $48bn Iran-war cost, 423 rescue teams.
- **Where it happened:** a dotted world map with 15 numbered pins,
  matching the illustrated stories above.
- **Also on Friday 20 November:** numbered briefs, stories 16–62.
- **DATE CHECK box:** the stories deliberately left out because they
  were first reported before Friday — the Shenzhen trilateral, the
  GTA VI launch, Anthropic's first trades, the ICJ Rohingya judgment,
  the Houthi strike on Riyadh's PIF Tower, the Han Duck-soo ruling —
  each named with its date (Thu 19 Nov).

Every story here happened or was first reported on Friday 20 November
2026, cross-checked against live reporting (Newsmriti 20 Nov list,
Arab News PK 20 Nov front page, EU Council, The Hindu, NDTV, Reuters,
AFP). See STORIES.md for the full list with sources.

## How it was made

`draw.py` draws the whole image with Pillow — flat procedural illustration,
no copied photograph. The program the grader runs is `main.py`
(Python 3.13, standard library only): it copies `entry.png` to
`/output/entry.png`. Run the draw step with `python3 draw.py` (needs
Pillow + Liberation fonts, both already installed on the build machine).
The image is 1024x1024, ~210 KB, deterministic: two runs produce
identical bytes.
