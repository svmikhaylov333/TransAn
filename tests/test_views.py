from typing import List
from unittest.mock import MagicMock, patch

import pandas as pd

from src.views import filter_by_date, get_last_digits, load_transactions, load_user_settings

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
    filtered = filter_by_date(sample_df, "2022-01-01 23:59:59")
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
