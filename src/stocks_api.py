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


def get_stock_prices(stocks: List[str]) -> List[Dict[str, float]]:
    """Получает цены акций по API"""


    # fallback_prices = {
    #     "AAPL": 339.59,
    #     "AMZN": 231.34,
    #     "GOOGL": 333.83,
    #     "MSFT": 397.30,
    #     "TSLA": 305.95,
    # }
    fallback_prices: Dict[str, float] = {
        "AAPL": 1.0,
        "AMZN": 1.0,
        "GOOGL": 1.0,
        "MSFT": 1.0,
        "TSLA": 1.0,
    }
    stocks_prices: List[Dict[str, float]] = []
    for stock in stocks:
        stocks_prices.append({"stock": stock, "price": fallback_prices.get(stock, 1.0)})

    access_key = os.getenv("STOCKS_API_KEY")
    api_url = os.getenv("STOCKS_API_URL", "https://api.apilayer.net/marketstack/v2")

    if not access_key:
        logger.error("STOCKS_API_KEY не найден")
        return stocks_prices

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
            return stocks_prices

        # цены
        for item in data["data"]:
            symbol = item.get("symbol")
            close_price = item.get("close")
            if symbol and close_price is not None:
                for stock_item in stocks_prices:
                    if stock_item["stock"] == symbol:
                        stock_item["price"] = round(close_price, 2)
                        logger.info(f"{symbol}: ${stock_item['price']}")
                        break
            else:
                logger.warning(f"Для {symbol} не удалось получить цену, используем цену по-умолчанию")

        # for stock in stocks:
        #     if stock not in stocks_prices:
        #         logger.warning(f"Тикер {stock} отсутствует в ответе API")
        #         stocks_prices[stock] = fallback_prices.get(stock, 1)

        return stocks_prices

    except Exception as exp:
        logger.error(f"Ошибка: {exp}")
        return stocks_prices
