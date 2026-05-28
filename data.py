import yfinance as yf
import pandas as pd
import streamlit as st

TICKERS = {
    "Petrobrás (PETR4)": "PETR4.SA",
    "Itaú (ITUB4)": "ITUB4.SA",
    "Vale (VALE3)": "VALE3.SA",
}

COLORS = {
    "Petrobrás (PETR4)": "#009B3A",
    "Itaú (ITUB4)": "#003087",
    "Vale (VALE3)": "#0066CC",
}


@st.cache_data(ttl=3600)
def get_stock_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    if df.empty:
        return df
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df["MM20"] = df["Close"].rolling(20).mean()
    df["MM50"] = df["Close"].rolling(50).mean()
    df["Retorno_Acumulado"] = (df["Close"] / df["Close"].iloc[0] - 1) * 100
    df["Variacao_Diaria"] = df["Close"].pct_change() * 100
    return df


def get_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return {}
    return {
        "cotacao_atual": df["Close"].iloc[-1],
        "retorno_total": df["Retorno_Acumulado"].iloc[-1],
        "variacao_diaria": df["Variacao_Diaria"].iloc[-1],
        "max_periodo": df["High"].max(),
        "min_periodo": df["Low"].min(),
        "volume_medio": df["Volume"].mean(),
    }


def get_monthly_returns(df: pd.DataFrame) -> pd.Series:
    monthly = df["Close"].resample("ME").last()
    return monthly.pct_change() * 100
