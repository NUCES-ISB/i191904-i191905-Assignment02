import datetime
import pandas as pd
from prophet import Prophet
from psx import stocks, tickers
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
STOCK_NAME = "FFC"

_ = tickers()
data_frame = stocks(
    STOCK_NAME, start=datetime.date(2020, 1, 1), end=datetime.date.today()
)
df = pd.DataFrame(
    {
        "ds": [x.strftime("%Y-%m-%d") for x in data_frame.index],
        "y": data_frame["Close"],
    }
)
df.index = list(range(len(df)))
forecasting_model = Prophet()
forecasting_model.fit(df)


@app.route("/api/date-prediction", methods=["POST"])
def date_prediction_api():
    """
    API route for date input prediction.
    """
    if request.method == "POST":
        if request.form.get("date"):
            date = request.form.get("date")
            forecast = forecasting_model.predict(pd.DataFrame({"ds": [date]}))
            print({"prediction": forecast.iloc[-1, 1]})
            return jsonify({"prediction": forecast.iloc[-1, 1]})
        return jsonify({"prediction": "Error in getting prediction. Try again."})
    return jsonify({"prediction": "Error in getting prediction. Try again."})


@app.route("/date-prediction")
def date_prediction():
    """
    Date prediction page route.
    """
    return render_template("prediction.html")


@app.route("/api/retrain")
def retrain_model():
    """
    API route for triggering model retrain.
    """
    global data_frame
    data_frame = stocks(
        STOCK_NAME, start=datetime.date(2020, 1, 1), end=datetime.date.today()
    )
    return jsonify({"message": "Training complete. The page will be refreshed."})


app.run(debug=True, use_debugger=False, use_reloader=False, host="0.0.0.0")
