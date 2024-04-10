import pytest
from app.crypto_client import get_crypto_curency_icon, get_top_cryptocurrencies
from unittest.mock import patch

@pytest.fixture
def mock_response():
    return {'image': {'thumb': 'https://api.coingecko.com/api/v3/coins/bitcoin'}}

def test_get_crypto_icon_bitcoin_with_mock(mock_response):
    with patch('app.crypto_client.requests.get') as mocked_get:
        mocked_get.return_value.json.return_value = mock_response
        crypto_icon = get_crypto_curency_icon(coin_id='bitcoin')
        expected_url = 'https://api.coingecko.com/api/v3/coins/bitcoin'
        assert crypto_icon == mock_response['image']['thumb'], f"Expected {expected_url} but got {crypto_icon}"

def test_get_top_crypto_currency():
    crypto_currency = get_top_cryptocurrencies()
    assert crypto_currency is not None