import os

def get_db_path():
    """Определяет путь к файлу БД."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "meal_planner.db")

def input_int(prompt, min_val=None, max_val=None):
    """Безопасный ввод целого числа."""
    while True:
        try:
            val = int(input(prompt))
            if min_val is not None and val < min_val:
                print(f"Значение должно быть не меньше {min_val}.")
                continue
            if max_val is not None and val > max_val:
                print(f"Значение должно быть не больше {max_val}.")
                continue
            return val
        except ValueError:
            print("Пожалуйста, введите целое число.")

def print_table(headers, rows):
    """Форматированный вывод таблицы."""
    if not rows:
        print("Нет данных.")
        return
        
    col_widths = [max(len(str(item)) for item in col) for col in zip(headers, *rows)]
    row_format = " | ".join(["{:<" + str(width) + "}" for width in col_widths])
    
    separator = "-" * (sum(col_widths) + 3 * len(headers) - 1)
    
    print(separator)
    print(row_format.format(*headers))
    print(separator)
    for row in rows:
        print(row_format.format(*[str(item) for item in row]))
    print(separator)