import numpy as np
import pandas as pd
import pandas
from pandas_datareader import data as pdr
import yfinance as yfin
import json
import requests
import time
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
%matplotlib inline
import cufflinks as cf
from prophet import Prophet
from datetime import datetime
#key = "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT"


yfin.pdr_override()
AAPL = pdr.get_data_yahoo('AAPL', start='2011-1-1', end='2023-1-1')
AAPL_data = yfin.download(tickers='AAPL', period='7d', interval='1m')
df = pd.DataFrame(AAPL)

cf.go_offline()
apple = df[['Open', 'High', 'Low', 'Close']].loc['2011-01-01':'2023-1-1']
apple.iplot(kind='candle')

m = Prophet()
df2 = pd.DataFrame({'ds': [x.strftime('%Y-%m-%d') for x in df.index], 'y': df['Close']})
df2.index = [x for x in range(len(df2))]

m = Prophet()
m.fit(df2)

future = m.make_future_dataframe(periods=365)
future.tail()

forecast = m.predict(future)
forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

# Python
fig1 = m.plot(forecast)
