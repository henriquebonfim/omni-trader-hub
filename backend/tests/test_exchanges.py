from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from src.exchanges.base import ExchangeError, NetworkError
from src.exchanges.binance_direct import BinanceDirectExchange
from src.exchanges.ccxt_adapter import CCXTExchange
from src.exchanges.factory import ExchangeFactory


def test_factory_returns_ccxt_by_default():
    with patch("src.exchanges.factory.get_config") as mock_get_config:
        mock_config = MagicMock()
        mock_config.exchange.adapter = "ccxt"
        mock_get_config.return_value = mock_config
        
        adapter = ExchangeFactory.create_exchange()
        assert isinstance(adapter, CCXTExchange)


def test_factory_returns_binance_direct_when_configured():
    with patch("src.exchanges.factory.get_config") as mock_get_config:
        mock_config = MagicMock()
        mock_config.exchange.adapter = "binance_direct"
        mock_get_config.return_value = mock_config
        
        with patch("src.exchanges.factory.BinanceDirectExchange") as MockBinanceDirect:
            MockBinanceDirect.return_value = MagicMock(spec=BinanceDirectExchange)
            ExchangeFactory.create_exchange()
            assert MockBinanceDirect.called


def test_factory_fallbacks_to_ccxt_on_error():
    with patch("src.exchanges.factory.get_config") as mock_get_config:
        mock_config = MagicMock()
        mock_config.exchange.adapter = "binance_direct"
        mock_get_config.return_value = mock_config
        
        with patch("src.exchanges.factory.BinanceDirectExchange", side_effect=Exception("Init failed")):
            adapter = ExchangeFactory.create_exchange()
            assert isinstance(adapter, CCXTExchange)


@pytest.fixture
def mock_config():
    config = MagicMock()
    config.exchange.paper_mode = False
    config.exchange.testnet = True
    config.exchange.leverage = 3
    config.exchange.margin_type = "isolated"
    config.trading.symbol = "BTC/USDT:USDT"
    config.trading.timeframe = "15m"
    return config


@pytest.fixture
def binance_direct(mock_config):
    with patch("src.exchanges.binance_direct.get_config", return_value=mock_config), \
         patch.dict("os.environ", {"BINANCE_API_KEY": "test_key", "BINANCE_SECRET": "test_secret"}):
        exchange = BinanceDirectExchange()
        return exchange


def test_binance_direct_initialization(binance_direct):
    assert binance_direct.base_url == "https://testnet.binancefuture.com"
    assert binance_direct.api_key == "test_key"
    assert binance_direct.secret == "test_secret"


def test_binance_direct_sign(binance_direct):
    params = {"symbol": "BTCUSDT", "timestamp": 1600000000000}
    signature = binance_direct._sign(params)
    assert isinstance(signature, str)
    assert len(signature) == 64  # SHA256 hex length


@pytest.mark.asyncio
async def test_binance_direct_request_network_error(binance_direct):
    with patch("aiohttp.ClientSession.get", side_effect=aiohttp.ClientError("Network timeout")):
        with pytest.raises(NetworkError) as excinfo:
            await binance_direct._request("GET", "/fapi/v1/exchangeInfo")
        assert "Network timeout" in str(excinfo.value)


@pytest.mark.asyncio
async def test_binance_direct_request_exchange_error(binance_direct):
    mock_response = AsyncMock()
    mock_response.status = 400
    mock_response.json.return_value = {"code": -1121, "msg": "Invalid symbol."}

    class MockContextManager:
        async def __aenter__(self):
            return mock_response
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    with patch("aiohttp.ClientSession.get", return_value=MockContextManager()):
        with pytest.raises(ExchangeError) as excinfo:
            await binance_direct._request("GET", "/fapi/v1/exchangeInfo")
        assert "Invalid symbol." in str(excinfo.value)

