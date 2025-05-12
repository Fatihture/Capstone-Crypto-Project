from flask import Flask, render_template, request, send_file
import numpy as np
import pandas as pd
import os
import joblib
from tensorflow.keras.models import load_model
from utils.fetch_data import fetch_data, fetch_current_prices
from utils.preprocess_data import preprocess_data
import plotly.graph_objs as go
import plotly
import json
from sklearn.metrics import mean_squared_error

app = Flask(__name__)

COINS = {
    "bitcoin": "Bitcoin",
    "ethereum": "Ethereum",
    "solana": "Solana",
    "ripple": "Ripple",
    "binancecoin": "Binance Coin",
    "dogecoin": "Dogecoin",
    "litecoin": "Litecoin",
    "polkadot": "Polkadot",
    "chainlink": "Chainlink",
    "avalanche-2": "Avalanche"
}

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = []
    graphJSON_pred = None
    graphJSON_past = None
    selected_coin = "bitcoin"
    future_days = 15
    csv_ready = False
    rmse_score = None
    current_prices = fetch_current_prices(list(COINS.keys()))
    past_prices = []
    original_df = None

    if request.method == "POST":
        selected_coin = request.form["coin"]
        future_days = int(request.form["days"])

        try:
            df = fetch_data(selected_coin).copy(deep=True)
            original_df = df.copy(deep=True)

            X, y, scaler = preprocess_data(df)

            model_path = f"model/{selected_coin}_model.h5"
            scaler_path = f"model/{selected_coin}_scaler.save"

            if not os.path.exists(model_path) or not os.path.exists(scaler_path):
                raise FileNotFoundError("Model or scaler file not found.")

            model = load_model(model_path, compile=False)
            scaler = joblib.load(scaler_path)

            # Tahmin
            last_window = X[-1:]
            predictions_scaled = []

            for _ in range(future_days):
                pred = model.predict(last_window, verbose=0)[0]
                predictions_scaled.append(pred[0])
                next_input = np.append(last_window[0][1:], [pred], axis=0)
                last_window = np.array([next_input])

            prediction_prices = scaler.inverse_transform(np.array(predictions_scaled).reshape(-1, 1)).flatten()
            dates = pd.date_range(start=original_df["timestamp"].iloc[-1] + pd.Timedelta(days=1), periods=future_days)
            prediction = list(zip(dates.date, prediction_prices))

            # CSV
            csv_df = pd.DataFrame(prediction, columns=["Date", "Predicted Price (USD)"])
            csv_df.to_csv("predictions.csv", index=False)
            csv_ready = True

            # RMSE
            last_15_X = X[-15:]
            real_15 = scaler.inverse_transform(y[-15:])
            predicted_15 = scaler.inverse_transform(model.predict(last_15_X, verbose=0))
            rmse_score = round(np.sqrt(mean_squared_error(real_15, predicted_15)), 2)

            # Grafik - Tahmin
            fig_pred = go.Figure()
            fig_pred.add_trace(go.Scatter(
                x=[str(date) for date, _ in prediction],
                y=[float(price) for _, price in prediction],
                mode='lines+markers',
                name='Prediction',
                marker=dict(color='red'),
                line=dict(width=2),
                hovertemplate='Date: %{x}<br>Price: %{y:.2f} USD'
            ))
            fig_pred.update_layout(
                title=f"{COINS[selected_coin]} Price Forecast (Prediction)",
                xaxis_title='Date',
                yaxis_title='Price (USD)',
                template='plotly_white'
            )
            graphJSON_pred = json.dumps(fig_pred, cls=plotly.utils.PlotlyJSONEncoder)

            # Geçmiş veri tablosu için
            past_prices = original_df[["timestamp", "price"]].tail(30).values.tolist()

        except Exception as e:
            prediction = f"Error: {str(e)}"

    return render_template("index.html",
        prediction=prediction,
        coins=COINS,
        selected_coin=selected_coin,
        future_days=future_days,
        graphJSON_pred=graphJSON_pred,
        graphJSON_past=graphJSON_past,
        csv_ready=csv_ready,
        rmse_score=rmse_score,
        current_prices=current_prices,
        past_prices=past_prices
    )

@app.route("/download")
def download_csv():
    return send_file("predictions.csv", as_attachment=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
