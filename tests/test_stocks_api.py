from unittest.mock import MagicMock, patch

from src.stocks_api import get_stock_prices


@patch("src.stocks_api.os.getenv")
def test_get_stock_prices_no_key(mock_getenv: MagicMock) -> None:
    """Тест - нет API-ключа."""
    mock_getenv.return_value = None

    result = get_stock_prices(["AAPL", "MSFT"])

    assert len(result) == 2
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == 1.0
    assert result[1]["stock"] == "MSFT"
    assert result[1]["price"] == 1.0


@patch("src.stocks_api.requests.get")
@patch("src.stocks_api.os.getenv")
def test_get_stock_prices_success(mock_getenv: MagicMock, mock_get: MagicMock) -> None:
    """Тест - успешное получение цен."""
    mock_getenv.return_value = "test_key"

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [{"symbol": "AAPL", "close": 175.34}, {"symbol": "MSFT", "close": 420.12}]
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = get_stock_prices(["AAPL", "MSFT"])

    assert len(result) == 2
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == 1.0
    assert result[1]["stock"] == "MSFT"
    assert result[1]["price"] == 1.0


@patch("src.stocks_api.requests.get")
@patch("src.stocks_api.os.getenv")
def test_get_stock_prices_api_error(mock_getenv: MagicMock, mock_get: MagicMock) -> None:
    """Тест - ошибка API."""
    mock_getenv.return_value = "test_key"
    mock_get.side_effect = Exception("API Error")

    result = get_stock_prices(["AAPL"])

    assert len(result) == 1
    assert result[0]["stock"] == "AAPL"
    assert result[0]["price"] == 1.0
