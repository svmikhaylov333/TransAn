import logging
import os
from pathlib import Path
from typing import Dict, List

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

file_handler = logging.FileHandler(LOG_DIR / "stocks_api.log", mode="w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def get_stock_prices(stocks: List[str]) -> Dict[str, float]:
    """Получает цены акций по API"""

    stocks_prices = {}
    access_key = os.getenv("STOCKS_API_KEY")
    api_url = os.getenv("STOCKS_API_URL", "https://api.apilayer.net/marketstack/v2")

    if not access_key:
        logger.error("STOCKS_API_KEY не найден")
        return {stock: 0.0 for stock in stocks}

    try:
        url = f"{api_url}/eod"
        params: dict[str, str | int] = {
            "access_key": access_key,
            "symbols": ",".join(stocks),
            "limit": 5,
            "sort": "DESC",
        }
        logger.info(f"Запрос цен у Marketstack для: {', '.join(stocks)}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Проверка получения данных
        if not data.get("data"):
            logger.error("В ответе Marketstack нет данных")
            return {stock: 0.0 for stock in stocks}

        # цены
        for item in data["data"]:
            symbol = item.get("symbol")
            close_price = item.get("close")

            if symbol and close_price is not None:
                stocks_prices[symbol] = round(close_price, 2)
                logger.info(f"{symbol}: ${stocks_prices[symbol]}")
            else:
                logger.warning(f"Для {symbol} не удалось получить цену")
                stocks_prices[symbol] = 0.0

        for stock in stocks:
            if stock not in stocks_prices:
                logger.warning(f"Тикер {stock} отсутствует в ответе API")
                stocks_prices[stock] = 0.0

        return stocks_prices

    except Exception as exp:
        logger.error(f"Ошибка: {exp}")
        return {stock: 0.0 for stock in stocks}
