"""Модуль для генерации JSON ответов веб-страниц"""

import json
import logging
import os
from datetime import datetime
from os import access
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from src.file_processing import read_excel_operations

# ====================
# Файл настройки
# ====================
# SETTINGS_PATH = "user_settings.json"
# BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_PATH = Path(__file__).resolve().parent.parent / "user_settings.json"

# ====================
# Настройка логгера
# ====================

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
os.makedirs("logs", exist_ok=True)

file_handler = logging.FileHandler("logs/views.log", mode="w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# # ====================
# # логгер в консоль
# #====================
# console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.DEBUG)
# console_handler.setFormatter(file_formatter)
# logger.addHandler(console_handler)
# ====================


# ====================
# Функции
# ====================
# 1. Загрузка настроек JSON
# ====================


def load_user_settings(settings_path: Path = SETTINGS_PATH) -> Dict[str, List[str]]:
    """Функция для загрузки пользовательских настроек из JSON-файла"""
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
        logger.info(f"Настройки пользователя загружены {settings}")
        return settings  # type: ignore
    except FileNotFoundError:
        logger.warning(f"Файл {settings_path} не найден, используются настройки по умолчанию")
        return {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]}
    except Exception as exp:
        logger.error(f"Ошибка {settings_path}: {exp}, используются настройки по умолчанию")
        return {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]}


# print(load_user_settings())

# ====================
# 2. Загрузка транзакций
# ====================


def load_transactions(excel_path: str) -> pd.DataFrame:
    """Функция загрузки транзакций из Excel"""
    operations = read_excel_operations(excel_path)
    if not operations:
        logger.warning(f"Не удалось загрузить данные из {excel_path}")
        return pd.DataFrame()
    df = pd.DataFrame(operations)
    df.columns = df.columns.str.lower()

    # Приведение дат
    if "дата операции" in df.columns:
        df["date"] = pd.to_datetime(df["дата операции"], dayfirst=True)
    elif "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])

    # Приведение сумм
    if "сумма операции" in df.columns:
        df["amount"] = df["сумма операции"].astype(float)
    elif "amount" in df.columns:
        df["amount"] = df["amount"].astype(float)

    # Приведение номера карты
    if "номер карты" in df.columns:
        df["card_number"] = df["номер карты"]

    # Приведение категории
    if "категория" in df.columns:
        df["category"] = df["категория"]

    # Приведение описания
    if "описание" in df.columns:
        df["description"] = df["описание"]

    logger.info(f"Загружено {len(df)} транзакций из {excel_path}")
    return df


# ====================
# 3. Фильтрация даты
# ====================


def filter_by_date(df: pd.DataFrame, date: str) -> pd.DataFrame:
    """Функция для фильтрации транзакции с начала месяца по указанную дату."""
    final_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    start_date = final_date.replace(day=1, hour=0, minute=0, second=0)
    mask: pd.Series = (df["date"] >= start_date) & (df["date"] <= final_date)
    filtered: pd.DataFrame = df[mask].copy()
    logger.info(f" с {start_date.date()} по {final_date.date()}, найдено {len(filtered)} транзакций")
    return filtered


# ===========================
# 4. Последние 4 цифры карты
# ===========================


def get_last_digits(card_number: Optional[str]) -> str:
    """Функция возвращает 4 последние цифры"""
    try:
        card_number = str(card_number).replace("*", "")
        logger.debug(f"Обработка номера карты: {card_number}")
        if len(card_number) != 4 or not card_number.isdigit():
            raise ValueError("Ошибка формата номера карты")
        else:
            logger.info(f"Успешно получены последние 4 цифры карты: {card_number}")
            return card_number

    except Exception as exp:
        logger.error(f"Ошибка типа данных для card_number={card_number}: {exp}")
        return "0000"


# ====================
# 5. Данные по картам
# ====================


def get_card_transactions(df: pd.DataFrame) -> List[Dict]:
    """
    Функция анализирует транзакции по картам.
    Возвращает список с данными по каждой карте - последние 4 цифры, общая сумма расходов, кешбэк 1р с 100р
    """
    card_data = []

    if "card_number" not in df.columns or "amount" not in df.columns:
        return []

    expenses_df = df[df["amount"] < 0].copy()

    if len(expenses_df) == 0:
        return []

    expenses_df["abs_amount"] = abs(expenses_df["amount"])

    grouped = expenses_df.groupby("card_number").agg({"abs_amount": "sum"}).reset_index()

    for index, row in grouped.iterrows():
        card_number = row["card_number"]
        expenses = float(row["abs_amount"])
        cashback = int(expenses // 100)  # 1 рубль на каждые 100 рублей

        card_data.append(
            {"last_digits": get_last_digits(card_number), "total_expenses": int(expenses), "cashback": cashback}
        )

    logger.info(f"Найдено {len(card_data)} карт")
    return card_data


# ====================
# 6. Топ-5 транзакций
# ====================
def get_top_transactions(df: pd.DataFrame, n: int = 5) -> List[Dict]:
    """Функция Возвращает топ-N (по умолчанию 5) транзакций по платежу (расходу)."""

    df_sorted: pd.DataFrame = df[df["amount"] < 0].copy()  # type: ignore

    if len(df_sorted) == 0:
        return []

    df_sorted["abs_amount"] = abs(df_sorted["amount"])
    df_sorted = df_sorted.sort_values("abs_amount", ascending=False)
    df_sorted = df_sorted.head(n)

    top_transactions = []
    for index, row in df_sorted.iterrows():
        top_transactions.append(
            {
                "date": row["date"].strftime("%d.%m.%Y"),
                "amount": int(row["amount"]),
                "category": row.get("category", "Неизвестно"),
                "description": row.get("description", ""),
            }
        )
    return top_transactions




pass
