import os
import joblib
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
from utils.fetch_data import fetch_data  # ← ✅ Yeni sistemden çekiyoruz

model_dir = "model"
os.makedirs(model_dir, exist_ok=True)

coins = [
    "bitcoin", "ethereum", "solana", "ripple", "binancecoin",
    "dogecoin", "litecoin", "polkadot", "chainlink", "avalanche-2"
]

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
        df = fetch_data(coin, days=365)  # ✅ Yeni fetch_data fonksiyonu
        X, y, scaler = preprocess_data(df)
        model = build_model((X.shape[1], X.shape[2]))
        es = EarlyStopping(patience=3, restore_best_weights=True)
        model.fit(X, y, epochs=10, batch_size=16, verbose=0, callbacks=[es])
        model.save(model_path)
        joblib.dump(scaler, scaler_path)
        print(f"✔ {coin} model saved.\n")
    except Exception as e:
        print(f"❌ Failed for {coin}: {e}\n")
