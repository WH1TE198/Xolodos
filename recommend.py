# recommend.py
from datetime import datetime, date
from products_db import list_products
from recipes_db import get_all_recipes

ALIASES = {
    "помидоры": "томаты",
    "томат": "томаты",
    "перец болгарский": "перец",
    "сыр пармезан": "сыр",
    "сыр фета": "сыр фета",
    "моцарелла": "сыр моцарелла",
    "курица": "куриное филе",
    "куриное мясо": "куриное филе",
    "говядина фарш": "говядина",
    "рыбное филе": "рыба",
    "зелень": "зелень",
    "фарш говяжий": "говядина",
    "масло сливочное": "масло",
    "масло растительное": "масло",
    "рис арборио": "рис",
    "нори": "нори",
    "печенье савоярди": "савоярди",
    "зелёный лук": "зелень",
    "листы лазаньи": "листы лазаньи",
    "лаваш": "лаваш",
    "сливки": "сливки",
    "бульон": "куриный бульон",
    "помидоры": "томаты",
    "помидор": "томаты",
    "томат": "томаты",
    "томатная паста": "томаты",
    "моцарелла": "сыр моцарелла",
    "сыр пармезан": "сыр",
    "сыр фета": "сыр фета",
    "макароны": "паста",
    "спагетти": "паста",
    "рис арборио": "рис",
    "лук репчатый": "лук",
    "зеленый лук": "зелень",
    "зелёный лук": "зелень",
    "болгарский перец": "перец",
    "фарш": "говядина",
    "фарш говяжий": "говядина",
    "курица": "куриное филе",
    "куриное мясо": "куриное филе",
    "яйцо": "яйца",
    "яйца куриные": "яйца",
    "огурцы": "огурец",
    "масло сливочное": "масло",
    "растительное масло": "масло",
    "оливковое масло": "масло",
    "рисовая лапша": "лапша",
    "нори лист": "нори",
    "листы лазаньи": "листы лазаньи",
    "лаваш тонкий": "лаваш",

}

def norm(s: str) -> str:
    k = (s or "").strip().lower()
    return ALIASES.get(k, k)

def _parse_date(s: str):
    try:
        return datetime.strptime((s or "").strip(), "%d.%m.%Y").date()
    except Exception:
        return None

def suggest_recipes(top_n: int = 10):
    """Возвращает [{recipe, score, coverage, have[], missing[]}, ...]."""
    try:
        prods = list_products(limit=2000)
    except Exception:
        prods = []
    have_map = {norm(p.get("name")): p for p in prods if (p.get("name") or "").strip()}
    today = date.today()

    out = []
    for r in get_all_recipes():
        ings = r.get("ingredients", [])
        if not ings:
            continue

        hits, missing, bonus = [], [], 0
        for i in ings:
            key = norm(i.get("name"))
            if key in have_map:
                hits.append(i)
                d = _parse_date(have_map[key].get("exp_date"))
                if d:
                    days = (d - today).days
                    bonus += max(0, 10 - days)  # бонус за скоро портящиеся
            else:
                missing.append(i)

        coverage = len(hits) / len(ings)
        score = int(coverage * 100 + bonus)
        out.append({"recipe": r, "coverage": coverage, "score": score, "have": hits, "missing": missing})

    out.sort(key=lambda x: (x["coverage"] >= 0.7, x["score"]), reverse=True)
    return out[:top_n]
