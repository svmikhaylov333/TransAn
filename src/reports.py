"""Модуль формирования отчетов"""

import logging
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional

import pandas as pd

# ====================
# Настройка логгера
# ====================

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
file_handler = logging.FileHandler(LOG_DIR / "reports.log", mode="w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


# ====================
# Декоратор
# ====================
def save_report(func: Callable) -> Callable:
    """Декоратор для сохранения отчета в текстовый файл (Имя_функции.txt)"""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)

        # категория из аргумента
        category = kwargs.get("category") or args[1] if len(args) > 1 else "Неизвестно"

        # дата из аргументов
        date_param = kwargs.get("date") or args[2] if len(args) > 2 else None

        # дата для отчета
        if date_param is None:
            end_date = datetime.now()
        else:
            if " " in date_param:
                end_date = datetime.strptime(date_param, "%Y-%m-%d %H:%M:%S")
            else:
                end_date = datetime.strptime(date_param, "%Y-%m-%d")

        start_date = end_date + timedelta(days=90)

        # Подсчет суммы
        if isinstance(result, pd.DataFrame) and not result.empty:
            total = round(result["amount"].sum(), 2)
            count = len(result)
        else:
            total = 0
            count = 0

        # формирование текстового отчета
        report_text = (
            f"Отчет по тратам за последние 3 месяца (90 дней)\n"
            "\n"
            f"Период: с {start_date.strftime('%d.%m.%Y')} по {end_date.strftime('%d.%m.%Y')}\n"
            f"Категория: {category}\n"
            f"ИТОГО: {total:.2f} руб.\n"
            f"Количество транзакций: {count}\n"
        )

        # сохранение в файл
        try:

            file_path = Path(__file__).parent.parent / "output" / f"{func.__name__}.txt"
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(report_text)

            logger.info(f"Отчет сохранен в output/{func.__name__}.txt")
            print(f"Отчет сохранен в output/{func.__name__}.txt")
        except Exception as exp:
            logger.error(f"Ошибка при сохранении отчета: {exp}")
            print(f"Ошибка при сохранении отчета: {exp}")

        return result

    return wrapper


# ====================
# Функции
# ====================
# 1. Траты по категории
# ====================
@save_report
def spending_by_category(operations: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Возвращает траты по заданной категории за последние 3 месяца."""
    if operations.empty:
        logger.warning("DataFrame с транзакциями пуст")
        return pd.DataFrame()
    if not category:
        logger.warning("Категория не указана")
        return pd.DataFrame()

    required_cols = ["date", "amount", "category"]
    for col in required_cols:
        if col not in operations.columns:
            logger.error(f"Колонка '{col}' не найдена")
            return pd.DataFrame()

    try:
        if date is None:
            end_date = datetime.now()
            logger.info(f"Дата не передана, дата по-умолчанию: {end_date.strftime('%Y-%m-%d')}")
        else:
            if " " in date:
                end_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            else:
                end_date = datetime.strptime(date, "%Y-%m-%d")
            logger.info(f"дата: {end_date.strftime('%Y-%m-%d')}")

        start_date = end_date - timedelta(days=90)

        mask_date = (operations["date"].dt.date >= start_date.date()) & (operations["date"].dt.date <= end_date.date())
        mask_category = operations["category"].str.lower() == category.lower()
        mask_expenses = operations["amount"] < 0
        combined_mask = mask_date & mask_category & mask_expenses

        result: pd.DataFrame = operations.loc[combined_mask].copy()  # type: ignore

        if len(result) > 0:
            result = result.assign(amount=result["amount"].abs())

        logger.info(f"Найдено {len(result)} транзакций по категории '{category}' за последние 3 месяца")
        return result

    except Exception as exp:
        logger.error(f"Ошибка при формировании отчета: {exp}")
        return pd.DataFrame()
