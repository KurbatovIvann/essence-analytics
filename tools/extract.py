#!/usr/bin/env python3
"""Build data/classes.json from the public Essence.game wiki API.

Usage:
  python3 tools/extract.py --cache .cache/wiki          # use cached JSON, fetch what is missing
  python3 tools/extract.py --cache .cache/wiki --icons  # also download skill icons

Cache layout: <cache>/cls/<slug>.json (UA), cls_en/, cls_ru/, tip/<id>_<lvl>.json
The wiki rate-limits aggressively, so requests are spaced out and cached.
"""
import argparse, glob, json, os, re, sys, time, urllib.request

API = "https://essence.game/wiki/api/v2/public"
UA_HDR = {"User-Agent": "Mozilla/5.0 (essence-analytics fan site)"}
CAP = 84
BOOK = {"Улучшенная Книга Заклинаний": 1, "Исключительная Книга Заклинаний": 2, "Редкая Книга Заклинаний": 3}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Race order and per-race class order shown on the site
RACES = ["human", "elf", "dark-elf", "orc", "dwarf", "kamael", "sylph", "high-elf"]


def get(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        with open(path, "rb") as f:
            raw = f.read()
        if raw[:1] in (b"{", b"["):
            return json.loads(raw)
    time.sleep(1.5)
    req = urllib.request.Request(url, headers=UA_HDR)
    raw = urllib.request.urlopen(req, timeout=30).read()
    if raw[:1] not in (b"{", b"["):
        raise RuntimeError(f"not JSON (rate limit?): {url}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(raw)
    return json.loads(raw)


def clean(html):
    x = re.sub(r"<br>\s*", "\n", html or "")
    x = re.sub(r"<[^>]+>", "", x)
    return x.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&amp;", "&")


def power_hits(desc):
    d = clean(desc)
    m = re.search(r"Мощность ([\d ]+)", d)
    pw = int(m.group(1).replace(" ", "")) if m else None
    hits = 1
    m2 = re.search(r"(\d) раза|дважды|Трижды|трижды", d)
    if m2:
        t = m2.group(0).lower()
        hits = 2 if t == "дважды" else 3 if t == "трижды" else int(m2.group(1))
    m3 = re.search(r"В PvE: атакует не более (\d+) цел", d)
    lim = int(m3.group(1)) if m3 else None
    return pw, hits, lim


def icon_name(url):
    return os.path.splitext(url.rsplit("/", 1)[-1].split("?")[0])[0] + ".webp" if url else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=os.path.join(ROOT, ".cache/wiki"))
    ap.add_argument("--icons", action="store_true")
    a = ap.parse_args()
    C = a.cache

    tree = {l: get(f"{API}/classes" + ("" if l == "ua" else f"?lang={l}"),
                   f"{C}/classes{'' if l == 'ua' else '_' + l}.json") for l in ("ua", "en", "ru")}
    race_names = {r["slug"]: {l: next(x["name"] for x in tree[l] if x["slug"] == r["slug"]) for l in tree}
                  for r in tree["ua"]}

    def leaves(node, out):
        if not node.get("children"):
            out.append(node["slug"])
        for ch in node.get("children", []):
            leaves(ch, out)
        return out

    order = []
    for r in tree["ua"]:
        for b in r["bases"]:
            for s in leaves(b, []):
                order.append((r["slug"], s))

    cmp = {}
    cmp_path = os.path.join(ROOT, "data/compare_seed.json")
    if os.path.exists(cmp_path):
        cmp = json.load(open(cmp_path))

    classes, icons = [], set()
    for race, slug in order:
        d = {l: get(f"{API}/classes/{slug}" + ("" if l == "ua" else f"?lang={l}"),
                    f"{C}/cls{'' if l == 'ua' else '_' + l}/{slug}.json") for l in ("ua", "en", "ru")}
        ua = d["ua"]
        sk_names = {l: {s["id"]: s["name"] for s in d[l]["skills"]} for l in d}

        def nm(sid, fallback):
            return {"ua": sk_names["ua"].get(sid, fallback), "en": sk_names["en"].get(sid, fallback),
                    "ru": sk_names["ru"].get(sid, fallback)}

        key, books = [], {1: [], 2: [], 3: []}
        for s in ua["skills"]:
            lv = [l for l in s["levels"] if l["charLevel"] <= CAP]
            if not lv:
                continue
            # books needed up to the cap
            for l in lv:
                for it in l.get("items") or []:
                    g = BOOK.get(it["main"]["name"])
                    if g:
                        books[g].append({"id": s["id"], "name": nm(s["id"], s["name"]), "level": l["level"],
                                         "charLevel": l["charLevel"], "kind": s["kind"], "category": s["category"],
                                         "icon": icon_name(s["icon"])})
                        icons.add(s["icon"])
            if s["kind"] != "active" or s["category"] != "attack" or s["grade"] >= 4:
                continue
            L = lv[-1]
            if L["charLevel"] < 70:  # stopped levelling long before the cap — not a real stage-1 skill
                continue
            pw, hits, lim = power_hits(L["desc"])
            if not pw:
                continue
            tip = None
            tp = f"{C}/tip/{s['id']}_{L['level']}.json"
            # cooldown / MP / targeting barely change between levels: any cached level will do
            cached = sorted(glob.glob(f"{C}/tip/{s['id']}_*.json"))
            try:
                tip = get(f"{API}/tip/skill/{s['id']}/{L['level']}", tp) if not cached or os.path.exists(tp) else json.load(open(cached[-1]))
            except Exception as e:  # rate limit — keep going with what we have
                print("tip miss", s["id"], e, file=sys.stderr)
            tg = (tip or {}).get("targeting") or {}
            key.append({
                "id": s["id"], "name": nm(s["id"], s["name"]), "icon": icon_name(s["icon"]),
                "grade": max(l["grade"] or 0 for l in lv), "level": L["level"], "top": s["topLevel"],
                "power": pw, "hits": hits,
                "targets": lim or tg.get("limit") or (1 if tg.get("shape") == "single" else None),
                "cd": (tip or {}).get("reuseDelay"), "mp": (tip or {}).get("mpConsume"),
                "ore": ((tip or {}).get("consume") or {}).get("count") if isinstance((tip or {}).get("consume"), dict) else None,
            })
            icons.add(s["icon"])
        # dedupe book lists: one row per skill per grade, keep highest level
        for g in books:
            seen = {}
            for b in books[g]:
                seen.setdefault(b["id"], {**b, "count": 0})
                seen[b["id"]]["count"] += 1
                seen[b["id"]]["level"] = max(seen[b["id"]]["level"], b["level"])
            books[g] = list(seen.values())
        key.sort(key=lambda k: ((k["cd"] or 99999) > 1500, -(k["power"] or 0) * k["hits"]))
        c = {
            "slug": slug, "race": race, "arch": ua["cls"]["archetype"],
            "name": {l: d[l]["cls"]["name"] for l in d},
            "chain": {l: [x["name"] for x in d[l]["chain"][:-1]] for l in d},
            "icon": f"{slug}.webp",
            "key": key[:8],
            "books": {str(g): books[g] for g in books},
            "bookCount": {str(g): sum(b["count"] for b in books[g]) for g in books},
        }
        if slug in cmp:
            # names in the seed are the wiki's RU skill names; localise them via skill ids
            idx = {l: {} for l in d}
            for l in d:
                for sk in d[l]["skills"]:
                    idx[l][sk["id"]] = (sk["name"], sk["icon"])
                    for r in sk.get("reps") or []:
                        idx[l].setdefault(r["replacement"]["id"], (r["replacement"]["name"], r["replacement"]["icon"]))
                    for lvl in sk["levels"]:
                        idx[l].setdefault(sk["id"], (lvl["name"], sk["icon"]))
            by_name = {}
            for sid, (n, ic) in idx["ua"].items():
                by_name.setdefault(n, sid)
            for k in ("spam", "aoe"):
                v = cmp[slug].get(k)
                if not v:
                    continue
                v = dict(v)
                sid = by_name.get(v["name"])
                if sid is None:
                    for sk in d["ua"]["skills"]:
                        for lvl in sk["levels"]:
                            if lvl["name"] == v["name"]:
                                sid = sk["id"]
                if sid is not None:
                    v["names"] = {l: (idx[l].get(sid) or (v["name"], None))[0] for l in d}
                    v["icon"] = icon_name(idx["ua"][sid][1])
                    icons.add(idx["ua"][sid][1])
                else:
                    v["names"] = {l: v["name"] for l in d}
                c[k] = v
        classes.append(c)

    out = {"cap": CAP, "races": [{"slug": r, "name": race_names[r]} for r in RACES if r in race_names],
           "classes": classes}
    with open(os.path.join(ROOT, "data/classes.json"), "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(len(classes), "classes,", len(icons), "skill icons")

    if a.icons:
        dst = os.path.join(ROOT, "assets/icons/skills")
        os.makedirs(dst, exist_ok=True)
        for u in sorted(icons):
            p = os.path.join(dst, icon_name(u))
            if os.path.exists(p):
                continue
            time.sleep(0.3)
            try:
                raw = urllib.request.urlopen(urllib.request.Request(u, headers=UA_HDR), timeout=30).read()
                open(p, "wb").write(raw)
            except Exception as e:
                print("icon miss", u, e, file=sys.stderr)


if __name__ == "__main__":
    main()
