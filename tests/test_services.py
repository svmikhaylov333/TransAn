"""Тесты для сервисов"""

from unittest.mock import MagicMock, patch

import pandas as pd

from src.services import get_cashback_categories

# ====================
# Выгодные категории кешбэка
# Тесты с mock для read_excel_operations
# ====================


@patch("src.services.read_excel_operations")
def test_get_cashback_categories_success(mock_read: MagicMock, sample_df: pd.DataFrame) -> None:
    """Тест - успешное получение топ-3 категорий по кешбэку"""

    test_data = sample_df.to_dict("records")
    mock_read.return_value = test_data

    result = get_cashback_categories("test.xlsx", 3)

    assert len(result) == 2
    assert result["Различные товары"] == 5
    assert result["Супермаркеты"] == 4


@patch("src.services.read_excel_operations")
def test_get_cashback_categories_empty_file(mock_read: MagicMock) -> None:
    """Тест - файл пустой"""
    mock_read.return_value = []
    result = get_cashback_categories("test.xlsx", 3)
    assert result == {}


@patch("src.services.read_excel_operations")
def test_get_cashback_categories_no_expenses(mock_read: MagicMock) -> None:
    """Тест - нет расходов"""

    test_data = [
        {"сумма операции": 1000, "категория": "Зарплата"},
    ]
    mock_read.return_value = test_data
    result = get_cashback_categories("test.xlsx", 3)
    assert result == {}


@patch("src.services.read_excel_operations")
def test_get_cashback_categories_missing_columns(mock_read: MagicMock) -> None:
    """Тест - нет нужной колонки"""

    test_data = [
        {"id": 1, "value": 100},
    ]
    mock_read.return_value = test_data
    result = get_cashback_categories("test.xlsx", 3)
    assert result == {}
