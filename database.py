import sqlite3

def init_db(conn):
    """Создание таблиц."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT CHECK(type IN ('завтрак', 'обед')) NOT NULL,
            calories INTEGER NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dish_ingredients (
            dish_id INTEGER NOT NULL,
            ingredient_id INTEGER NOT NULL,
            grams INTEGER NOT NULL,
            FOREIGN KEY (dish_id) REFERENCES dishes(id) ON DELETE CASCADE,
            FOREIGN KEY (ingredient_id) REFERENCES ingredients(id) ON DELETE CASCADE,
            PRIMARY KEY (dish_id, ingredient_id)
        )
    ''')
    conn.commit()

def add_dish(conn, name, dish_type, calories, ingredients):
    """Вставка блюда и его ингредиентов."""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO dishes (name, type, calories) VALUES (?, ?, ?)",
            (name, dish_type, calories)
        )
        dish_id = cursor.lastrowid
        
        for ing in ingredients:
            ing_name = ing['name']
            grams = ing['grams']
            
            cursor.execute("INSERT OR IGNORE INTO ingredients (name) VALUES (?)", (ing_name,))
            cursor.execute("SELECT id FROM ingredients WHERE name = ?", (ing_name,))
            ingredient_id = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO dish_ingredients (dish_id, ingredient_id, grams)
                VALUES (?, ?, ?)
            """, (dish_id, ingredient_id, grams))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        conn.rollback()
        return False

def get_all_dishes(conn):
    """Возвращает список всех блюд."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, type, calories FROM dishes")
    return cursor.fetchall()

def get_dishes_by_type(conn, dish_type):
    """Возвращает блюда заданного типа."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM dishes WHERE type = ?", (dish_type,))
    return cursor.fetchall()

def get_dish_details(conn, dish_id):
    """Возвращает ингредиенты конкретного блюда (только названия и граммы)."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.name, di.grams
        FROM dish_ingredients di
        JOIN ingredients i ON di.ingredient_id = i.id
        WHERE di.dish_id = ?
    """, (dish_id,))
    return cursor.fetchall()

def delete_dish(conn, dish_id):
    """Удаление блюда."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dishes WHERE id = ?", (dish_id,))
    conn.commit()