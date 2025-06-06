import requests
import pandas as pd
import time
from datetime import datetime

CRYPTOCOMPARE_API_KEY = "94d76d5d1459a03c3ddaee417d0cce037a65cf2bc9595c5d1faa6646b8056ef6"

# Coin eşleşmeleri
cc_symbols = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
    "ripple": "XRP",
    "binancecoin": "BNB",
    "dogecoin": "DOGE",
    "litecoin": "LTC",
    "polkadot": "DOT",
    "chainlink": "LINK",
    "avalanche-2": "AVAX"
}

# cache
_data_cache = {}
_data_fetch_times = {}
_DATA_CACHE_DURATION = 300  # saniye

# Güncel fiyat cache
_cached_prices = {}
_last_fetch_time = 0
_CACHE_DURATION = 600  # saniye

#  Geçmiş fiyat verisi
def fetch_data(coin_id="bitcoin", days="365"):
    global _data_cache, _data_fetch_times

    now = time.time()
    cache_key = f"{coin_id}_{days}"

    if cache_key in _data_cache and now - _data_fetch_times.get(cache_key, 0) < _DATA_CACHE_DURATION:
        return _data_cache[cache_key]

    if coin_id not in cc_symbols:
        raise ValueError(f"Unsupported coin ID: {coin_id}")

    symbol = cc_symbols[coin_id]

    url = f"https://min-api.cryptocompare.com/data/v2/histoday"
    params = {
        "fsym": symbol,
        "tsym": "USD",
        "limit": int(days),
        "api_key": CRYPTOCOMPARE_API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("Response") != "Success":
        raise ValueError(f"Invalid API response: {data}")

    raw = data["Data"]["Data"]

    df = pd.DataFrame([{
         "timestamp": pd.to_datetime(item["time"], unit="s"),
         "price": float(item["close"])
    } for item in raw if item.get("close") is not None and float(item["close"]) > 0])


    _data_cache[cache_key] = df
    _data_fetch_times[cache_key] = now
    return df

#  Güncel fiyat verisi
def fetch_current_prices(coin_ids):
    global _cached_prices, _last_fetch_time

    now = time.time()
    if now - _last_fetch_time < _CACHE_DURATION and _cached_prices:
        return _cached_prices

    prices = {}
    symbols = [cc_symbols[cid] for cid in coin_ids if cid in cc_symbols]

    for symbol, coin_id in zip(symbols, coin_ids):
        url = f"https://min-api.cryptocompare.com/data/price"
        params = {
            "fsym": symbol,
            "tsyms": "USD",
            "api_key": CRYPTOCOMPARE_API_KEY
        }

        try:
            response = requests.get(url, params=params)
            data = response.json()
            prices[coin_id] = data.get("USD", None)
        except Exception as e:
            print(f"Error fetching {coin_id}: {e}")

    _cached_prices = prices
    _last_fetch_time = now
    return prices
