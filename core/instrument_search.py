
from __future__ import annotations
import os
import requests
from dotenv import load_dotenv

load_dotenv()
SEARCH_URL = "https://api.upstox.com/v2/instruments/search"

def _headers():
    token = os.getenv("UPSTOX_ACCESS_TOKEN", "").strip()
    if not token:
        raise RuntimeError("UPSTOX_ACCESS_TOKEN is missing in .env")
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

def search_instruments(query: str, exchange: str = "NSE", segment: str = "EQ", records: int = 20):
    query = (query or "").strip()
    if len(query) < 2:
        return []
    params = {
        "query": query[:50],
        "exchanges": exchange,
        "segments": segment,
        "page_number": 1,
        "records": min(max(int(records), 1), 30),
    }
    response = requests.get(SEARCH_URL, headers=_headers(), params=params, timeout=20)
    response.raise_for_status()
    items = response.json().get("data", []) or []
    cleaned = []
    for item in items:
        key = item.get("instrument_key")
        if not key:
            continue
        cleaned.append({
            "name": item.get("name") or item.get("short_name") or item.get("trading_symbol") or key,
            "trading_symbol": item.get("trading_symbol") or item.get("short_name") or item.get("name") or key,
            "instrument_key": key,
            "exchange": item.get("exchange") or exchange,
            "segment": item.get("segment") or "",
        })
    return cleaned
