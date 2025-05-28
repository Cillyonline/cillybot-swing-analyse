pandas
numpy
requests
# Swing-Trading Analyse-Tool (verwendet Google Sheet "CillyBot_SwingTradeWL" als Datenquelle)

# Hinweis: Dieses Skript speichert die Ergebnisse lokal als CSV-Datei.

import pandas as pd
import numpy as np
import datetime as dt
import requests
import csv

# Google Sheets als CSV-Quelle
SHEET_URL = "https://docs.google.com/spreadsheets/d/1MyH7AwYQNNu3fzboFDcnU/export?format=csv&gid=0"  # GID=0 für 'Assets'-Tab

# Technische Indikatoren (ohne externe Libraries)
def ema(series, window):
    return series.ewm(span=window, adjust=False).mean()

def rsi(series, window=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / (avg_loss + 1e-6)
    return 100 - (100 / (1 + rs))

def macd(series, fast=12, slow=26):
    exp1 = series.ewm(span=fast, adjust=False).mean()
    exp2 = series.ewm(span=slow, adjust=False).mean()
    return exp1 - exp2

def atr(df, window=14):
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(window=window).mean()

def detect_candle_signal(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    if prev['Close'] < prev['Open'] and last['Close'] > last['Open'] and last['Close'] > prev['Open'] and last['Open'] < prev['Close']:
        return 'Bullish Engulfing'
    if prev['Close'] > prev['Open'] and last['Close'] < last['Open'] and last['Open'] > prev['Close'] and last['Close'] < prev['Open']:
        return 'Bearish Engulfing'
    if abs(last['Close'] - last['Open']) / (last['High'] - last['Low'] + 1e-6) < 0.1:
        return 'Doji'
    return 'Neutral'

def fetch_and_prepare(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={(dt.datetime.today() - dt.timedelta(days=180)).timestamp():.0f}&period2={dt.datetime.today().timestamp():.0f}&interval=1d&events=history"
        df = pd.read_csv(url)
        df.dropna(subset=["Close"], inplace=True)
        df['ema20'] = ema(df['Close'], 20)
        df['ema50'] = ema(df['Close'], 50)
        df['rsi'] = rsi(df['Close'])
        df['macd'] = macd(df['Close'])
        df['atr'] = atr(df)
        return df
    except Exception as e:
        print(f"Fehler beim Abruf von {ticker}: {e}")
        return None

def generate_signal(df):
    if df is None or len(df) < 20:
        return {"Signal": "No Data"}
    signal = "HOLD"
    if df['rsi'].iloc[-1] < 30:
        signal = "BUY"
    elif df['rsi'].iloc[-1] > 70:
        signal = "SELL"
    return {
        "Signal": signal,
        "RSI": round(df['rsi'].iloc[-1], 2),
        "MACD": round(df['macd'].iloc[-1], 2),
        "ATR": round(df['atr'].iloc[-1], 2),
        "Candle": detect_candle_signal(df),
        "Close": round(df['Close'].iloc[-1], 2)
    }

# Watchlist direkt aus Google Sheet laden
watchlist_df = pd.read_csv(SHEET_URL)
watchlist = dict(zip(watchlist_df['Ticker'], watchlist_df['Name']))

# Analyse
results = []
for ticker, name in watchlist.items():
    print(f"Analysiere {ticker} ({name})...")
    df = fetch_and_prepare(ticker)
    signal = generate_signal(df)
    result = {"Ticker": ticker, "Name": name, **signal}
    results.append(result)

# Ausgabe als CSV
df_results = pd.DataFrame(results)
df_results.to_csv("swing_signale.csv", index=False)
print("Analyse abgeschlossen. Ergebnisse in 'swing_signale.csv' gespeichert.")
