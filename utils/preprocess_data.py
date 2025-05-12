import numpy as np
from sklearn.preprocessing import MinMaxScaler

def preprocess_data(df, window_size=10):  # ⬅️ 30 gün veriye göre 10 günlük pencere
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df[["price"]])  # (n_samples, 1)

    X, y = [], []

    for i in range(window_size, len(scaled)):
        X.append(scaled[i - window_size:i])  # (window_size, 1)
        y.append(scaled[i])  # (1,)

    X = np.array(X)  # shape: (samples, window_size, 1)
    y = np.array(y)  # shape: (samples, 1)
    return X, y, scaler
