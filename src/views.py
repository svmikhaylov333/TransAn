"""Модуль для генерации JSON ответов веб-страниц"""
import json
import logging
import os
from typing import Dict, List
from pathlib import Path

import pandas as pd
from flake8.discover_files import expand_paths

# ====================
# Файл настройки
# ====================
BASE_DIR = Path(__file__).resolve().parent.parent
SETTINGS_PATH = BASE_DIR / "user_settings.json"
# SETTINGS_PATH = "user_settings.json"
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

def load_user_settings(settings_path:str = SETTINGS_PATH) -> Dict[str,List[str]]:
    """Функция для загрузки пользовательских настроек из JSON-файла"""
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
        logger.info(f"Настройки пользователя загружены {settings}")
        return settings
    except FileNotFoundError:
        logger.warning(f"Файл {settings_path} не найден, используются настройки по умолчанию")
        return {
                  "user_currencies": ["USD", "EUR"],
                  "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
                }
    except Exception as exp:
        logger.error(f"Ошибка {settings_path}: {exp}, используются настройки по умолчанию")
        return {
            "user_currencies": ["USD", "EUR"],
            "user_stocks": ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
        }

print(load_user_settings())
