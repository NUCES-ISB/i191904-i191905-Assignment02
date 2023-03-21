import numpy as np
import pandas as pd
import pandas
from pandas_datareader import data as pdr
import json
import requests
key = "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT"
import time
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
%matplotlib inline
import cufflinks as cf

### Binance

for i in range(1000):
    time.sleep(0.25)
    data = requests.get(key)
    data = data.json()
    a = (data['symbol'])
    b = float(data['price'])
    #print(a, "price is ",b)
    
### Stock


import yfinance as yfin

yfin.pdr_override()
AAPL = pdr.get_data_yahoo('AAPL', start='2003-1-1', end='2023-1-1')
AAPL_data = yfin.download(tickers='AAPL', period='7d', interval='1m')
df = pd.DataFrame(AAPL)

### Plot show

cf.go_offline()
apple = df[['Open', 'High', 'Low', 'Close']].loc['2021-01-01':'2021-5-30']
apple.iplot(kind='candle')
