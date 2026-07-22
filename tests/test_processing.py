import os
import tempfile
from unittest.mock import MagicMock, patch

import pandas as pd

from src.file_processing import read_excel_operations

# Тесты для EXCEL


@patch("src.file_processing.pd.read_excel")
def test_read_excel_operations_success(mock_read_excel: MagicMock) -> None:
    """Тест чтения Excel-файла"""

    mock_df = pd.DataFrame(
        [{"id": 1, "amount": 100.5, "currency": "USD"}, {"id": 2, "amount": 200.0, "currency": "EUR"}]
    )
    mock_read_excel.return_value = mock_df

    # Создание временного файла)
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
        tmp_file_path = tmp_file.name

    try:
        # записывается test, чтобы файл был не пустым
        with open(tmp_file_path, "w") as f:
            f.write("test")

        result = read_excel_operations(tmp_file_path)
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[0]["amount"] == 100.5
    finally:
        os.unlink(tmp_file_path)


def test_read_excel_operations_not_found() -> None:
    """Тест при отсутствии Excel-файла"""
    result = read_excel_operations("non_existent_file.xlsx")
    assert result == []


def test_read_excel_operations_empty_file() -> None:
    """Тест при пустом Excel-файле"""
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
        tmp_file_path = tmp_file.name

    try:
        result = read_excel_operations(tmp_file_path)
        assert result == []
    finally:
        os.unlink(tmp_file_path)


@patch("src.file_processing.pd.read_excel")
def test_read_excel_operations_value_error(mock_read_excel: MagicMock) -> None:
    """Тест ошибка ValueError"""
    mock_read_excel.side_effect = ValueError("Excel format error")

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
        tmp_file_path = tmp_file.name
        with open(tmp_file_path, "w") as f:
            f.write("test")

    try:
        result = read_excel_operations(tmp_file_path)
        assert result == []
    finally:
        os.unlink(tmp_file_path)


@patch("src.file_processing.pd.read_excel")
def test_read_excel_operations_general_error(mock_read_excel: MagicMock) -> None:
    """Тест ошибка чтения Excel"""
    mock_read_excel.side_effect = Exception("General error")

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
        tmp_file_path = tmp_file.name
        with open(tmp_file_path, "w") as f:
            f.write("test")

    try:
        result = read_excel_operations(tmp_file_path)
        assert result == []
    finally:
        os.unlink(tmp_file_path)


@patch("src.file_processing.pd.read_excel")
def test_read_excel_operations_with_nan(mock_read_excel: MagicMock) -> None:
    """Тест Excel-файла с пустыми значениями"""
    mock_df = pd.DataFrame(
        [
            {"id": 1, "amount": 100.5, "currency": "USD", "from": None},
            {"id": 2, "amount": 200.0, "currency": "EUR", "from": "Visa 1234"},
        ]
    )
    mock_read_excel.return_value = mock_df

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
        tmp_file_path = tmp_file.name
        with open(tmp_file_path, "w") as f:
            f.write("test")

    try:
        result = read_excel_operations(tmp_file_path)
        assert len(result) == 2
        assert result[0]["from"] is None
        assert result[1]["from"] == "Visa 1234"
    finally:
        os.unlink(tmp_file_path)
