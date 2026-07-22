from unittest.mock import MagicMock, patch

from src.external_api import convert_currency


@patch("src.external_api.requests.get")
def test_convert_currency_usd(mock_get: MagicMock) -> None:
    """Тест конвертации USD в рубли"""
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True, "rates": {"RUB": 75.5}}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    transaction = {"amount": 100, "currency": "USD"}
    result = convert_currency(transaction)
    assert result == 7550.0


@patch("src.external_api.requests.get")
def test_convert_currency_eur(mock_get: MagicMock) -> None:
    """Тест конвертации EUR в рубли"""
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True, "rates": {"RUB": 85.0}}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    transaction = {"amount": 50, "currency": "EUR"}
    result = convert_currency(transaction)
    assert result == 4250.0


def test_convert_currency_rub() -> None:
    """Тест транзакции в рублях - конвертация не требуется"""
    transaction = {"amount": 100.5, "currency": "RUB"}
    result = convert_currency(transaction)
    assert result == 100.5


@patch("src.external_api.requests.get")
def test_convert_currency_api_failure(mock_get: MagicMock) -> None:
    """Тест при ошибке API - возвращает 0"""
    mock_get.side_effect = Exception("API Error")

    transaction = {"amount": 100, "currency": "USD"}
    result = convert_currency(transaction)
    assert result == 0.0


def test_convert_currency_unknown_currency() -> None:
    """Тест с неизвестной валютой - возвращает 0"""
    transaction = {"amount": 100, "currency": "GBP"}
    result = convert_currency(transaction)
    assert result == 0.0


def test_convert_currency_missing_amount() -> None:
    """Тест транзакции без суммы - возвращает 0"""
    transaction = {"currency": "USD"}
    result = convert_currency(transaction)
    assert result == 0.0


def test_convert_currency_invalid_amount() -> None:
    """Тест с некорректной суммой - возвращает 0"""
    transaction = {"amount": "invalid", "currency": "USD"}
    result = convert_currency(transaction)
    assert result == 0.0
