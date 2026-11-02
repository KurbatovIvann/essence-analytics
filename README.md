# Essence analytics

Unofficial fan analytics for the Essence.game Lineage 2 Essence server: class data for stage 1 (cap 84), a forecast tier list and our own measurements from the open beta (OBT) onward. UA / EN / RU.

Not affiliated with the Essence.game administration. Game data comes from the public [Essence.game wiki](https://ua.essence.game/wiki/).

## How it works

```
data/classes.json            generated from the wiki by tools/extract.py
data/tiers.json              tier list (forecast until OBT measurements exist)
data/zones.json              open zones, measurement spots, key dates
data/measurements/farm.json  farming measurements (one object per test)
data/measurements/tower.json Boss Tower attempts
tools/build.py               renders everything into dist/
```

Every push to `main` rebuilds the site and deploys it to GitHub Pages (`.github/workflows/pages.yml`).

Local preview:

```
python3 tools/build.py
python3 -m http.server -d dist 8000
```

Refresh class data from the wiki (slow — the wiki rate-limits, so requests are spaced out and cached in `.cache/`):

```
python3 tools/extract.py --icons
```

## Measurement format

`data/measurements/farm.json`:

```json
{
  "id": "2026-11-06-sb-dd83-3",
  "date": "2026-11-06",
  "by": "nickname",
  "class": "storm_blaster",
  "gs": 18400,
  "books": {"1": ["..."], "2": ["..."], "3": ["..."]},
  "spot": "ДД83",
  "minutes": 3,
  "kills": 74,
  "exp": 123456789,
  "exp_pct": 1.23,
  "adena": 120000,
  "lcoin": 2590,
  "shards": {"a": 0, "legacy": 0, "epic": 0},
  "drops": "",
  "ore": 0,
  "mana_idle_s": 0,
  "deaths": 0,
  "crowd": "none",
  "stream": "",
  "note": ""
}
```

Spots: `ДД83`, `СМ84`, `ГЖ85`. Per-hour values are calculated at build time.

`data/measurements/tower.json`:

```json
{"date": "2026-11-06", "by": "nickname", "class": "storm_blaster", "gs": 18400, "floor": 5,
 "difficulty": "hard", "win": true, "time_left": 12, "boss_hp_pct": 0, "hp_lost": 35, "note": ""}
```
