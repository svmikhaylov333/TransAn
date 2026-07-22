import os
from typing import Any, Dict

import requests
from dotenv import load_dotenv

load_dotenv()


def convert_currency(transaction: Dict[str, Any]) -> float:
    """
    Конвертирует сумму транзакции в рубли.

    """
    # Получаем сумму и валюту из транзакции
    amount = transaction.get("amount")
    currency = transaction.get("currency", "RUB")

    # Проверка, что сумма есть. если нет, то 0
    if amount is None:
        return 0.0

    # Преобразование в число
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return 0.0

    if amount <= 0:
        return 0.0

    # Если рубли, то не конвертируем
    if currency.upper() == "RUB":
        return round(amount, 2)

    # конвертация USD и EUR
    if currency.upper() in ["USD", "EUR"]:

        api_key = os.getenv("EXCHANGE_RATES_API_KEY")
        api_url = os.getenv("EXCHANGE_RATES_API_URL", "https://api.exchangeratesapi.io/v1")

        # Провекрка ключа. если нет возрат 0.0
        if not api_key:
            return 0.0

        try:
            # Формирование запроса к API для получения курса
            url = f"{api_url}/latest"
            params = {"base": currency.upper(), "symbols": "RUB"}
            headers = {"apikey": api_key}
            response = requests.get(url, params=params, headers=headers, timeout=10)
            # статус
            response.raise_for_status()

            data = response.json()
            if not data.get("success", False):
                return 0.0

            # Получаем курс рубля
            rates = data.get("rates", {})
            rate = float(rates.get("RUB", 0.0))

            # Если курс получен, конвертируем сумму
            if rate > 0:
                return round(amount * rate, 2)
            return 0.0

        except Exception:
            return 0.0

    # Для других валют возвращаем 0
    return 0.0
