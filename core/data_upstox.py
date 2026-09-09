
from __future__ import annotations
import os
from urllib.parse import quote
from datetime import date, timedelta
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
API = "https://api.upstox.com/v3"

def _headers():
    token = os.getenv("UPSTOX_ACCESS_TOKEN", "").strip()
    h = {"Accept": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h

def candles_to_df(candles):
    rows = []
    for c in candles:
        if len(c) < 6:
            continue
        rows.append({
            "timestamp": pd.to_datetime(c[0]),
            "open": float(c[1]),
            "high": float(c[2]),
            "low": float(c[3]),
            "close": float(c[4]),
            "volume": float(c[5]),
        })
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df.sort_values("timestamp").drop_duplicates("timestamp").reset_index(drop=True)

def fetch_historical(instrument_key, unit="minutes", interval=5, from_date=None, to_date=None):
    to_date = to_date or date.today()
    from_date = from_date or (to_date - timedelta(days=20))
    inst = quote(instrument_key, safe="")
    url = f"{API}/historical-candle/{inst}/{unit}/{int(interval)}/{to_date.isoformat()}/{from_date.isoformat()}"
    r = requests.get(url, headers=_headers(), timeout=30)
    r.raise_for_status()
    return candles_to_df(r.json().get("data", {}).get("candles", []))

def fetch_intraday(instrument_key, unit="minutes", interval=1):
    inst = quote(instrument_key, safe="")
    url = f"{API}/historical-candle/intraday/{inst}/{unit}/{int(interval)}"
    r = requests.get(url, headers=_headers(), timeout=30)
    r.raise_for_status()
    return candles_to_df(r.json().get("data", {}).get("candles", []))

def fetch_market_window(instrument_key, unit="minutes", interval=5, days=30, include_intraday=True):
    today = date.today()
    hist = fetch_historical(
        instrument_key,
        unit=unit,
        interval=interval,
        from_date=today - timedelta(days=int(days)),
        to_date=today,
    )
    if include_intraday and unit in {"minutes", "hours", "days"}:
        try:
            intra = fetch_intraday(instrument_key, unit=unit, interval=interval)
            if not intra.empty:
                hist = pd.concat([hist, intra], ignore_index=True)
        except requests.HTTPError:
            pass
    if hist.empty:
        return hist
    hist["timestamp"] = pd.to_datetime(hist["timestamp"])
    return hist.sort_values("timestamp").drop_duplicates("timestamp", keep="last").reset_index(drop=True)

def load_csv(path):
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.dropna(subset=["open", "high", "low", "close"]).sort_values("timestamp").reset_index(drop=True)
