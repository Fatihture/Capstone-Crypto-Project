import requests
import pandas as pd
import time  # ⬅️ Cache için eklendi

def fetch_data(coin_id="bitcoin", days="365"):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "daily"
    }
    response = requests.get(url, params=params)
    data = response.json()

    if "prices" not in data:
        raise ValueError(f"Missing 'prices' in API response: {data}")

    prices = data["prices"]
    volumes = data["total_volumes"]
    market_caps = data["market_caps"]

    df = pd.DataFrame({
        "timestamp": [x[0] for x in prices],
        "price": [x[1] for x in prices],
        "volume": [x[1] for x in volumes],
        "market_cap": [x[1] for x in market_caps],
    })
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

# 🔄 Cache ayarları
_cached_prices = {}
_last_fetch_time = 0
_CACHE_DURATION = 600  # saniye (10 dakika)

# 🔄 Güncel fiyatları getir (cache'li)
def fetch_current_prices(coin_ids):
    global _cached_prices, _last_fetch_time

    now = time.time()
    if now - _last_fetch_time < _CACHE_DURATION and _cached_prices:
        return _cached_prices

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": ",".join(coin_ids),
        "vs_currencies": "usd"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        prices = {}
        for coin_id in coin_ids:
            price = data.get(coin_id, {}).get("usd", None)
            if price is not None:
                prices[coin_id] = price

        # Cache güncelle
        _cached_prices = prices
        _last_fetch_time = now

        return prices

    except Exception as e:
        print(f"Error fetching prices: {e}")
        return _cached_prices if _cached_prices else {}
