# recipes_db.py
import sqlite3
from contextlib import closing

DB_PATH = "app.db"

def _conn():
    return sqlite3.connect(DB_PATH)

def init_recipes_db():
    """Создаёт таблицы под рецепты/ингредиенты."""
    with _conn() as conn, closing(conn.cursor()) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                steps TEXT,            -- можно хранить текст или markdown
                time_min INTEGER,      -- время приготовления (мин)
                difficulty TEXT        -- 'легко' / 'средне' / 'сложно'
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS recipe_ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                name TEXT NOT NULL,    -- название ингредиента
                qty REAL,              -- количество (необязательно)
                unit TEXT,             -- ед. изм. (г, мл, шт, ...)
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
            )
        """)
        conn.commit()

def add_recipe(title: str, steps: str, ingredients: list, time_min: int | None = None, difficulty: str | None = None) -> int:
    """Добавляет рецепт и его ингредиенты. Ingredients — список словарей: {'name':..., 'qty':..., 'unit':...}"""
    with _conn() as conn, closing(conn.cursor()) as c:
        c.execute(
            "INSERT INTO recipes(title, steps, time_min, difficulty) VALUES(?,?,?,?)",
            (title, steps, time_min, difficulty)
        )
        rid = c.lastrowid
        if ingredients:
            c.executemany(
                "INSERT INTO recipe_ingredients(recipe_id, name, qty, unit) VALUES(?,?,?,?)",
                [(rid, i.get("name"), i.get("qty"), i.get("unit")) for i in ingredients]
            )
        conn.commit()
        return rid

def get_all_recipes() -> list[dict]:
    """Возвращает список рецептов с вложенными ингредиентами."""
    with _conn() as conn, closing(conn.cursor()) as c:
        rows = c.execute("SELECT id, title, steps, time_min, difficulty FROM recipes").fetchall()
        data = []
        for (rid, title, steps, tm, diff) in rows:
            ings = c.execute(
                "SELECT name, qty, unit FROM recipe_ingredients WHERE recipe_id=?",
                (rid,)
            ).fetchall()
            data.append({
                "id": rid,
                "title": title,
                "steps": steps or "",
                "time_min": tm,
                "difficulty": diff,
                "ingredients": [{"name": n, "qty": q, "unit": u} for (n, q, u) in ings],
            })
        return data

# Небольшой сидер (по желанию) — вызови один раз, чтобы были примеры
def seed_demo_if_empty():
    with _conn() as conn, closing(conn.cursor()) as c:
        cnt = c.execute("SELECT COUNT(*) FROM recipes").fetchone()[0]
    if cnt > 0:
        return
    add_recipe(
        "Омлет с сыром",
        "Взбить яйца, добавить соль, перец. Обжарить на сковороде, посыпать сыром, сложить пополам.",
        [{"name": "яйца", "qty": 3, "unit": "шт"},
         {"name": "сыр", "qty": 50, "unit": "г"},
         {"name": "молоко", "qty": 30, "unit": "мл"}],
        time_min=10, difficulty="легко"
    )
    add_recipe(
        "Салат греческий",
        "Нарезать помидоры, огурцы, перец, лук, фету; добавить маслины, оливковое масло.",
        [{"name": "помидоры", "qty": 2, "unit": "шт"},
         {"name": "огурец", "qty": 1, "unit": "шт"},
         {"name": "сыр фета", "qty": 100, "unit": "г"},
         {"name": "маслины", "qty": 10, "unit": "шт"}],
        time_min=12, difficulty="легко"
    )
    add_recipe(
        "Паста с томатным соусом",
        "Сварить пасту аль денте. Соус: пассеровать чеснок, добавить томаты, уварить, смешать с пастой.",
        [{"name": "паста", "qty": 200, "unit": "г"},
         {"name": "томаты", "qty": 300, "unit": "г"},
         {"name": "чеснок", "qty": 2, "unit": "зубчик"}],
        time_min=20, difficulty="средне"
    )
# --- helpers: добавление рецепта, если его ещё нет по title ---
def _has_recipe(title: str) -> bool:
    with _conn() as conn, closing(conn.cursor()) as c:
        row = c.execute("SELECT 1 FROM recipes WHERE title = ? LIMIT 1", (title,)).fetchone()
        return row is not None

def add_recipe_if_absent(title, steps, ingredients, time_min=None, difficulty=None):
    if not _has_recipe(title):
        return add_recipe(title, steps, ingredients, time_min, difficulty)
    return None

# --- сидер: популярные рецепты мира ---
def seed_world_recipes() -> int:
    """
    Добавляет набор популярных рецептов, если их ещё нет.
    Возвращает, сколько штук было добавлено.
    """
    added = 0

    def put(title, steps, ings, time_min=None, difficulty=None):
        nonlocal added
        rid = add_recipe_if_absent(title, steps, ings, time_min, difficulty)
        if rid:
            added += 1

    # 1) Пицца Маргарита
    put(
        "Пицца Маргарита",
        "Тесто, томатный соус, сверху сыр моцарелла и базилик. Выпекать до румяности.",
        [
            {"name": "томаты", "qty": 300, "unit": "г"},
            {"name": "сыр моцарелла", "qty": 150, "unit": "г"},
            {"name": "мука", "qty": 300, "unit": "г"},
            {"name": "дрожжи", "qty": 7, "unit": "г"},
            {"name": "базилик", "qty": 1, "unit": "пучок"},
            {"name": "оливковое масло", "qty": 2, "unit": "ст.л."},
        ],
        time_min=30, difficulty="средне"
    )

    # 2) Спагетти Карбонара
    put(
        "Спагетти Карбонара",
        "Отварить пасту. Обжарить бекон, смешать с яйцами и сыром. Перемешать с пастой.",
        [
            {"name": "паста", "qty": 250, "unit": "г"},
            {"name": "яйца", "qty": 2, "unit": "шт"},
            {"name": "сыр", "qty": 60, "unit": "г"},
            {"name": "бекон", "qty": 120, "unit": "г"},
            {"name": "чеснок", "qty": 1, "unit": "зубчик"},
        ],
        time_min=20, difficulty="легко"
    )

    # 3) Пад тай
    put(
        "Пад тай",
        "Обжарить рисовую лапшу с курицей/креветками, яйцом, арахисом, лаймом и соусом.",
        [
            {"name": "рисовая лапша", "qty": 200, "unit": "г"},
            {"name": "куриное филе", "qty": 200, "unit": "г"},
            {"name": "яйца", "qty": 1, "unit": "шт"},
            {"name": "арахис", "qty": 30, "unit": "г"},
            {"name": "лайм", "qty": 1, "unit": "шт"},
            {"name": "соевый соус", "qty": 2, "unit": "ст.л."},
        ],
        time_min=25, difficulty="средне"
    )

    # 4) Фо бо (вьетнамский суп)
    put(
        "Фо бо",
        "Говяжий бульон, рисовая лапша, говядина, зелень, лайм. Подача с соусами.",
        [
            {"name": "говядина", "qty": 250, "unit": "г"},
            {"name": "рисовая лапша", "qty": 200, "unit": "г"},
            {"name": "лук", "qty": 1, "unit": "шт"},
            {"name": "лайм", "qty": 1, "unit": "шт"},
            {"name": "зелень", "qty": 1, "unit": "пучок"},
        ],
        time_min=40, difficulty="средне"
    )

    # 5) Рамен (shoyu)
    put(
        "Рамен шою",
        "Куриный/свиной бульон, лапша, соевый соус, яйцо, зелёный лук.",
        [
            {"name": "куриный бульон", "qty": 1, "unit": "л"},
            {"name": "лапша", "qty": 200, "unit": "г"},
            {"name": "соевый соус", "qty": 3, "unit": "ст.л."},
            {"name": "яйца", "qty": 1, "unit": "шт"},
            {"name": "зелёный лук", "qty": 1, "unit": "пучок"},
        ],
        time_min=35, difficulty="средне"
    )

    # 6) Том ям
    put(
        "Том ям",
        "Кисло-острый суп с креветками, грибами, лаймом и пастой том ям.",
        [
            {"name": "креветки", "qty": 250, "unit": "г"},
            {"name": "грибы", "qty": 150, "unit": "г"},
            {"name": "лайм", "qty": 1, "unit": "шт"},
            {"name": "кокосовое молоко", "qty": 200, "unit": "мл"},
            {"name": "чили", "qty": 1, "unit": "шт"},
        ],
        time_min=25, difficulty="средне"
    )

    # 7) Паэлья
    put(
        "Паэлья",
        "Обжарить рис с шафраном, добавить бульон, морепродукты/курицу и овощи, довести.",
        [
            {"name": "рис", "qty": 300, "unit": "г"},
            {"name": "куриное филе", "qty": 200, "unit": "г"},
            {"name": "креветки", "qty": 200, "unit": "г"},
            {"name": "перец", "qty": 1, "unit": "шт"},
            {"name": "томаты", "qty": 200, "unit": "г"},
        ],
        time_min=45, difficulty="средне"
    )

    # 8) Шакшука
    put(
        "Шакшука",
        "Томаты с луком и специями тушить, сделать лунки, добавить яйца и довести до готовности.",
        [
            {"name": "томаты", "qty": 400, "unit": "г"},
            {"name": "лук", "qty": 1, "unit": "шт"},
            {"name": "чеснок", "qty": 2, "unit": "зубчик"},
            {"name": "яйца", "qty": 3, "unit": "шт"},
            {"name": "перец", "qty": 0.5, "unit": "шт"},
        ],
        time_min=20, difficulty="легко"
    )

    # 9) Хумус
    put(
        "Хумус",
        "Измельчить нут с тахини, лимоном, чесноком и оливковым маслом до пасты.",
        [
            {"name": "нут", "qty": 250, "unit": "г"},
            {"name": "тахини", "qty": 2, "unit": "ст.л."},
            {"name": "лимон", "qty": 0.5, "unit": "шт"},
            {"name": "чеснок", "qty": 1, "unit": "зубчик"},
            {"name": "оливковое масло", "qty": 2, "unit": "ст.л."},
        ],
        time_min=15, difficulty="легко"
    )

    # 10) Цезарь (классический, без курицы)
    put(
        "Салат Цезарь",
        "Салат ромэн, сухарики, пармезан, заправка на основе яйца/анчоуса/масла.",
        [
            {"name": "листья салата", "qty": 1, "unit": "кочан"},
            {"name": "сыр", "qty": 50, "unit": "г"},
            {"name": "батон", "qty": 4, "unit": "ломтик"},
            {"name": "яйца", "qty": 1, "unit": "шт"},
            {"name": "анчоусы", "qty": 4, "unit": "шт"},
        ],
        time_min=15, difficulty="легко"
    )

    # 11) Тако (базовые)
    put(
        "Тако",
        "Обжарить мясо со специями, подать в тортильях с овощами и соусом.",
        [
            {"name": "говядина", "qty": 250, "unit": "г"},
            {"name": "тортильи", "qty": 4, "unit": "шт"},
            {"name": "лук", "qty": 1, "unit": "шт"},
            {"name": "томаты", "qty": 150, "unit": "г"},
            {"name": "перец", "qty": 1, "unit": "шт"},
        ],
        time_min=25, difficulty="легко"
    )

    # 12) Фиш-н-чипс
    put(
        "Фиш-н-чипс",
        "Филе белой рыбы в кляре обжарить во фритюре. Подача с картофелем фри.",
        [
            {"name": "рыба", "qty": 300, "unit": "г"},
            {"name": "картофель", "qty": 400, "unit": "г"},
            {"name": "мука", "qty": 120, "unit": "г"},
            {"name": "яйца", "qty": 1, "unit": "шт"},
            {"name": "масло растительное", "qty": 400, "unit": "мл"},
        ],
        time_min=30, difficulty="средне"
    )

    return added

def seed_more_world_recipes() -> int:
    """
    Ещё набор популярных рецептов мира. Добавляет только те, которых нет.
    Возвращает число добавленных.
    """
    added = 0

    def put(title, steps, ings, time_min=None, difficulty=None):
        nonlocal added
        rid = add_recipe_if_absent(title, steps, ings, time_min, difficulty)
        if rid:
            added += 1

    # 1) Лазанья болоньезе
    put(
        "Лазанья болоньезе",
        "Слой листов лазаньи, соус болоньезе, соус бешамель и сыр. Запекать до румяности.",
        [
            {"name": "фарш говяжий", "qty": 400, "unit": "г"},
            {"name": "лук", "qty": 1, "unit": "шт"},
            {"name": "чеснок", "qty": 2, "unit": "зубчик"},
            {"name": "томаты", "qty": 400, "unit": "г"},
            {"name": "листы лазаньи", "qty": 9, "unit": "шт"},
            {"name": "молоко", "qty": 400, "unit": "мл"},
            {"name": "мука", "qty": 2, "unit": "ст.л."},
            {"name": "масло сливочное", "qty": 40, "unit": "г"},
            {"name": "сыр", "qty": 120, "unit": "г"},
        ],
        time_min=60, difficulty="средне"
    )

    # 2) Ризотто с грибами
    put(
        "Ризотто с грибами",
        "Обжарить рис арборио с луком, подливать бульон, добавить грибы и сыр.",
        [
            {"name": "рис", "qty": 300, "unit": "г"},
            {"name": "грибы", "qty": 250, "unit": "г"},
            {"name": "лук", "qty": 1, "unit": "шт"},
            {"name": "масло сливочное", "qty": 40, "unit": "г"},
            {"name": "куриный бульон", "qty": 1, "unit": "л"},
            {"name": "сыр", "qty": 60, "unit": "г"},
        ],
        time_min=35, difficulty="средне"
    )

    # 3) Борщ
    put(
        "Борщ",
        "Сварить бульон. Обжарить свёклу, морковь, лук, добавить капусту и картофель, томаты.",
        [
            {"name": "говядина", "qty": 400, "unit": "г"},
            {"name": "свёкла", "qty": 1, "unit": "шт"},
            {"name": "морковь", "qty": 1, "unit": "шт"},
            {"name": "лук", "qty": 1, "unit": "шт"},
            {"name": "картофель", "qty": 3, "unit": "шт"},
            {"name": "капуста", "qty": 300, "unit": "г"},
            {"name": "томаты", "qty": 200, "unit": "г"},
        ],
        time_min=70, difficulty="средне"
    )

    # 4) Плов
    put(
        "Плов",
        "Обжарить мясо с луком и морковью, добавить рис, специи и воду. Томить до готовности.",
        [
            {"name": "рис", "qty": 400, "unit": "г"},
            {"name": "говядина", "qty": 500, "unit": "г"},
            {"name": "лук", "qty": 2, "unit": "шт"},
            {"name": "морковь", "qty": 2, "unit": "шт"},
            {"name": "чеснок", "qty": 1, "unit": "головка"},
            {"name": "масло растительное", "qty": 80, "unit": "мл"},
        ],
        time_min=60, difficulty="средне"
    )

    # 5) Чили кон карне
    put(
        "Чили кон карне",
        "Обжарить фарш, добавить фасоль, томаты, кукурузу, специи. Тушить до густоты.",
        [
            {"name": "фарш говяжий", "qty": 400, "unit": "г"},
            {"name": "фасоль", "qty": 300, "unit": "г"},
            {"name": "кукуруза", "qty": 150, "unit": "г"},
            {"name": "томаты", "qty": 400, "unit": "г"},
            {"name": "лук", "qty": 1, "unit": "шт"},
            {"name": "чили", "qty": 1, "unit": "шт"},
        ],
        time_min=35, difficulty="легко"
    )

    # 6) Минестроне
    put(
        "Минестроне",
        "Томатный овощной суп с фасолью и пастой. Варить до мягкости овощей.",
        [
            {"name": "томаты", "qty": 400, "unit": "г"},
            {"name": "морковь", "qty": 1, "unit": "шт"},
            {"name": "лук", "qty": 1, "unit": "шт"},
            {"name": "сельдерей", "qty": 1, "unit": "стебель"},
            {"name": "фасоль", "qty": 200, "unit": "г"},
            {"name": "паста", "qty": 80, "unit": "г"},
        ],
        time_min=30, difficulty="легко"
    )

    # 7) Курица терияки с рисом
    put(
        "Курица терияки",
        "Обжарить курицу, добавить соус терияки, подать с рисом и зелёным луком.",
        [
            {"name": "куриное филе", "qty": 350, "unit": "г"},
            {"name": "соевый соус", "qty": 3, "unit": "ст.л."},
            {"name": "рис", "qty": 200, "unit": "г"},
            {"name": "зелёный лук", "qty": 1, "unit": "пучок"},
        ],
        time_min=25, difficulty="легко"
    )

    # 8) Гаспачо
    put(
        "Гаспачо",
        "Холодный суп: измельчить томаты, огурец, перец, лук, чеснок, масло и уксус.",
        [
            {"name": "томаты", "qty": 600, "unit": "г"},
            {"name": "огурец", "qty": 1, "unit": "шт"},
            {"name": "перец", "qty": 1, "unit": "шт"},
            {"name": "лук", "qty": 0.5, "unit": "шт"},
            {"name": "чеснок", "qty": 1, "unit": "зубчик"},
            {"name": "оливковое масло", "qty": 2, "unit": "ст.л."},
        ],
        time_min=15, difficulty="легко"
    )

    # 9) Сырный крем-суп
    put(
        "Сырный крем-суп",
        "Обжарить лук, добавить картофель и бульон. Взбить, вмешать сливки и сыр.",
        [
            {"name": "картофель", "qty": 400, "unit": "г"},
            {"name": "лук", "qty": 1, "unit": "шт"},
            {"name": "куриный бульон", "qty": 800, "unit": "мл"},
            {"name": "сливки", "qty": 150, "unit": "мл"},
            {"name": "сыр", "qty": 120, "unit": "г"},
        ],
        time_min=30, difficulty="легко"
    )

    # 10) Куриный суп-лапша
    put(
        "Куриный суп-лапша",
        "Бульон с курицей, лапшой, морковью и зеленью. Варить до готовности.",
        [
            {"name": "куриное филе", "qty": 300, "unit": "г"},
            {"name": "куриный бульон", "qty": 1, "unit": "л"},
            {"name": "лапша", "qty": 120, "unit": "г"},
            {"name": "морковь", "qty": 1, "unit": "шт"},
            {"name": "зелень", "qty": 1, "unit": "пучок"},
        ],
        time_min=30, difficulty="легко"
    )

    # 11) Бургеры классические
    put(
        "Бургеры классические",
        "Сформовать котлеты, обжарить. Собрать с булочкой, сыром и овощами.",
        [
            {"name": "фарш говяжий", "qty": 400, "unit": "г"},
            {"name": "булочки", "qty": 4, "unit": "шт"},
            {"name": "сыр", "qty": 4, "unit": "ломтик"},
            {"name": "лук", "qty": 1, "unit": "шт"},
            {"name": "огурец", "qty": 1, "unit": "шт"},
            {"name": "томатный соус", "qty": 2, "unit": "ст.л."},
        ],
        time_min=20, difficulty="легко"
    )

    # 12) Шаверма (шаурма) куриная
    put(
        "Шаверма куриная",
        "Обжарить курицу со специями, завернуть в лаваш с овощами и соусом.",
        [
            {"name": "куриное филе", "qty": 350, "unit": "г"},
            {"name": "лаваш", "qty": 2, "unit": "шт"},
            {"name": "огурец", "qty": 1, "unit": "шт"},
            {"name": "томаты", "qty": 2, "unit": "шт"},
            {"name": "чеснок", "qty": 1, "unit": "зубчик"},
            {"name": "йогурт", "qty": 150, "unit": "г"},
        ],
        time_min=25, difficulty="легко"
    )

    # 13) Суши-ролл «Калифорния»
    put(
        "Суши-ролл Калифорния",
        "Приготовить рис для суши, завернуть с нори, крабом/краб-палочками, авокадо и огурцом.",
        [
            {"name": "рис", "qty": 250, "unit": "г"},
            {"name": "нори", "qty": 4, "unit": "лист"},
            {"name": "огурец", "qty": 1, "unit": "шт"},
            {"name": "крабовые палочки", "qty": 150, "unit": "г"},
            {"name": "майонез", "qty": 2, "unit": "ст.л."},
            {"name": "соевый соус", "qty": 2, "unit": "ст.л."},
        ],
        time_min=40, difficulty="средне"
    )

    # 14) Панкейки
    put(
        "Панкейки",
        "Смешать яйцо, молоко, муку, разрыхлитель, сахар. Жарить небольшими кружками.",
        [
            {"name": "яйца", "qty": 1, "unit": "шт"},
            {"name": "молоко", "qty": 250, "unit": "мл"},
            {"name": "мука", "qty": 180, "unit": "г"},
            {"name": "сахар", "qty": 1.5, "unit": "ст.л."},
            {"name": "разрыхлитель", "qty": 1, "unit": "ч.л."},
            {"name": "масло сливочное", "qty": 30, "unit": "г"},
        ],
        time_min=20, difficulty="легко"
    )

    # 15) Тирамису (упрощённый)
    put(
        "Тирамису",
        "Выложить слоями савоярди, крем из маскарпоне и кофе. Охладить и присыпать какао.",
        [
            {"name": "печенье савоярди", "qty": 200, "unit": "г"},
            {"name": "маскарпоне", "qty": 250, "unit": "г"},
            {"name": "сливки", "qty": 200, "unit": "мл"},
            {"name": "кофе", "qty": 150, "unit": "мл"},
            {"name": "какао", "qty": 1, "unit": "ст.л."},
        ],
        time_min=30, difficulty="легко"
    )

    return added
