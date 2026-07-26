import json
import tempfile
from pathlib import Path
from typing import Dict, List
from unittest.mock import MagicMock, patch

import pandas as pd

from src.views import (
    filter_by_date,
    get_card_transactions,
    get_currency_rates,
    get_last_digits,
    get_top_transactions,
    load_transactions,
    load_user_settings,
    main_page,
    save_response_to_json,
)

# Тесты функции get_last_digits


def test_last_digits_with_star() -> None:
    """Тест - Номер карты со звёздочкой — возвращает 4 последние цифры."""
    assert get_last_digits("*7197") == "7197"
    assert get_last_digits("*5091") == "5091"


def test_last_digits_normal() -> None:
    """Тест - Номер из 4 цифр — возвращает его же."""
    assert get_last_digits("7197") == "7197"


def test_last_digits_invalid() -> None:
    """Тест - Неверный формат — возвращает '0000'."""
    assert get_last_digits("123") == "0000"
    assert get_last_digits("abc") == "0000"
    assert get_last_digits(None) == "0000"


# Тесты функции filter_by_date


def test_filter_by_date_all(sample_df: pd.DataFrame) -> None:
    """Тест - Фильтрация за весь день — возвращает 5 транзакций."""
    filtered = filter_by_date(sample_df, "2021-12-31 23:59:59")
    assert len(filtered) == 5


def test_filter_by_date_partial(sample_df: pd.DataFrame) -> None:
    """Тест - Фильтрация до 12:00 — возвращает 1 транзакции."""
    filtered = filter_by_date(sample_df, "2021-12-31 12:00:00")
    assert len(filtered) == 1


def test_filter_by_date_empty(sample_df: pd.DataFrame) -> None:
    """Тест - Фильтрация по дате вне диапазона — возвращает пустой DataFrame."""
    filtered = filter_by_date(sample_df, "2026-01-01 23:59:59")
    assert filtered.empty


# Тесты функции load_transactions


@patch("src.views.read_excel_operations")
def test_load_transactions_success(mock_read: MagicMock, sample_transactions: List) -> None:
    """Тест- Успешная загрузка"""
    mock_read.return_value = sample_transactions
    df = load_transactions("data/operations.xlsx")
    assert len(df) == 5
    assert "date" in df.columns


@patch("src.views.read_excel_operations")
def test_load_transactions_empty(mock_read: MagicMock) -> None:
    """Тест - Пустой файл"""
    mock_read.return_value = []
    df = load_transactions("data/operations.xlsx")
    assert df.empty


# Тесты функции load_user_settings
@patch("src.views.Path.exists")
def test_load_user_settings_default(mock_exists: MagicMock) -> None:
    """Тест - Файл настроек не найден — возвращаются настройки по умолчанию."""
    mock_exists.return_value = False
    settings = load_user_settings()
    assert settings["user_currencies"] == ["USD", "EUR"]


@patch("src.views.open")
@patch("src.views.Path.exists")
def test_load_user_settings_success(mock_exists: MagicMock, mock_open: MagicMock) -> None:
    """Тест - Файл найден и корректен — возвращаются настройки из JSON."""
    mock_exists.return_value = True
    mock_file = MagicMock()
    mock_file.__enter__.return_value.read.return_value = '{"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL"]}'
    mock_open.return_value = mock_file
    settings = load_user_settings()
    assert settings["user_stocks"] == ["AAPL"]


# Тест - сохранение JSON в файл
def test_save_response_to_json() -> None:
    """Тест - сохранение JSON в файл."""

    # создание тестовых данных
    test_data = {"test": "data", "number": 123}

    # создание тест файл
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name

    try:

        save_response_to_json(test_data, tmp_path)
        assert Path(tmp_path).exists()

        with open(tmp_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["test"] == "data"
            assert data["number"] == 123

    finally:
        # Удаление временного файла
        Path(tmp_path).unlink(missing_ok=True)


# тесты для для get_currency_rates


@patch("src.views.convert_currency")
def test_get_currency_rates_success(mock_convert: MagicMock) -> None:
    """Тест - успешное получение курсов."""
    mock_convert.side_effect = [78.03, 88.89, 0.0]

    result = get_currency_rates(["USD", "EUR", "QQQ"])

    assert result["USD"] == 78.03
    assert result["EUR"] == 88.89
    assert "QQQ" not in result


def test_get_currency_rates_empty() -> None:
    """Тест - пустой список валют."""
    result = get_currency_rates([])
    assert result == {}


# Тесты для get_card_transactions


def test_get_card_transactions(sample_df: pd.DataFrame) -> None:
    """Тест - общий расход, кэшбэк"""
    result = get_card_transactions(sample_df)

    assert len(result) == 2
    card_7197 = next(c for c in result if c["last_digits"] == "7197")
    assert card_7197["total_expenses"] == 421.06
    assert card_7197["cashback"] == 4.21

    card_5091 = next(c for c in result if c["last_digits"] == "5091")
    assert card_5091["total_expenses"] == 564.0
    assert card_5091["cashback"] == 5.64


def test_get_card_transactions_empty() -> None:
    """Тест - пустой DataFrame."""

    df = pd.DataFrame()
    result = get_card_transactions(df)
    assert result == []


def test_get_card_transactions_no_card_column() -> None:
    """Тест - нет колонки card_number."""

    df = pd.DataFrame({"amount": [-100, -200]})
    result = get_card_transactions(df)
    assert result == []


# Тесты для get_top_transactions


def test_get_top_transactions_success(sample_df: pd.DataFrame) -> None:
    """Тест - успешное получение топ-5."""
    result: List[Dict] = get_top_transactions(sample_df, 3)

    assert len(result) == 3
    assert result[0]["amount"] == -564.0
    assert result[0]["category"] == "Различные товары"
    assert result[0]["description"] == "Ozon.ru"
    assert result[1]["amount"] == -160.89


def test_get_top_transactions_empty() -> None:
    """Тест - пустой DataFrame."""

    df = pd.DataFrame(columns=["amount", "date"])
    result = get_top_transactions(df)
    assert result == []


# def test_get_top_transactions_no_expenses() -> None:
#     """Тест - нет расходов."""
#
#     df = pd.DataFrame({"amount": [100, 200], "date": pd.to_datetime(["2026-07-01", "2026-07-02"])})
#     result = get_top_transactions(df)
#     assert result == []


# Тесты для main_page


@patch("src.views.load_transactions")
@patch("src.views.filter_by_date")
@patch("src.views.load_user_settings")
@patch("src.views.get_currency_rates")
@patch("src.views.get_stock_prices")
@patch("src.views.get_card_transactions")
@patch("src.views.get_top_transactions")
@patch("src.views.greeting")
def test_main_page_success(
    mock_greeting: MagicMock,
    mock_top: MagicMock,
    mock_cards: MagicMock,
    mock_stocks: MagicMock,
    mock_currency: MagicMock,
    mock_settings: MagicMock,
    mock_filter: MagicMock,
    mock_load: MagicMock,
) -> None:
    """Тест - успешная генерация главной страницы."""

    mock_load.return_value = MagicMock()
    mock_load.return_value.empty = False

    mock_filter.return_value = MagicMock()
    mock_filter.return_value.empty = False

    mock_greeting.return_value = "Добрый день!"
    mock_cards.return_value = [{"last_digits": "7197", "total_expenses": 1500, "cashback": 15}]
    mock_top.return_value = [{"date": "01.01.2021", "amount": -500, "category": "Еда", "description": "Магнит"}]
    mock_currency.return_value = {"USD": 90.0}
    mock_stocks.return_value = {"AAPL": 175.34}
    mock_settings.return_value = {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}

    result = main_page("2021-01-01 12:00:00")

    assert "greeting" in result
    assert "cards" in result
    assert "top_transactions" in result
    assert "currency_rates" in result
    assert "stock_prices" in result
    assert result["greeting"] == "Добрый день!"


@patch("src.views.load_transactions")
def test_main_page_empty_data(mock_load: MagicMock) -> None:
    """Тест - пустые данные"""
    mock_load.return_value = MagicMock()
    mock_load.return_value.empty = True

    result = main_page("2021-01-01 12:00:00")

    assert result["cards"] == []
    assert result["top_transactions"] == []
    assert result["currency_rates"] == {}
    assert result["stock_prices"] == {}
    assert "greeting" in result


@patch("src.views.load_transactions")
@patch("src.views.filter_by_date")
def test_main_page_filtered_empty(mock_filter: MagicMock, mock_load: MagicMock) -> None:
    """Тест - после фильтрации данных нет (df_filtered.empty == True)."""
    mock_load.return_value = MagicMock()
    mock_load.return_value.empty = False

    mock_filter.return_value = MagicMock()
    mock_filter.return_value.empty = True

    result = main_page("2021-01-01 12:00:00")

    assert result["cards"] == []
    assert result["top_transactions"] == []
    assert result["currency_rates"] == {}
    assert result["stock_prices"] == {}
    assert "greeting" in result


@patch("src.views.load_transactions")
def test_main_page_error(mock_load: MagicMock) -> None:
    """Тест - ошибка при загрузке."""
    mock_load.side_effect = Exception("Test error")

    result = main_page("2021-01-01 12:00:00")

    assert "error" in result
    assert result["error"] == "Test error"
