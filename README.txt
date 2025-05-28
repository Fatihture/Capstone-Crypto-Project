# Cryptocurrency Price Forecasting with LSTM

This project is a Flask-based web application that predicts the short-term prices of popular cryptocurrencies using LSTM neural networks. Each coin is trained individually and can be selected from the user interface for live forecast visualization.

## 📦 Project Structure

```
Capstone Crypto Project/
├── app.py                  # Main Flask application
├── train_model.py          # Model training script
├── requirements.txt        # Required Python libraries
├── predictions.csv         # Sample prediction output
├── utils/
│   ├── fetch_data.py       # API-based data collection
│   └── preprocess_data.py  # Data normalization & windowing
├── model/                  # Trained .h5 models & scalers
├── templates/              # HTML templates (index.html)
└── static/                 # CSS & JS assets
```

## 🚀 How to Run the Project

### 1. Clone or Download

```bash

git clone <https://github.com/fatihture/Capstone-Crypto-Project.git>
cd "Capstone Crypto Project"

```

### 2. Install Dependencies

```bash

pip install -r requirements.txt

```

### 3. Train Models (Optional)

If you need to re-train the models:

```bash

python train_model.py

```

### 4. Run the Application

```bash

python app.py

```

Then open your browser and visit:  
**http://127.0.0.1:5000**

## 📈 Features

- Predicts next N-day prices using LSTM models
- Separate model for each coin
- Interactive web interface with Plotly graphs
- CSV download of predictions
- Uses CryptoCompare API for historical & live price data
