import json

from src.reports import spending_by_category
from src.services import get_cashback_categories
from src.views import load_transactions, main_page, save_response_to_json

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
    # excel_path = "data/operations.xlsx"

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


# ====================
# Отчеты
# ====================
#   1. Траты по категории
def run_reports() -> None:
    """Отчет по категории за последние 3 месяца"""

    operations = load_transactions(excel_path)
    if operations.empty:
        print("Нет данных для отчета")
        return
    # date = "2021-12-31 12:00:00"
    cat = "Супермаркеты"
    # spending_by_category(operations, cat, date)
    spending_by_category(operations, cat)


if __name__ == "__main__":
    main()
    run_services()
    run_reports()
