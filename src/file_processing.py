"""Модуль для считывания финансовых операций из XLSX-файлов."""

import logging
import os
from pathlib import Path
from typing import List

import pandas as pd

# ====================
# Настройка логгера
# ====================

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

file_handler = logging.FileHandler(LOG_DIR / "file_processing.log", mode="w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)

# ====================
# Функции
# ====================


def read_excel_operations(file_path: str) -> List:
    """Функция для чтения операций из Excel файла"""

    try:
        logger.debug(f"Чтение Excel-файла: {file_path}")
        if not os.path.exists(file_path):
            logger.warning(f"Excel-файл {file_path}не найден ")
            return []
        if os.path.getsize(file_path) == 0:
            logger.warning(f"Excel-файл {file_path} пуст")
            return []

        df = pd.read_excel(file_path)
        operations = df.to_dict(orient="records")
        for operation in operations:
            for key, value in operation.items():
                if pd.isna(value):
                    operation[key] = None
        logger.info(f"Успешно загружено {len(operations)} транзакций из Excel")
        return operations

    # except Exception:
    #     return []
    except ValueError as exp:
        logger.error(f"Ошибка чтения Excel-файла {file_path}: {exp}")
        return []
    except Exception as exp:
        logger.error(f"Ошибка при чтении Excel-файла {file_path}: {exp}")
        return []
