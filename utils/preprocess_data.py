import numpy as np
from sklearn.preprocessing import MinMaxScaler

def preprocess_data(df, window_size=10):  # 30 gün veri 10 günlük pencere
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df[["price"]]) 

    X, y = [], []

    for i in range(window_size, len(scaled)):
        X.append(scaled[i - window_size:i]) 
        y.append(scaled[i])  

    X = np.array(X)  
    y = np.array(y)  
    return X, y, scaler
