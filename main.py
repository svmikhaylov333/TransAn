import json

from src.views import main_page, save_response_to_json
from src.services import get_cashback_categories
# import sys
# from pathlib import Path


# sys.path.insert(0, str(Path(__file__)))
excel_path = "data/operations.xlsx"
# ====================
# Страницы
# ====================
# 1. Главная
def main() -> None:
    """Главная страница"""
    # date = "2025-07-27 00:00:00"
    date = "2021-12-31 12:00:00"
    #excel_path = "data/operations.xlsx"

    result = main_page(date, str(excel_path))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    save_response_to_json(result)


# ====================
# Сервис
# ====================
#   1. Выгодные категории повышенного кешбэка
def run_services() -> None:
    numbers_cat = 5
    cashback_categories = get_cashback_categories(excel_path, numbers_cat)
    if cashback_categories:
        save_response_to_json(cashback_categories, "output/cashback_categories.json")
    else:
        print("Нет данных для анализа кешбэка")


if __name__ == "__main__":
    main()
    run_services()