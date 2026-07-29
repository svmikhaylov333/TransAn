import os
from pathlib import Path
from typing import Any, Dict
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

# ====================
# Настройка логгера
# ====================

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

file_handler = logging.FileHandler(LOG_DIR / "external_api.log", mode="w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)



def convert_currency(transaction: Dict[str, Any]) -> float:
    """
    Конвертирует сумму транзакции в рубли.

    """
    logger.info("начало конвертации")
    # Получаем сумму и валюту из транзакции
    amount = transaction.get("amount")
    currency = transaction.get("currency", "RUB")

    # Проверка, что сумма есть. если нет, то 0
    if amount is None:
        logger.warning("Сумма отсутствует")
        return 0.0

    # Преобразование в число
    try:
        amount = float(amount)
    except (ValueError, TypeError) as exp:
        logger.error(f"Ошибка преобразования суммы: {exp}")
        return 0.0

    if amount <= 0:
        return 0.0

    # Если рубли, то не конвертируем
    if currency.upper() == "RUB":
        return round(amount, 2)

    # конвертация USD и EUR
    if currency.upper() in ["USD", "EUR"]:

        api_key = os.getenv("EXCHANGE_RATES_API_KEY")
        # api_url = os.getenv("EXCHANGE_RATES_API_URL", "https://api.exchangeratesapi.io/v1")
        api_url = os.getenv("EXCHANGE_RATES_API_URL")

        # Провекрка ключа. если нет возрат 0.0
        if not api_key:
            logger.error("EXCHANGE_RATES_API_KEY не найден в .env")
            return 0.0

        try:
            # Формирование запроса к API для получения курса
            url = f"{api_url}/latest"
            params = {"base": currency.upper(), "symbols": "RUB"}
            headers = {"apikey": api_key}
            response = requests.get(url, params=params, headers=headers, timeout=10)

            logger.info(f"Статус ответа: {response.status_code}")
            logger.debug(f"Заголовки ответа: {response.headers}")

            # статус
            response.raise_for_status()

            data = response.json()
            logger.debug(f"Ответ API: {data}")
            if not data.get("success", False):
                return 0.0

            # Получаем курс рубля
            rates = data.get("rates", {})
            rate = float(rates.get("RUB", 0.0))

            logger.info(f"Курс {currency}/RUB: {rate}")

            # Если курс получен, конвертируем сумму
            if rate > 0:
                return round(amount * rate, 2)
            return 0.0

        except Exception:
            return 0.0

    # Для других валют возвращаем 0
    return 0.0
