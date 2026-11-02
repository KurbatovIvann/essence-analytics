#!/usr/bin/env python3
"""Render the static site into dist/ from data/*.json.

  python3 tools/build.py            # -> dist/
  python3 -m http.server -d dist    # preview at http://localhost:8000/
"""
import html, json, os, shutil, datetime
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
LANGS = ["ua", "en", "ru"]
HTML_LANG = {"ua": "uk", "en": "en", "ru": "ru"}
WIKI = {"ua": "https://ua.essence.game/wiki/", "en": "https://essence.game/wiki/", "ru": "https://ru.essence.game/wiki/"}
SPOT_ORDER = ["ДД83", "СМ84", "ГЖ85"]

T = {
 "ua": {
  "site": "Аналітика Essence", "nav_tiers": "Tier-листи", "nav_classes": "Класи", "nav_compare": "Порівняння",
  "nav_zones": "Локації", "nav_meas": "Заміри", "lang": "Мова", "menu": "Головне меню",
  "official": "Офіційні ресурси:", "o_site": "Сайт Essence.game", "o_wiki": "Вікі", "o_help": "Допомога",
  "o_tower": "Вежа Босів", "o_skills": "Уміння класів",
  "foot": "Неофіційна фан-сторінка. Не пов’язана з адміністрацією Essence.game.",
  "foot_data": "Дані: <a href=\"{wiki}\">вікі Essence.game</a> та власні заміри",
  "stage1": "Стадія 1", "cap": "Кап: 84 рівень", "books_to": "Книги: до 3★", "lcoin": "L-Coin з мобів: 105 000 / день",
  "meas_n": "Замірів: {n}", "updated": "Оновлено {d}",
  "tier_title": "Tier-лист · Стадія 1", "category": "Категорія", "forecast": "Прогноз до ОБТ",
  "tests": "тестів: {n}",
  "all_classes": "Усі класи", "search": "Пошук класу", "search_ph": "Наприклад, Снайпер", "nothing": "Нічого не знайдено",
  "zones_title": "Відкриті локації до 84", "all_zones": "Усі локації",
  "z_name": "Локація", "z_lvl": "Рівень", "z_hp": "HP моба", "z_exp": "Досвід / 1k HP", "z_adena": "Адена / 1k HP",
  "z_book": "Забута книга", "yes": "так",
  "latest": "Останні заміри", "no_meas": "Немає замірів. Початок — ОБТ, 06.11.", "dates": "Ключові дати",
  "stage_tab1": "Стадія 1 · до 84", "stage_tab2": "Стадія 2 · пізніше", "stage": "Стадія",
  "stage_note": "Без книг 4★ і 5★. Сила вмінь — на рівнях, доступних до 84.",
  "rating": "Рейтинг PvE · PvP · Вежа", "awaiting": "Очікує замірів ОБТ (з 06.11)",
  "class_wiki": "Клас у вікі", "fighter": "Воїн", "mage": "Маг",
  "key_skills": "Ключові вміння", "key_note": "Атакувальні вміння на рівнях до 84 · сила без модифікації · час удару базовий, без Швидк. Атк./Маг.",
  "k_skill": "Вміння", "k_hits": "Ударів", "k_targets": "Цілі", "k_cd": "Відкат", "k_hit": "Час удару", "k_mp": "MP", "k_book": "Книга",
  "k_power": "Сила", "k_pve": "Сила в PvE", "spam": "спам-удар", "replaces": "замінює звичайний удар після книги",
  "order": "Книги для класу", "order_note": "Усе, що потребує книг 1★–3★ до 84 рівня. Безкоштовні джерела до 26.11 проти потреби класу.",
  "have_of": "є {h} з {n}", "g1": "1★ Покращена", "g2": "2★ Виняткова", "g3": "3★ Рідкісна",
  "src1": "Джерела: календар 13.11 і 24.11, 78 рівень, Вежа (5 пов., Складна), рефералка",
  "src2": "Джерела: календар 15.11 і 25.11, 80 рівень, Вежа (10 пов.)",
  "src3": "Джерела: календар 17.11 і 26.11, 83 рівень. Решта — Особливе створення",
  "lvl": "рів.", "from_lvl": "з {l} рів.", "passive": "пасивне", "active": "активне", "nobooks": "Не потрібно",
  "measures": "Заміри", "meas_note": "Тести на 84 рівні, з усіма бафами і книгами першого дня. Середнє по всіх класах на тому ж споті — для порівняння.",
  "farm": "Фарм", "tower": "Вежа Босів", "m_spot": "Спот", "m_gs": "GS", "m_exp": "Досвід / год", "m_adena": "Адена / год",
  "m_lcoin": "L-Coin / год", "m_mobs": "Мобів / год", "m_vs": "vs середнє", "m_n": "Тестів",
  "m_floor": "Поверх", "m_diff": "Складність", "m_mings": "Мін. GS для перемоги", "m_left": "Залишок часу",
  "m_hp": "Втрачено HP", "m_res": "Результат", "win": "перемога", "loss": "поразка",
  "m_date": "Дата", "m_class": "Клас", "m_min": "Хв", "m_kills": "Вбито", "m_by": "Хто", "m_note": "Нотатки",
  "no_meas_short": "Немає замірів. Початок — 06.11.",
  "cmp_title": "Порівняння класів", "cmp_intro": "Вибери до трьох класів. Сила вмінь — з вікі на рівнях до 84, заміри — з ОБТ.",
  "cmp_pick": "Клас {n}", "cmp_skills": "Вміння на стадії 1", "cmp_race": "Раса", "cmp_spam": "Спам-удар",
  "cmp_pps": "Сила в PvE за 1 с", "cmp_cd": "відкат", "cmp_hit": "удар", "cmp_base": "база", "cmp_aoe": "Найсильніший AoE", "cmp_mp": "MP за спам-удар", "cmp_books": "Книги 1★ / 2★ / 3★",
  "cmp_mix": "Порівнюєш мага з воїном: сила маг. і фіз. умінь рахується по-різному, порівнюй усередині типу.",
  "cmp_meas": "Заміри на споті", "cmp_spot": "Спот", "targets_n": "{n} цілей",
  "zones_page": "Локації", "spots": "Споти для замірів", "sp_code": "Код", "sp_type": "Що перевіряє",
  "meas_page": "Заміри", "meas_method": "Як міряємо",
  "method": ["84 рівень, усі доступні бафи, книги першого дня сервера (13.11), автобій.",
             "Три тривалості: 1, 3 і 6 хвилин. Таймер — після першого вбитого моба.",
             "Споти: ДД83, СМ84, ГЖ85 — однакові для всіх класів.",
             "Показники перераховуються на годину; «vs середнє» — відносно всіх класів на тому ж споті."],
  "per_hour_note": "Значення на годину, перераховані з тривалості заміру.",
  "sec": "с", "min": "хв",
 },
 "en": {
  "site": "Essence analytics", "nav_tiers": "Tier lists", "nav_classes": "Classes", "nav_compare": "Compare",
  "nav_zones": "Zones", "nav_meas": "Measurements", "lang": "Language", "menu": "Main menu",
  "official": "Official resources:", "o_site": "Essence.game", "o_wiki": "Wiki", "o_help": "Help",
  "o_tower": "Boss Tower", "o_skills": "Class skills",
  "foot": "Unofficial fan page. Not affiliated with the Essence.game administration.",
  "foot_data": "Data: <a href=\"{wiki}\">Essence.game wiki</a> and our own measurements",
  "stage1": "Stage 1", "cap": "Cap: level 84", "books_to": "Books: up to 3★", "lcoin": "L-Coin from mobs: 105,000 / day",
  "meas_n": "Measurements: {n}", "updated": "Updated {d}",
  "tier_title": "Tier list · Stage 1", "category": "Category", "forecast": "Pre-OBT forecast",
  "tests": "tests: {n}",
  "all_classes": "All classes", "search": "Find a class", "search_ph": "e.g. Sagittarius", "nothing": "Nothing found",
  "zones_title": "Open zones up to 84", "all_zones": "All zones",
  "z_name": "Zone", "z_lvl": "Level", "z_hp": "Mob HP", "z_exp": "XP / 1k HP", "z_adena": "Adena / 1k HP",
  "z_book": "Forgotten book", "yes": "yes",
  "latest": "Latest measurements", "no_meas": "No measurements yet. They start with the OBT on 06.11.", "dates": "Key dates",
  "stage_tab1": "Stage 1 · up to 84", "stage_tab2": "Stage 2 · later", "stage": "Stage",
  "stage_note": "No 4★ or 5★ books. Skill power at the levels available before 84.",
  "rating": "PvE · PvP · Tower rating", "awaiting": "Waiting for OBT measurements (from 06.11)",
  "class_wiki": "Class on the wiki", "fighter": "Fighter", "mage": "Mage",
  "key_skills": "Key skills", "key_note": "Attack skills at levels up to 84 · power without modification · base cast time, before Atk./Casting Spd.",
  "k_skill": "Skill", "k_hits": "Hits", "k_targets": "Targets", "k_cd": "Cooldown", "k_hit": "Cast time", "k_mp": "MP", "k_book": "Book",
  "k_power": "Power", "k_pve": "PvE power", "spam": "spam skill", "replaces": "replaces the base skill after the book",
  "order": "Books for the class", "order_note": "Everything that needs 1★–3★ books up to level 84. Free sources until 26.11 vs. what the class needs.",
  "have_of": "{h} of {n} available", "g1": "1★ Improved", "g2": "2★ Exceptional", "g3": "3★ Rare",
  "src1": "Sources: calendar 13.11 and 24.11, level 78, Tower (floor 5, Hard), referrals",
  "src2": "Sources: calendar 15.11 and 25.11, level 80, Tower (floor 10)",
  "src3": "Sources: calendar 17.11 and 26.11, level 83. The rest — Special Crafting",
  "lvl": "lv.", "from_lvl": "from lv. {l}", "passive": "passive", "active": "active", "nobooks": "Not needed",
  "measures": "Measurements", "meas_note": "Tests at level 84 with all buffs and day-one books. The average of all classes on the same spot is shown for comparison.",
  "farm": "Farming", "tower": "Boss Tower", "m_spot": "Spot", "m_gs": "GS", "m_exp": "XP / h", "m_adena": "Adena / h",
  "m_lcoin": "L-Coin / h", "m_mobs": "Mobs / h", "m_vs": "vs average", "m_n": "Tests",
  "m_floor": "Floor", "m_diff": "Difficulty", "m_mings": "Min. GS to win", "m_left": "Time left",
  "m_hp": "HP lost", "m_res": "Result", "win": "win", "loss": "loss",
  "m_date": "Date", "m_class": "Class", "m_min": "Min", "m_kills": "Kills", "m_by": "By", "m_note": "Notes",
  "no_meas_short": "No measurements yet. Start — 06.11.",
  "cmp_title": "Compare classes", "cmp_intro": "Pick up to three classes. Skill power is from the wiki at levels up to 84; measurements come from the OBT.",
  "cmp_pick": "Class {n}", "cmp_skills": "Skills in stage 1", "cmp_race": "Race", "cmp_spam": "Spam skill",
  "cmp_pps": "PvE power per second", "cmp_cd": "cooldown", "cmp_hit": "cast", "cmp_base": "base", "cmp_aoe": "Strongest AoE", "cmp_mp": "MP per spam skill", "cmp_books": "Books 1★ / 2★ / 3★",
  "cmp_mix": "You are comparing a mage with a fighter: magic and physical power scale differently, so compare within one type.",
  "cmp_meas": "Measurements on a spot", "cmp_spot": "Spot", "targets_n": "{n} targets",
  "zones_page": "Zones", "spots": "Measurement spots", "sp_code": "Code", "sp_type": "What it tests",
  "meas_page": "Measurements", "meas_method": "How we measure",
  "method": ["Level 84, all available buffs, books available on server day one (13.11), auto-hunt.",
             "Three durations: 1, 3 and 6 minutes. The timer starts after the first kill.",
             "Spots: ДД83, СМ84, ГЖ85 — the same for every class.",
             "Values are converted to per hour; “vs average” is relative to all classes on the same spot."],
  "per_hour_note": "Per-hour values converted from the measurement duration.",
  "sec": "s", "min": "min",
 },
 "ru": {
  "site": "Аналитика Essence", "nav_tiers": "Тир-листы", "nav_classes": "Классы", "nav_compare": "Сравнение",
  "nav_zones": "Локации", "nav_meas": "Замеры", "lang": "Язык", "menu": "Главное меню",
  "official": "Официальные ресурсы:", "o_site": "Сайт Essence.game", "o_wiki": "Вики", "o_help": "Помощь",
  "o_tower": "Башня Боссов", "o_skills": "Умения классов",
  "foot": "Неофициальная фан-страница. Не связана с администрацией Essence.game.",
  "foot_data": "Данные: <a href=\"{wiki}\">вики Essence.game</a> и собственные замеры",
  "stage1": "Стадия 1", "cap": "Кап: 84 уровень", "books_to": "Книги: до 3★", "lcoin": "L-Coin с мобов: 105 000 / день",
  "meas_n": "Замеров: {n}", "updated": "Обновлено {d}",
  "tier_title": "Тир-лист · Стадия 1", "category": "Категория", "forecast": "Прогноз до ОБТ",
  "tests": "тестов: {n}",
  "all_classes": "Все классы", "search": "Поиск класса", "search_ph": "Например, Снайпер", "nothing": "Ничего не найдено",
  "zones_title": "Открытые локации до 84", "all_zones": "Все локации",
  "z_name": "Локация", "z_lvl": "Уровень", "z_hp": "HP моба", "z_exp": "Опыт / 1k HP", "z_adena": "Адена / 1k HP",
  "z_book": "Забытая книга", "yes": "да",
  "latest": "Последние замеры", "no_meas": "Замеров нет. Начало — ОБТ, 06.11.", "dates": "Ключевые даты",
  "stage_tab1": "Стадия 1 · до 84", "stage_tab2": "Стадия 2 · позже", "stage": "Стадия",
  "stage_note": "Без книг 4★ и 5★. Сила умений — на уровнях, доступных до 84.",
  "rating": "Рейтинг PvE · PvP · Башня", "awaiting": "Ждёт замеров ОБТ (с 06.11)",
  "class_wiki": "Класс в вики", "fighter": "Воин", "mage": "Маг",
  "key_skills": "Ключевые умения", "key_note": "Атакующие умения на уровнях до 84 · сила без модификации · время удара базовое, без Скор. Атк./Маг.",
  "k_skill": "Умение", "k_hits": "Ударов", "k_targets": "Цели", "k_cd": "Откат", "k_hit": "Время удара", "k_mp": "MP", "k_book": "Книга",
  "k_power": "Сила", "k_pve": "Сила в PvE", "spam": "спам-удар", "replaces": "заменяет обычный удар после книги",
  "order": "Книги для класса", "order_note": "Всё, что требует книг 1★–3★ до 84 уровня. Бесплатные источники до 26.11 против потребности класса.",
  "have_of": "есть {h} из {n}", "g1": "1★ Улучшенная", "g2": "2★ Исключительная", "g3": "3★ Редкая",
  "src1": "Источники: календарь 13.11 и 24.11, 78 уровень, Башня (5 эт., Сложная), рефералка",
  "src2": "Источники: календарь 15.11 и 25.11, 80 уровень, Башня (10 эт.)",
  "src3": "Источники: календарь 17.11 и 26.11, 83 уровень. Остальное — Особое создание",
  "lvl": "ур.", "from_lvl": "с {l} ур.", "passive": "пассивное", "active": "активное", "nobooks": "Не нужно",
  "measures": "Замеры", "meas_note": "Тесты на 84 уровне, со всеми баффами и книгами первого дня. Среднее по всем классам на том же споте — для сравнения.",
  "farm": "Фарм", "tower": "Башня Боссов", "m_spot": "Спот", "m_gs": "GS", "m_exp": "Опыт / ч", "m_adena": "Адена / ч",
  "m_lcoin": "L-Coin / ч", "m_mobs": "Мобов / ч", "m_vs": "vs среднее", "m_n": "Тестов",
  "m_floor": "Этаж", "m_diff": "Сложность", "m_mings": "Мин. GS для победы", "m_left": "Осталось времени",
  "m_hp": "Потеряно HP", "m_res": "Результат", "win": "победа", "loss": "поражение",
  "m_date": "Дата", "m_class": "Класс", "m_min": "Мин", "m_kills": "Убито", "m_by": "Кто", "m_note": "Заметки",
  "no_meas_short": "Замеров нет. Начало — 06.11.",
  "cmp_title": "Сравнение классов", "cmp_intro": "Выбери до трёх классов. Сила умений — из вики на уровнях до 84, замеры — с ОБТ.",
  "cmp_pick": "Класс {n}", "cmp_skills": "Умения на стадии 1", "cmp_race": "Раса", "cmp_spam": "Спам-удар",
  "cmp_pps": "Сила в PvE за 1 с", "cmp_cd": "откат", "cmp_hit": "удар", "cmp_base": "база", "cmp_aoe": "Сильнейший AoE", "cmp_mp": "MP за спам-удар", "cmp_books": "Книги 1★ / 2★ / 3★",
  "cmp_mix": "Сравниваешь мага с воином: сила маг. и физ. умений считается по-разному, сравнивай внутри типа.",
  "cmp_meas": "Замеры на споте", "cmp_spot": "Спот", "targets_n": "{n} целей",
  "zones_page": "Локации", "spots": "Споты для замеров", "sp_code": "Код", "sp_type": "Что проверяет",
  "meas_page": "Замеры", "meas_method": "Как меряем",
  "method": ["84 уровень, все доступные баффы, книги первого дня сервера (13.11), автобой.",
             "Три длительности: 1, 3 и 6 минут. Таймер — после первого убитого моба.",
             "Споты: ДД83, СМ84, ГЖ85 — одинаковые для всех классов.",
             "Показатели пересчитываются на час; «vs среднее» — относительно всех классов на том же споте."],
  "per_hour_note": "Значения в час, пересчитанные из длительности замера.",
  "sec": "с", "min": "мин",
 },
}
# free book sources until 26.11 (calendar + level rewards + tower + referral)
FREE_BOOKS = {"1": 7, "2": 4, "3": 3}

e = html.escape


def load(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return json.load(f)


def num(v, lang, dec=0):
    if v is None:
        return "—"
    s = f"{v:,.{dec}f}"
    if lang == "en":
        return s
    return s.replace(",", " ").replace(".", ",")


def write(path, text):
    full = os.path.join(DIST, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)


# ---------------------------------------------------------------- data
DATA = load("data/classes.json")
CLASSES = DATA["classes"]
BY = {c["slug"]: c for c in CLASSES}
RACE = {r["slug"]: r["name"] for r in DATA["races"]}
TIERS = load("data/tiers.json")
ZONES = load("data/zones.json")
FARM = load("data/measurements/farm.json")
TOWER = load("data/measurements/tower.json")
TODAY = datetime.date.today().strftime("%d.%m.%Y")


def per_hour(m, k):
    v = m.get(k)
    return None if v is None or not m.get("minutes") else v * 60.0 / m["minutes"]


def farm_agg():
    """class -> spot -> aggregated per-hour values; spot -> average mobs/h across classes."""
    agg = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for m in FARM:
        for k in ("exp", "adena", "lcoin", "kills"):
            v = per_hour(m, k)
            if v is not None:
                agg[m["class"]][m["spot"]][k].append(v)
        agg[m["class"]][m["spot"]]["gs"].append(m.get("gs"))
    out = {}
    for c, spots in agg.items():
        out[c] = {}
        for s, vals in spots.items():
            out[c][s] = {k: (sum(x for x in v if x is not None) / max(1, len([x for x in v if x is not None]))
                             if any(x is not None for x in v) else None) for k, v in vals.items()}
            out[c][s]["n"] = len(vals["gs"])
    spot_avg = {}
    for s in SPOT_ORDER + sorted({m["spot"] for m in FARM} - set(SPOT_ORDER)):
        vals = [out[c][s]["kills"] for c in out if s in out[c] and out[c][s].get("kills")]
        spot_avg[s] = sum(vals) / len(vals) if vals else None
    return out, spot_avg


AGG, SPOT_AVG = farm_agg()


# ---------------------------------------------------------------- layout
def page(lang, rel, key, path_in_lang, title, body, scripts=""):
    t = T[lang]
    nav = [("tiers", "", t["nav_tiers"]), ("classes", "#classes", t["nav_classes"]),
           ("compare", "compare/", t["nav_compare"]), ("zones", "zones/", t["nav_zones"]),
           ("meas", "measurements/", t["nav_meas"])]
    navh = "".join(
        f'<a href="{rel}{lang}/{h}"{" aria-current=\"page\"" if k == key else ""}>{e(lbl)}</a>' for k, h, lbl in nav)
    langs = "".join(
        f'<a href="{rel}{l}/{path_in_lang}" hreflang="{HTML_LANG[l]}"{" aria-current=\"true\"" if l == lang else ""}>{l.upper()}</a>'
        for l in LANGS)
    w = WIKI[lang]
    alts = "".join(f'<link rel="alternate" hreflang="{HTML_LANG[l]}" href="{rel}{l}/{path_in_lang}">' for l in LANGS)
    return f"""<!doctype html>
<html lang="{HTML_LANG[lang]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} — {e(t['site'])}</title>
<meta name="description" content="{e(t['foot'])}">
{alts}
<link rel="icon" href="{rel}assets/icons/classes/storm_blaster.webp">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel}assets/css/site.css">
</head>
<body>
<header class="site-head">
<div class="wrap head-row">
<nav class="nav" aria-label="{e(t['menu'])}">{navh}</nav>
<div class="langs" role="group" aria-label="{e(t['lang'])}">{langs}</div>
</div>
<div class="official"><div class="wrap">
<span>{e(t['official'])}</span>
<a href="https://essence.game/">{e(t['o_site'])}</a>
<a href="{w}">{e(t['o_wiki'])}</a>
<a href="https://essence.game/help">{e(t['o_help'])}</a>
<a href="{w}boss-tower">{e(t['o_tower'])}</a>
<a href="{w}skills">{e(t['o_skills'])}</a>
</div></div>
</header>
<main>
{body}
</main>
<footer class="site-foot"><div class="wrap">
<span>{e(t['foot'])}</span>
<span>{t['foot_data'].format(wiki=w)}</span>
</div></footer>
{scripts}
</body>
</html>
"""


def icon(rel, slug, size=40):
    return f'<img class="ico" src="{rel}assets/icons/classes/{slug}.webp" alt="" width="{size}" height="{size}" loading="lazy">'


def sk_icon(rel, name, size=36):
    if not name or not os.path.exists(os.path.join(ROOT, "assets/icons/skills", name)):
        return f'<span class="ico" style="width:{size}px;height:{size}px"></span>'
    return f'<img class="ico" src="{rel}assets/icons/skills/{name}" alt="" width="{size}" height="{size}" loading="lazy">'


def grade_badge(g):
    return f'<span class="g g{g}">{g}★</span>' if g in (1, 2, 3) else '<span class="g g0">—</span>'


def secs(ms, lang):
    if ms is None:
        return "—"
    s = ms / 1000.0
    return (num(s, lang, 2 if s < 1 else 0 if s == int(s) else 1)) + " " + T[lang]["sec"]


def total_meas():
    return len(FARM) + len(TOWER)


# ---------------------------------------------------------------- home
def home(lang):
    t, rel = T[lang], "../"
    strip = f"""<section class="wrap" style="padding-top:24px"><div class="strip">
<span><strong>{t['stage1']}</strong></span><span>{t['cap']}</span><span>{t['books_to']}</span>
<span>{t['lcoin']}</span><span>{t['meas_n'].format(n=total_meas())}</span>
<span class="muted">{t['updated'].format(d=TODAY)}</span></div></section>"""

    tabs, panels = [], []
    for i, (tid, tab) in enumerate(TIERS["tabs"].items()):
        sel = "true" if i == 0 else "false"
        tabs.append(f'<button type="button" role="tab" id="tab-{tid}" aria-controls="panel-{tid}" aria-selected="{sel}" data-tab="{tid}">{e(tab["label"][lang])}</button>')
        rows = []
        for tier, lst in tab["rows"]:
            chips = []
            for slug, why in lst:
                c = BY[slug]
                n = sum(v["n"] for v in AGG.get(slug, {}).values())
                extra = f' · {t["tests"].format(n=n)}' if n else ""
                chips.append(f'<a class="chip" href="{rel}{lang}/class/{slug}/">{icon(rel, slug)}<span><b>{e(c["name"][lang])}</b><small>{e(why[lang])}{extra}</small></span></a>')
            rows.append(f'<div class="tier"><div class="tier-badge tier-{tier}">{tier}</div><div class="tier-list">{"".join(chips)}</div></div>')
        panels.append(f'<div role="tabpanel" id="panel-{tid}" aria-labelledby="tab-{tid}"{"" if i == 0 else " hidden"}>'
                      f'<div class="tiers">{"".join(rows)}</div></div>')
    tiers = f"""<section class="wrap sec" id="tiers">
<div class="sec-head"><h1>{t['tier_title']}</h1>
<div class="tabs" role="tablist" aria-label="{e(t['category'])}">{"".join(tabs)}</div></div>
<div class="banner" style="margin-bottom:18px"><strong>{t['forecast']}</strong><span>{e(TIERS['note'][lang])}</span></div>
{"".join(panels)}
</section>"""

    races = []
    for r in DATA["races"]:
        items = "".join(
            f'<a href="{rel}{lang}/class/{c["slug"]}/" data-name="{e((c["name"]["ua"] + " " + c["name"]["en"] + " " + c["name"]["ru"]).lower())}">{icon(rel, c["slug"], 32)}<span>{e(c["name"][lang])}</span></a>'
            for c in CLASSES if c["race"] == r["slug"])
        races.append(f'<div class="race" data-race><div class="race-name">{e(r["name"][lang])}</div><div style="display:flex;flex-direction:column;gap:4px">{items}</div></div>')
    classes = f"""<section class="wrap sec" id="classes">
<div class="sec-head"><h2>{t['all_classes']}</h2>
<div class="search"><label for="cls-search">{t['search']}</label><input id="cls-search" type="search" placeholder="{e(t['search_ph'])}" autocomplete="off"></div></div>
<div class="empty" id="cls-empty" hidden>{t['nothing']}</div>
<div class="races">{"".join(races)}</div>
</section>"""

    latest = latest_block(lang, rel, 5)
    dates = "".join(f'<div><b>{d["d"]}</b><span>{e(d["t"][lang])}</span></div>' for d in ZONES["dates"])
    lower = f"""<section class="wrap sec"><div class="cols">
<div class="main panel">
<div style="display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:8px"><h2>{t['zones_title']}</h2><a href="{rel}{lang}/zones/">{t['all_zones']}</a></div>
<p class="muted small" style="margin:6px 0 16px">{e(ZONES['note'][lang])}</p>
{zones_table(lang)}
</div>
<div class="side">
<div class="panel"><h2 style="font-size:22px;margin-bottom:14px">{t['latest']}</h2>{latest}</div>
<div class="panel"><h2 style="font-size:22px;margin-bottom:14px">{t['dates']}</h2><div class="dates" style="display:flex;flex-direction:column;gap:8px;font-size:15px">{dates}</div></div>
</div></div></section>"""

    js = f'<script src="{rel}assets/js/home.js" defer></script>'
    return page(lang, rel, "tiers", "", t["tier_title"], strip + tiers + classes + lower, js)


def zones_table(lang):
    t = T[lang]
    mx = max(z["exp"] for z in ZONES["zones"])
    rows = "".join(f"""<tr><td style="font-weight:600">{e(z['name'][lang])}</td><td class="c2">{z['lvl']}</td><td class="c2 num">{z['hp']}</td>
<td><div style="display:flex;align-items:center;gap:10px"><span style="width:44px;text-align:right">{z['exp']}</span><span class="bar"><i style="width:{round(100 * z['exp'] / mx)}%"></i></span></div></td>
<td class="num">{z['adena'] if z['adena'] is not None else '—'}</td><td class="c2">{t['yes'] if z['book'] else '—'}</td></tr>""" for z in ZONES["zones"])
    return f"""<div class="tbl-wrap"><table style="min-width:560px"><thead><tr><th>{t['z_name']}</th><th>{t['z_lvl']}</th><th class="num">{t['z_hp']}</th><th>{t['z_exp']}</th><th class="num">{t['z_adena']}</th><th>{t['z_book']}</th></tr></thead><tbody>{rows}</tbody></table></div>"""


def latest_block(lang, rel, n):
    t = T[lang]
    if not FARM:
        return f'<div class="empty">{t["no_meas"]}</div>'
    items = sorted(FARM, key=lambda m: m.get("date", ""), reverse=True)[:n]
    rows = "".join(
        f'<a class="chip" style="flex:1 1 100%" href="{rel}{lang}/class/{m["class"]}/">{icon(rel, m["class"], 32)}<span><b>{e(BY[m["class"]]["name"][lang])}</b>'
        f'<small>{m["spot"]} · {m["minutes"]} {t["min"]} · GS {num(m.get("gs"), lang)} · {t["m_mobs"]}: {num(per_hour(m, "kills"), lang)}</small></span></a>'
        for m in items)
    return f'<div style="display:flex;flex-direction:column;gap:8px">{rows}</div>'


# ---------------------------------------------------------------- class page
def class_page(lang, c):
    t, rel = T[lang], "../../../"
    slug = c["slug"]
    chain = " → ".join(e(x) for x in c["chain"][lang])
    arch = t["mage"] if c["arch"] == "mage" else t["fighter"]
    hero = f"""<div class="wrap"><div class="crumbs"><a href="{rel}{lang}/#classes">{t['nav_classes']}</a> / {e(RACE[c['race']][lang])}</div>
<section class="hero">{icon(rel, slug, 88)}
<div style="flex:1 1 420px;min-width:0"><div class="muted small">{chain}</div><h1>{e(c['name'][lang])}</h1>
<div class="tags"><span class="tag">{arch}</span><span class="tag">{e(RACE[c['race']][lang])}</span><a href="{WIKI[lang]}skills/{slug}" style="padding:4px 10px">{t['class_wiki']}</a></div></div>
<div class="rating"><div class="muted" style="font-size:13px">{t['rating']}</div><div class="gold">{t['awaiting']}</div></div>
</section>
<div class="tabs" role="tablist" aria-label="{t['stage']}" style="display:inline-flex;margin:28px 0 6px">
<button type="button" role="tab" aria-selected="true">{t['stage_tab1']}</button><button type="button" role="tab" aria-selected="false" disabled style="color:var(--dim)">{t['stage_tab2']}</button></div>
<p class="muted small" style="margin:0 0 24px">{t['stage_note']}</p>"""

    # key skills
    rows = []
    spam = c.get("spam") or {}
    key_names = {k["name"]["ru"] for k in c["key"]}
    if spam and spam.get("name") and spam["name"] not in key_names:
        rows.append(f"""<tr><td><div class="skill">{sk_icon(rel, spam.get('icon'))}<div><b>{e(spam.get('names', {}).get(lang, spam['name']))}</b><small>{t['spam']}{(' · ' + e(spam['via'][lang])) if spam.get('via') else ''}</small></div></div></td>
<td class="num">{num(spam.get('power'), lang)}</td><td class="num">{num(spam.get('pve'), lang)}</td><td class="num gold">{spam.get('h', '—')}</td><td class="c2">{spam.get('lim') or 1}</td><td class="c2">{secs((spam.get('cd') or 0) * 1000, lang)}</td><td class="c2">{secs(spam.get('hit'), lang)}</td><td class="num c2">{spam.get('mp') or '—'}</td><td>{grade_badge(spam.get('book'))}</td></tr>""")
    for k in c["key"]:
        is_spam = spam.get("name") == k["name"]["ru"]
        note = (t["spam"] + " · " if is_spam else "") + f'{t["lvl"]} {k["level"]}/{k["top"]}'
        rows.append(f"""<tr><td><div class="skill">{sk_icon(rel, k['icon'])}<div><b>{e(k['name'][lang])}</b><small>{note}</small></div></div></td>
<td class="num">{num(k['power'], lang)}</td><td class="num">{num(k.get('pve') or k['power'], lang)}</td><td class="num gold">{k['hits']}</td><td class="c2">{k['targets'] or '—'}</td><td class="c2">{secs(k['cd'], lang)}</td><td class="c2">{secs(k.get('hit'), lang)}</td><td class="num c2">{k['mp'] or '—'}</td><td>{grade_badge(k['grade'])}</td></tr>""")
    skills = f"""<section class="panel" aria-labelledby="skills"><h2 id="skills">{t['key_skills']}</h2>
<p class="muted small" style="margin:4px 0 16px">{t['key_note']}</p>
<div class="tbl-wrap"><table style="min-width:700px"><thead><tr><th>{t['k_skill']}</th><th class="num">{t['k_power']}</th><th class="num">{t['k_pve']}</th><th class="num">{t['k_hits']}</th><th>{t['k_targets']}</th><th>{t['k_cd']}</th><th>{t['k_hit']}</th><th class="num">{t['k_mp']}</th><th>{t['k_book']}</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table></div></section>"""

    # books
    cols = []
    for g in ("1", "2", "3"):
        lst = sorted(c["books"][g], key=lambda b: (b["category"] != "attack", b["kind"] != "passive", b["charLevel"]))
        need = c["bookCount"][g]
        have = FREE_BOOKS[g]
        pct = min(100, round(100 * have / need)) if need else 100
        colr = "var(--gold)" if have >= need else "var(--amber)"
        items = "".join(
            f'<li><span>{i + 1}</span>{sk_icon(rel, b["icon"], 32)}<span><b>{e(b["name"][lang])}</b><small>{t["lvl"]} {b["level"]} · {t["from_lvl"].format(l=b["charLevel"])}{" · ×" + str(b["count"]) if b["count"] > 1 else ""}</small></span></li>'
            for i, b in enumerate(lst)) or f'<li class="muted">{t["nobooks"]}</li>'
        cols.append(f"""<div class="ocol"><div class="ocol-head"><span class="g g{g}">{t['g' + g]}</span><span class="small c2">{t['have_of'].format(h=have, n=need)}</span></div>
<div class="prog"><i style="width:{pct}%;background:{colr}"></i></div><ol>{items}</ol><div class="muted" style="margin-top:12px;font-size:13px">{t['src' + g]}</div></div>""")
    books = f"""<section class="panel" style="margin-top:24px" aria-labelledby="order"><h2 id="order">{t['order']}</h2>
<p class="muted small" style="margin:4px 0 18px">{t['order_note']}</p><div class="order">{"".join(cols)}</div></section>"""

    # measurements
    a = AGG.get(slug, {})
    if a:
        frows = []
        for s in sorted(a, key=lambda s: SPOT_ORDER.index(s) if s in SPOT_ORDER else 99):
            v = a[s]
            avg = SPOT_AVG.get(s)
            vs = f"{(v['kills'] / avg - 1) * 100:+.0f}%" if avg and v.get("kills") else "—"
            frows.append(f'<tr><td style="font-weight:600">{s}</td><td class="num">{num(v.get("gs"), lang)}</td><td class="num">{num(v.get("exp"), lang)}</td><td class="num">{num(v.get("adena"), lang)}</td><td class="num">{num(v.get("lcoin"), lang)}</td><td class="num">{num(v.get("kills"), lang)}</td><td class="num">{vs}</td><td class="num">{v["n"]}</td></tr>')
        fbody = "".join(frows)
    else:
        fbody = f'<tr><td colspan="8" class="muted" style="text-align:center;padding:20px 8px">{t["no_meas_short"]}</td></tr>'
    trs = [m for m in TOWER if m["class"] == slug]
    if trs:
        tbody = "".join(
            f'<tr><td>{m.get("floor")}</td><td>{e(str(m.get("difficulty", "—")))}</td><td>{t["win"] if m.get("win") else t["loss"]}</td><td class="num">{num(m.get("gs"), lang)}</td><td class="num">{m.get("time_left", "—")}</td><td class="num">{m.get("hp_lost", "—")}</td></tr>'
            for m in sorted(trs, key=lambda m: (m.get("floor", 0), m.get("gs", 0))))
    else:
        tbody = f'<tr><td colspan="6" class="muted" style="text-align:center;padding:20px 8px">{t["no_meas_short"]}</td></tr>'
    meas = f"""<section class="panel" style="margin-top:24px" aria-labelledby="meas"><h2 id="meas">{t['measures']}</h2>
<p class="muted small" style="margin:4px 0 16px">{t['meas_note']}</p>
<h3>{t['farm']}</h3><div class="tbl-wrap"><table style="min-width:760px;font-size:14px"><thead><tr><th>{t['m_spot']}</th><th class="num">{t['m_gs']}</th><th class="num">{t['m_exp']}</th><th class="num">{t['m_adena']}</th><th class="num">{t['m_lcoin']}</th><th class="num">{t['m_mobs']}</th><th class="num">{t['m_vs']}</th><th class="num">{t['m_n']}</th></tr></thead><tbody>{fbody}</tbody></table></div>
<h3 style="margin-top:24px">{t['tower']}</h3><div class="tbl-wrap"><table style="min-width:640px;font-size:14px"><thead><tr><th>{t['m_floor']}</th><th>{t['m_diff']}</th><th>{t['m_res']}</th><th class="num">{t['m_gs']}</th><th class="num">{t['m_left']}</th><th class="num">{t['m_hp']}</th></tr></thead><tbody>{tbody}</tbody></table></div>
</section></div>"""
    return page(lang, rel, "classes", f"class/{slug}/", c["name"][lang], hero + skills + books + meas)


# ---------------------------------------------------------------- compare
def loc_skill(v, lang):
    if not v:
        return None
    v = {k: x for k, x in v.items() if k != "names"} | {"name": (v.get("names") or {}).get(lang, v["name"])}
    return v


def compare(lang):
    t, rel = T[lang], "../../"
    payload = {
        "classes": [{"slug": c["slug"], "name": c["name"][lang], "race": RACE[c["race"]][lang], "arch": c["arch"],
                     "spam": loc_skill(c.get("spam"), lang), "aoe": loc_skill(c.get("aoe"), lang), "books": c["bookCount"],
                     "farm": AGG.get(c["slug"], {})} for c in CLASSES],
        "spots": [{"code": s["code"], "name": s["name"][lang]} for s in ZONES["spots"]],
        "t": {k: t[k] for k in ("cmp_race", "cmp_spam", "cmp_pps", "cmp_cd", "cmp_hit", "cmp_base", "cmp_aoe", "cmp_mp", "cmp_books", "cmp_mix",
                                "m_exp", "m_adena", "m_lcoin", "m_mobs", "m_gs", "m_n", "no_meas_short", "targets_n", "sec")},
        "lang": lang, "rel": rel,
    }
    opts = "".join(f'<option value="{c["slug"]}">{e(c["name"][lang])}</option>' for c in sorted(CLASSES, key=lambda c: c["name"][lang]))
    pickers = "".join(f'<div class="picker"><label for="pick{i}">{t["cmp_pick"].format(n=i + 1)}</label><select id="pick{i}" data-pick="{i}">{opts}</select></div>' for i in range(3))
    spots = "".join(f'<option value="{s["code"]}">{s["code"]} — {e(s["name"][lang])}</option>' for s in ZONES["spots"])
    body = f"""<section class="wrap sec"><h1>{t['cmp_title']}</h1><p class="c2" style="margin:8px 0 20px">{t['cmp_intro']}</p>
<div class="panel"><div class="pickers">{pickers}</div><div class="banner warn" id="mix" hidden><span>{t['cmp_mix']}</span></div></div>
<div class="panel" style="margin-top:24px"><h2>{t['cmp_skills']}</h2><div class="tbl-wrap" style="margin-top:14px"><table id="cmp-skills" style="min-width:640px"></table></div></div>
<div class="panel" style="margin-top:24px"><div class="sec-head" style="margin-bottom:8px"><h2>{t['cmp_meas']}</h2>
<div class="picker" style="flex:0 1 340px"><label for="spot">{t['cmp_spot']}</label><select id="spot">{spots}</select></div></div>
<div class="tbl-wrap"><table id="cmp-meas" style="min-width:640px"></table></div><p class="muted small" style="margin:10px 0 0">{t['per_hour_note']}</p></div>
</section>
<script id="cmp-data" type="application/json">{json.dumps(payload, ensure_ascii=False)}</script>"""
    return page(lang, rel, "compare", "compare/", t["cmp_title"], body, f'<script src="{rel}assets/js/compare.js" defer></script>')


# ---------------------------------------------------------------- zones
def zones(lang):
    t, rel = T[lang], "../../"
    sp = "".join(f'<tr><td class="gold">{s["code"]}</td><td style="font-weight:600">{e(s["name"][lang])}</td><td>{s["lvl"]}</td><td class="num">{s["hp"]}</td><td class="c2">{e(s["what"][lang])}</td></tr>' for s in ZONES["spots"])
    body = f"""<section class="wrap sec"><h1>{t['zones_page']}</h1>
<div class="panel" style="margin-top:20px"><h2>{t['zones_title']}</h2><p class="muted small" style="margin:6px 0 16px">{e(ZONES['note'][lang])}</p>{zones_table(lang)}</div>
<div class="panel" style="margin-top:24px"><h2>{t['spots']}</h2><div class="tbl-wrap" style="margin-top:14px"><table style="min-width:600px"><thead><tr><th>{t['sp_code']}</th><th>{t['z_name']}</th><th>{t['z_lvl']}</th><th class="num">{t['z_hp']}</th><th>{t['sp_type']}</th></tr></thead><tbody>{sp}</tbody></table></div></div>
</section>"""
    return page(lang, rel, "zones", "zones/", t["zones_page"], body)


# ---------------------------------------------------------------- measurements
def measurements(lang):
    t, rel = T[lang], "../../"
    method = "".join(f"<li>{e(x)}</li>" for x in t["method"])
    if FARM:
        rows = "".join(
            f'<tr><td class="c2">{e(m.get("date", ""))}</td><td><a href="{rel}{lang}/class/{m["class"]}/" style="display:flex;gap:8px;align-items:center;color:var(--text)">{icon(rel, m["class"], 28)}{e(BY[m["class"]]["name"][lang])}</a></td>'
            f'<td>{m["spot"]}</td><td class="num">{m["minutes"]}</td><td class="num">{num(m.get("gs"), lang)}</td><td class="num">{m.get("kills", "—")}</td>'
            f'<td class="num">{num(per_hour(m, "exp"), lang)}</td><td class="num">{num(per_hour(m, "adena"), lang)}</td><td class="num">{num(per_hour(m, "lcoin"), lang)}</td><td class="num">{num(per_hour(m, "kills"), lang)}</td>'
            f'<td class="c2">{e(m.get("by", ""))}</td><td class="c2">{e(m.get("note", ""))}</td></tr>'
            for m in sorted(FARM, key=lambda m: m.get("date", ""), reverse=True))
    else:
        rows = f'<tr><td colspan="12" class="muted" style="text-align:center;padding:20px 8px">{t["no_meas_short"]}</td></tr>'
    if TOWER:
        trows = "".join(
            f'<tr><td class="c2">{e(m.get("date", ""))}</td><td>{e(BY[m["class"]]["name"][lang])}</td><td>{m.get("floor")}</td><td>{e(str(m.get("difficulty", "—")))}</td><td>{t["win"] if m.get("win") else t["loss"]}</td><td class="num">{num(m.get("gs"), lang)}</td><td class="num">{m.get("time_left", "—")}</td><td class="num">{m.get("hp_lost", "—")}</td></tr>'
            for m in sorted(TOWER, key=lambda m: m.get("date", ""), reverse=True))
    else:
        trows = f'<tr><td colspan="8" class="muted" style="text-align:center;padding:20px 8px">{t["no_meas_short"]}</td></tr>'
    body = f"""<section class="wrap sec"><h1>{t['meas_page']}</h1>
<div class="panel" style="margin-top:20px"><h2>{t['meas_method']}</h2><ul style="margin:12px 0 0;padding-left:20px;color:var(--text-2)">{method}</ul></div>
<div class="panel" style="margin-top:24px"><h2>{t['farm']}</h2><p class="muted small" style="margin:4px 0 14px">{t['per_hour_note']}</p>
<div class="tbl-wrap"><table style="min-width:1000px;font-size:14px"><thead><tr><th>{t['m_date']}</th><th>{t['m_class']}</th><th>{t['m_spot']}</th><th class="num">{t['m_min']}</th><th class="num">{t['m_gs']}</th><th class="num">{t['m_kills']}</th><th class="num">{t['m_exp']}</th><th class="num">{t['m_adena']}</th><th class="num">{t['m_lcoin']}</th><th class="num">{t['m_mobs']}</th><th>{t['m_by']}</th><th>{t['m_note']}</th></tr></thead><tbody>{rows}</tbody></table></div></div>
<div class="panel" style="margin-top:24px"><h2>{t['tower']}</h2>
<div class="tbl-wrap" style="margin-top:14px"><table style="min-width:760px;font-size:14px"><thead><tr><th>{t['m_date']}</th><th>{t['m_class']}</th><th>{t['m_floor']}</th><th>{t['m_diff']}</th><th>{t['m_res']}</th><th class="num">{t['m_gs']}</th><th class="num">{t['m_left']}</th><th class="num">{t['m_hp']}</th></tr></thead><tbody>{trows}</tbody></table></div></div>
</section>"""
    return page(lang, rel, "meas", "measurements/", t["meas_page"], body)


# ---------------------------------------------------------------- root
def root_index():
    return """<!doctype html><html lang="uk"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Essence analytics</title>
<meta http-equiv="refresh" content="0; url=ua/">
<script>(function(){var l=(navigator.language||'').toLowerCase();var t=l.indexOf('ru')===0?'ru/':(l.indexOf('uk')===0?'ua/':(l.indexOf('en')===0?'en/':'ua/'));location.replace(t);})();</script>
<style>body{background:#100E0C;color:#ECE4D3;font-family:system-ui,sans-serif;padding:24px}a{color:#E2B95A}</style>
</head><body><a href="ua/">UA</a> · <a href="en/">EN</a> · <a href="ru/">RU</a></body></html>"""


def main():
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(DIST, "assets"))
    write("index.html", root_index())
    write(".nojekyll", "")
    n = 0
    for lang in LANGS:
        write(f"{lang}/index.html", home(lang))
        write(f"{lang}/compare/index.html", compare(lang))
        write(f"{lang}/zones/index.html", zones(lang))
        write(f"{lang}/measurements/index.html", measurements(lang))
        for c in CLASSES:
            write(f"{lang}/class/{c['slug']}/index.html", class_page(lang, c))
            n += 1
    print(f"built {n + 4 * len(LANGS) + 1} pages into dist/")


if __name__ == "__main__":
    main()
