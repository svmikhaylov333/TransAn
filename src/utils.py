import logging
from datetime import datetime
from pathlib import Path

# настройка логирования

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

file_handler = logging.FileHandler(LOG_DIR / "utils.log", mode="w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")


def greeting(time: str) -> str:
    """Функция, которая возвращает приветствие в зависимости от времени
    на входе время в формате 'YYYY-MM-DD HH:MM:SS'
    на выходе: приветствие"""
    try:
        dt = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        hour = dt.hour

        if 6 <= hour < 12:
            return "Доброе утро!"
        elif 12 <= hour < 18:
            return "Добрый день!"
        elif 18 <= hour < 23:
            return "Добрый вечер!"
        else:
            return "Доброй ночи!"
    except ValueError as exp:
        logger.error(f"Ошибка парсинга даты: {exp}")
        return "Здравствуйте!"
