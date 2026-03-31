import sys
import sqlite3
import math
from database import init_db, add_dish, get_all_dishes, get_dishes_by_type, get_dish_details, delete_dish
from utils import get_db_path, input_int, print_table

# Исправление кодировки для Windows консоли
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def menu_add_dish(conn):
    print("\n=== Добавление блюда ===")
    name = input("Введите название блюда: ").strip()
    
    print("Выберите тип:\n1. завтрак\n2. обед")
    type_choice = input_int("Ваш выбор: ", 1, 2)
    types_map = {1: 'завтрак', 2: 'обед'}
    dish_type = types_map[type_choice]

    calories = input_int("\nВведите общую калорийность блюда (на порцию): ", 0)

    ing_count = input_int("\nСколько ингредиентов будет для одной порции? ", 1, 100)
    ingredients = []
    
    for i in range(1, ing_count + 1):
        print(f"\nИнгредиент {i}:")
        ing_name = input("Название: ").strip()
        grams = input_int("Граммы: ", 1)
        ingredients.append({'name': ing_name, 'grams': grams})

    if add_dish(conn, name, dish_type, calories, ingredients):
        print(f'\nБлюдо "{name}" добавлено!')
    else:
        print(f'\nОшибка: Блюдо с названием "{name}" уже существует.')

def menu_show_dishes(conn):
    print("\n=== Все блюда ===")
    dishes = get_all_dishes(conn)
    if dishes:
        print_table(["ID", "Название", "Тип", "Калории"], dishes)
    else:
        print("База блюд пуста.")

def menu_create_plan(conn):
    print("\n=== Составление рациона ===")
    days = input_int("Введите количество дней: ", 1, 30)
    meal_multiply = input_int("\nВведите количество порций на один прием пищи: ",1,4)
    
    # Порядок приёмов пищи: завтрак, обед, ужин
    meals = [
        ('завтрак', 'завтрак'),    # (отображаемое имя, тип в БД)
        ('обед', 'обед'),
        ('ужин', 'обед')
    ]
    selected_dishes_info = []   # (день, приём, название_блюда)
    selected_dish_ids = []      # id выбранных блюд

    for day in range(1, days + 1):
        print(f"\nДень {day}:")
        for meal_name, meal_type in meals:
            print(f"--- {meal_name.capitalize()} ---")
            available = get_dishes_by_type(conn, meal_type)
            
            if not available:
                print(f"В базе нет блюд типа '{meal_type}'. Пожалуйста, добавьте их сначала.")
                return

            print("Доступные блюда:")
            for idx, dish in enumerate(available, 1):
                print(f"{idx}. {dish[1]}")
            
            choice = input_int("Выберите блюдо (введите номер): ", 1, len(available))
            selected_dish = available[choice - 1]
            
            selected_dishes_info.append((day, meal_name, selected_dish[1]))
            selected_dish_ids.append(selected_dish[0])

    print("\n=== Ваш рацион ===")
    for day in range(1, days + 1):
        print(f"День {day}:")
        day_meals = [info for info in selected_dishes_info if info[0] == day]
        for meal in day_meals:
            print(f"  {meal[1].capitalize()}: {meal[2]}")

    print("\n=== Список покупок ===")
    shopping_list = {}
    
    for dish_id in selected_dish_ids:
        details = get_dish_details(conn, dish_id)
        for item in details:
            name, grams = item
            shopping_list[name] = shopping_list.get(name, 0) + grams

    # Сортировка по алфавиту и округление веса до 10 грамм
    for name in sorted(shopping_list.keys()):
        raw_grams = shopping_list[name]
        final_grams = raw_grams * meal_multiply
        # rounded_grams = int(round(raw_grams / 10.0) * 10)
        # final_grams = rounded_grams if rounded_grams > 0 else 10 
        print(f"{name}: {final_grams} г")

def menu_delete_dish(conn):
    print("\n=== Удаление блюда ===")
    dishes = get_all_dishes(conn)
    if not dishes:
        print("База блюд пуста.")
        return
        
    print_table(["ID", "Название", "Тип", "Калории"], dishes)
    dish_id = input_int("Введите ID блюда для удаления (0 для отмены): ", 0)
    if dish_id != 0:
        delete_dish(conn, dish_id)
        print("Блюдо успешно удалено.")

def main():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    
    conn.execute("PRAGMA foreign_keys = 1")
    init_db(conn)

    while True:
        print("\n=== Конструктор рациона питания ===")
        print("1. Добавить блюдо")
        print("2. Показать все блюда")
        print("3. Составить рацион")
        print("4. Удалить блюдо")
        print("0. Выход")
        
        choice = input("Выберите действие: ").strip()
        
        if choice == '1':
            menu_add_dish(conn)
        elif choice == '2':
            menu_show_dishes(conn)
        elif choice == '3':
            menu_create_plan(conn)
        elif choice == '4':
            menu_delete_dish(conn)
        elif choice == '0':
            break
        else:
            print("Неверный ввод. Попробуйте снова.")

    conn.close()

if __name__ == "__main__":
    main()