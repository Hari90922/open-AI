from flask import Flask, jsonify
import requests
import openai
import os

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
STOCK_SYMBOL = "AAPL"

@app.route("/api/data")
def get_data():
    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={STOCK_SYMBOL}&interval=1min&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url)
        data = response.json()
        time_series = data["Time Series (1min)"]
        latest_timestamp = sorted(time_series.keys())[-1]
        latest_data = time_series[latest_timestamp]
        current_price = float(latest_data["1. open"])

        prompt = f"Analyze the stock trend for {STOCK_SYMBOL} with the current price at {current_price}. What should a trader consider in the next hour?"

        ai_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a stock market analyst."},
                {"role": "user", "content": prompt}
            ]
        )
        analysis = ai_response.choices[0].message["content"]
        return jsonify({"symbol": STOCK_SYMBOL, "price": current_price, "analysis": analysis})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")