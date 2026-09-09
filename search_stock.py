import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("UPSTOX_ACCESS_TOKEN")

if not token:
    raise RuntimeError("UPSTOX_ACCESS_TOKEN not found in .env")

if len(sys.argv) < 2:
    print('Usage: python search_stock.py "RELIANCE"')
    raise SystemExit

query = " ".join(sys.argv[1:])

url = "https://api.upstox.com/v2/instruments/search"

headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {token}"
}

params = {
    "query": query,
    "exchanges": "NSE",
    "segments": "EQ",
    "page_number": 1,
    "records": 20
}

response = requests.get(
    url,
    headers=headers,
    params=params,
    timeout=30
)

response.raise_for_status()

data = response.json().get("data", [])

if not data:
    print("No NSE equity found.")
else:
    print("\nMatches:\n")

    for item in data:
        print(
            f'{item.get("trading_symbol", ""):15} | '
            f'{item.get("name", ""):40} | '
            f'{item.get("instrument_key", "")}'
        )