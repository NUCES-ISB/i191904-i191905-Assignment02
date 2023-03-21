from flask import Flask, jsonify, render_template
from psx import stocks, tickers
import datetime
import requests
from bs4 import BeautifulSoup as bs
from prophet import Prophet
import pandas as pd

app = Flask(__name__)

stock_name = 'FFC'


@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404


@app.route('/api/trend')
def trend():
    ticker = tickers()
    df = stocks(stock_name, start=datetime.date(
        2022, 1, 1), end=datetime.date.today())
    data = {
        'x': [datetime.datetime.utcfromtimestamp(x/10**9).strftime('%Y-%m-%d') for x in df.index.to_numpy().tolist()],
        'open': df['Open'].to_numpy().tolist(),
        'close': df['Close'].to_numpy().tolist(),
        'high': df['High'].to_numpy().tolist(),
        'low': df['Low'].to_numpy().tolist(),
        'increasing': {'line': {'color': 'green'}},
        'decreasing': {'line': {'color': 'red'}},
        'type': 'candlestick',
        'xaxis': 'x',
        'yaxis': 'y'
    }
    df2 = pd.DataFrame({'ds': [x.strftime('%Y-%m-%d')
                       for x in df.index], 'y': df['Close']})
    df2.index = [x for x in range(len(df2))]

    m = Prophet()
    m.fit(df2)
    future = m.make_future_dataframe(periods=0)
    forecast = m.predict(future)
    pred = round(forecast.iloc[-1, 1], 2)
    print(pred)
    return jsonify({'trend': data, 'prediction': pred})


@app.route('/')
def home():
    soup = bs(requests.get(
        f'https://dps.psx.com.pk/company/{stock_name}').content, 'html.parser')
    section = soup.find('div', class_="section section--padded company")
    lst = [section.find(class_='quote__close').contents[0][3:]]
    for stat in section.find_all(class_='stats_item')[:4]:
        lst.append(stat.find(class_='stats_value').contents[0])
    return render_template('home.html', lst=lst, time=datetime.date.today().strftime('%Y-%m-%d'), stock_name=stock_name)


app.run(debug=True, use_debugger=False, use_reloader=False, host='0.0.0.0')
