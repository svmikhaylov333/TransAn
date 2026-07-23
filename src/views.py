"""Модуль для генерации JSON ответов веб-страниц"""

import json
import logging
import os
from datetime import datetime
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
