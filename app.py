import datetime
import requests
import pandas as pd
from prophet import Prophet
from bs4 import BeautifulSoup as bs
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


@app.errorhandler(404)
def page_not_found(_):
    """
    Error handler route.
    """
    return render_template("error.html"), 404


@app.route("/api/trend")
def trend_api():
    """
    API route for stock trends data.
    """
    data = {
        "x": [
            datetime.datetime.utcfromtimestamp(x / 10**9).strftime("%Y-%m-%d")
            for x in data_frame.index.to_numpy().tolist()
        ],
        "open": data_frame["Open"].to_numpy().tolist(),
        "close": data_frame["Close"].to_numpy().tolist(),
        "high": data_frame["High"].to_numpy().tolist(),
        "low": data_frame["Low"].to_numpy().tolist(),
        "increasing": {"line": {"color": "green"}},
        "decreasing": {"line": {"color": "red"}},
        "type": "candlestick",
        "xaxis": "x",
        "yaxis": "y",
    }
    future = forecasting_model.make_future_dataframe(periods=0)
    forecast = forecasting_model.predict(future)
    pred = round(forecast.iloc[-1, 1], 2)
    return jsonify({"trend": data, "prediction": pred})


@app.route("/")
def home():
    """
    Home page route. Returns predictions as well as one-liner live data.
    """
    soup = bs(
        requests.get(
            f"https://dps.psx.com.pk/company/{STOCK_NAME}", timeout=10
        ).content,
        "html.parser",
    )
    section = soup.find("div", class_="section section--padded company")
    lst = [section.find(class_="quote__close").contents[0][3:]]
    for stat in section.find_all(class_="stats_item")[:4]:
        lst.append(stat.find(class_="stats_value").contents[0])
    return render_template(
        "home.html",
        lst=lst,
        time=datetime.date.today().strftime("%Y-%m-%d"),
        stock_name=STOCK_NAME,
    )


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
