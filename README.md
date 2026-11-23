# news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/aikogansduniaakhirat/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/aikogansduniaakhirat/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

A newspaper front page for Monday 23 November 2026: the date set large, a world
map with one numbered pin per story, six leads and a strip of further headlines.

## The day it shows

| # | Story | Where |
|---|---|---|
| 1 | COP31 closes without a final text; ministers trade blame | Antalya, Turkey |
| 2 | Seoul shares open 2.8% lower as AI-bubble fears spread | Seoul, South Korea |
| 3 | Kataib Hezbollah commander denies terrorism charges in court | New York, USA |
| 4 | Supercell storm wipes out Tupancireta; five dead, 250 hurt | Rio Grande do Sul, Brazil |
| 5 | Cameroon's former rebels say reintegration promises went unmet | Yaounde, Cameroon |
| 6 | Molly Meldrum, host of *Countdown*, dies aged 83 | Melbourne, Australia |

Also on the page: Kim Jong Un says Pyongyang seeks no regional dominance ·
Paolo Bulgari dies at 89 · Poundland days from administration · UK energy bills
to soar · Alcaraz wins the ATP Finals · Ateez take a fourth US No. 1.

Every line above comes from a feed item whose own `pubDate` is 23 November 2026
in UTC or in the reporting desk's local clock, which the bounty's rules allow.
The COP31 collapse itself fell on the 22nd, so that card carries the 23rd's
development — the recriminations between ministers — rather than restating the
collapse as if it happened that morning.

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
