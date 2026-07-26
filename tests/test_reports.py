"""Тесты для отчетов"""

from datetime import datetime, timedelta

import pandas as pd

from src.reports import spending_by_category


def test_spending_by_category_success(sample_df: pd.DataFrame) -> None:
    """Тест - успешное получение трат по категории за 3 месяца"""

    result = spending_by_category(sample_df, "Супермаркеты", "2021-12-31 12:00:00")

    assert len(result) == 4
    assert all(result["amount"] > 0)
    assert all(result["category"] == "Супермаркеты")
    assert round(result["amount"].sum(), 2) == 421.06


def test_spending_by_category_no_category(sample_df: pd.DataFrame) -> None:
    """Тест - категория не указана"""
    result = spending_by_category(sample_df, "")
    assert result.empty


def test_spending_by_category_empty_df() -> None:
    """Тест - пустой DataFrame"""
    df = pd.DataFrame()
    result = spending_by_category(df, "Супермаркеты")
    assert result.empty


def test_spending_by_category_no_expenses() -> None:
    """Тест - только доходы, расходов нет"""
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2021-12-31"]),
            "amount": [1000.0],
            "category": ["Зарплата"],
            "description": ["Зарплата"],
        }
    )
    result = spending_by_category(df, "Зарплата", "2021-12-31")
    assert result.empty
