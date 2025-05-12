import requests
import pandas as pd
import time
from datetime import datetime, timedelta

# Cache ayarları: geçmiş veri
_data_cache = {}
_data_fetch_times = {}
_DATA_CACHE_DURATION = 300  # 5 dakika

# Cache ayarları: güncel fiyat
_cached_prices = {}
_last_fetch_time = 0
_CACHE_DURATION = 600  # 10 dakika

# Coin ID dönüşüm tablosu (senin projendeki id'lerle eşleştik)
coinpaprika_ids = {
    "bitcoin": "btc-bitcoin",
    "ethereum": "eth-ethereum",
    "solana": "sol-solana",
    "ripple": "xrp-xrp",
    "binancecoin": "bnb-binance-coin",
    "dogecoin": "doge-dogecoin",
    "litecoin": "ltc-litecoin",
    "polkadot": "dot-polkadot",
    "chainlink": "link-chainlink",
    "avalanche-2": "avax-avalanche"
}

# 🔁 Geçmiş fiyat verisini getir (grafik & tahmin için)
def fetch_data(coin_id="bitcoin", days="365"):
    global _data_cache, _data_fetch_times

    now = time.time()
    cache_key = f"{coin_id}_{days}"

    if cache_key in _data_cache and now - _data_fetch_times.get(cache_key, 0) < _DATA_CACHE_DURATION:
        return _data_cache[cache_key]

    if coin_id not in coinpaprika_ids:
        raise ValueError(f"Unsupported coin ID for CoinPaprika: {coin_id}")

    paprika_id = coinpaprika_ids[coin_id]
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=int(days))

    url = f"https://api.coinpaprika.com/v1/coins/{paprika_id}/ohlcv/historical"
    params = {
        "start": start_date.isoformat(),
        "end": end_date.isoformat()
    }

    response = requests.get(url, params=params)
    data = response.json()

    if not isinstance(data, list) or len(data) == 0:
        raise ValueError(f"Invalid or empty data from CoinPaprika: {data}")

    df = pd.DataFrame(data)
    df.rename(columns={"time_open": "timestamp", "close": "price"}, inplace=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df[["timestamp", "price", "volume", "market_cap"]]

    _data_cache[cache_key] = df
    _data_fetch_times[cache_key] = now
    return df

# 🔁 Güncel fiyatları getir (sayfanın alt kısmı için)
def fetch_current_prices(coin_ids):
    global _cached_prices, _last_fetch_time

    now = time.time()
    if now - _last_fetch_time < _CACHE_DURATION and _cached_prices:
        return _cached_prices

    prices = {}

    for coin_id in coin_ids:
        if coin_id not in coinpaprika_ids:
            continue

        paprika_id = coinpaprika_ids[coin_id]
        url = f"https://api.coinpaprika.com/v1/tickers/{paprika_id}"

        try:
            response = requests.get(url)
            data = response.json()
            usd_price = data.get("quotes", {}).get("USD", {}).get("price", None)

            if usd_price is not None:
                prices[coin_id] = usd_price

        except Exception as e:
            print(f"Error fetching {coin_id}: {e}")

    _cached_prices = prices
    _last_fetch_time = now
    return prices
