import os
import joblib
import numpy as np
import pandas as pd
import requests
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.callbacks import EarlyStopping

model_dir = "model"
os.makedirs(model_dir, exist_ok=True)

coins = [
    "bitcoin", "ethereum", "solana", "ripple", "binancecoin",
    "dogecoin", "litecoin", "polkadot", "chainlink", "avalanche-2"
]

def fetch_data(coin_id="bitcoin", days="365"):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "daily"
    }
    response = requests.get(url, params=params)
    data = response.json()
    if 'prices' not in data:
        raise ValueError(f"API error: {data}")
    df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

def preprocess_data(df):
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df[["price"]])
    X, y = [], []
    for i in range(30, len(scaled)):
        X.append(scaled[i-30:i])
        y.append(scaled[i])
    return np.array(X), np.array(y), scaler

def build_model(input_shape):
    model = Sequential()
    model.add(LSTM(50, return_sequences=False, input_shape=input_shape))
    model.add(Dense(1))
    model.compile(optimizer="adam", loss="mse")
    return model

for coin in coins:
    model_path = os.path.join(model_dir, f"{coin}_model.h5")
    scaler_path = os.path.join(model_dir, f"{coin}_scaler.save")

    if os.path.exists(model_path) and os.path.exists(scaler_path):
        print(f"✅ {coin} already trained. Skipping.")
        continue

    try:
        print(f"▶ Training model for: {coin}")
        df = fetch_data(coin)
        X, y, scaler = preprocess_data(df)
        model = build_model((X.shape[1], X.shape[2]))
        es = EarlyStopping(patience=3, restore_best_weights=True)
        model.fit(X, y, epochs=10, batch_size=16, verbose=0, callbacks=[es])
        model.save(model_path)
        joblib.dump(scaler, scaler_path)
        print(f"✔ {coin} model saved.\n")
    except Exception as e:
        print(f"❌ Failed for {coin}: {e}\n")
