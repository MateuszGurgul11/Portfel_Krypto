import pytest
import crypto_client

def test_get_crypto_icon_bitcoin():
    crypto_icon = crypto_client.get_crypto_curency_icon(coin_id='bitcoin')
    assert crypto_icon is not None
