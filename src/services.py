import logging
from pathlib import Path
from typing import Dict, List

import pandas as pd

from src.file_processing import read_excel_operations

# ====================
# Настройка логгера
# ====================

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

file_handler = logging.FileHandler(LOG_DIR / "views.log", mode="w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


# Выгодные категории повышенного кешбэка
def get_cashback_categories(excel_path: str = "data/operations.xlsx", top_n: int = 3) -> Dict[str, int]:
    """
      Возвращает топ-N категорий с наибольшим кешбэком.
      Кешбэк = 1 рубль на каждые 100 рублей трат.

    на входе
          excel_path: путь к Excel файлу
          top_n: количество категорий для возврата

    на выходе:
          Список словарей с категориями и кешбэком
    """
    logger.info(f"Поиск топ-{top_n} категорий по кешбэку")

    operations = read_excel_operations(excel_path)
    if not operations:
        logger.warning(f"Не удалось загрузить данные из {excel_path}")
        return {}
    df = pd.DataFrame(operations)
    df.columns = df.columns.str.lower()

    # Приведение сумм
    if "сумма операции" in df.columns:
        df["amount"] = df["сумма операции"].astype(float)
    elif "amount" in df.columns:
        df["amount"] = df["amount"].astype(float)
    else:
        logger.error("Колонка с суммой не найдена")
        return {}

    # категории
    if "категория" in df.columns:
        df["category"] = df["категория"]
    elif "category" in df.columns:
        df["category"] = df["category"]
    else:
        logger.error("Колонка с категорией не найдена")
        return {}

    # Фильтр расходов
    expenses = df[df["amount"] < 0].copy()
    if expenses.empty:
        logger.info("Нет расходов для анализа")
        return {}

    expenses["amount"] = abs(expenses["amount"])

    # расходы по группам
    grouped = expenses.groupby("category")["amount"].sum().reset_index()

    # кешбэк (1 рубль на каждые 100 рублей)
    grouped["cashback"] = (grouped["amount"] // 100).astype(int)

    # сортировка по убыванию
    grouped = grouped.sort_values("cashback", ascending=False)

    # топ N категорий
    top = grouped.head(top_n)

    result = dict(zip(top["category"], top["cashback"]))
    logger.info(f"Найдено {len(result)} категорий с кешбэком")
    return result


# добавить остальные сервисы
