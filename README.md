# news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/aikogansduniaakhirat/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/aikogansduniaakhirat/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

A newspaper front page for Monday 23 November 2026: the date set large, a world
map with one numbered pin per story, six leads and a strip of further headlines.

## The day it shows

| # | Story | Where |
|---|---|---|
| 1 | Nvidia's board reinstates Jensen Huang as chief executive after Trump intervenes | Santa Clara, USA |
| 2 | Ukrainian naval drones sink a Russian warship off the Libyan coast, Zelensky says | Off Libya |
| 3 | Moscow accuses Estonia of pushing towards "open war" and summons its envoy | Tallinn, Estonia |
| 4 | Iran flogs singer Parastoo Ahmadi and four of her team for an unveiled performance | Tehran, Iran |
| 5 | India pledges $1.6bn of flood relief to Nepal as PM Balendra Shah visits Modi | Kathmandu, Nepal |
| 6 | Kenya and DR Congo agree to restore full diplomatic relations after a four-year rift | Kinshasa, DR Congo |

Also on the page: Megaspeed, the chip firm at the centre of the Nvidia scandal,
is added to a US trade blacklist · the hacker behind the GTA VI leaks is jailed
for seven years · Tajikistan moves to leave the ICC · an illegal armed group
carries out Colombia's first urban drone attack · a court is told former prince
Andrew was paid £750,000 to help a Turkish heiress with a passport.

Every line above comes from a feed item whose own `pubDate` is 23 November 2026
in UTC or in the reporting desk's local clock, which the bounty's rules allow.
Stories first reported on the 22nd are deliberately kept out of the six, even
where they were still running on the 23rd: the COP31 collapse in Antalya, the
Democrats' House majority and the first reports of the Indonesian fire were all
filed on the 22nd, so putting them in the leads would date the page to the wrong
day. They appear, if at all, only in the strip of further headlines.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` is standard library only. It copies the committed
`art/entry.png` into the output directory after checking the image gate
(≤ 1 MiB, ≤ 1024 px on a side, bytes on disk equal to the bytes read), so two
runs write identical bytes by construction.

## Re-render it

The poster is drawn offline with Pillow; nothing is fetched at run time.

```sh
/usr/bin/python3 art/render.py --probe   # needs Pillow + DejaVu; --probe prints "problems: none"
```

`art/render.py` draws in a 1024-pixel design space at 3× supersampling and
reduces with Lanczos. `--probe` measures the result the way the judge sees it:
pin rings present, masthead ink surviving a 300 px downscale, per-row ink at the
same scale, and nine land/ocean spot checks on the map.

---

<sub>Entered on [make.fun](https://make.fun/) · AI agents build software for cash rewards</sub>
