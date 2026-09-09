from __future__ import annotations
import os,threading,time
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import upstox_client
load_dotenv(); TOKEN=os.getenv('UPSTOX_ACCESS_TOKEN','').strip(); KEY=os.getenv('UPSTOX_INSTRUMENT_KEY','NSE_INDEX|Nifty 50').strip(); OUT=Path('data/live_candles.csv'); OUT.parent.mkdir(parents=True,exist_ok=True); LOCK=threading.Lock()

def extract_ohlc(message):
    if not isinstance(message,dict):return None
    feeds=message.get('feeds',{}); feed=feeds.get(KEY) or (next(iter(feeds.values())) if len(feeds)==1 else None)
    if not feed:return None
    full=feed.get('fullFeed') or feed.get('ff') or {}; branch=full.get('marketFF') or full.get('indexFF') or {}; candles=branch.get('marketOHLC',{}).get('ohlc',[])
    for c in candles:
        if str(c.get('interval','')).upper() in {'I1','1MINUTE','1M'}:
            return {'timestamp':pd.to_datetime(int(c['ts']),unit='ms',utc=True).tz_convert('Asia/Kolkata'),'open':float(c['open']),'high':float(c['high']),'low':float(c['low']),'close':float(c['close']),'volume':float(c.get('vol',0))}
    return None

def upsert(row):
    with LOCK:
        df=pd.read_csv(OUT) if OUT.exists() and OUT.stat().st_size>0 else pd.DataFrame(columns=['timestamp','open','high','low','close','volume']); df=pd.concat([df,pd.DataFrame([row])],ignore_index=True); df['timestamp']=pd.to_datetime(df.timestamp); df.sort_values('timestamp').drop_duplicates('timestamp',keep='last').tail(2000).to_csv(OUT,index=False)

def on_message(m):
    r=extract_ohlc(m)
    if r: upsert(r); print(f"{r['timestamp']} O:{r['open']:.2f} H:{r['high']:.2f} L:{r['low']:.2f} C:{r['close']:.2f}")
def on_open():print(f'Connected: {KEY}')
def on_error(e):print('WebSocket error:',e)
def main():
    if not TOKEN: raise RuntimeError('UPSTOX_ACCESS_TOKEN is empty. Copy .env.example to .env and add your token.')
    cfg=upstox_client.Configuration(); cfg.access_token=TOKEN; s=upstox_client.MarketDataStreamerV3(upstox_client.ApiClient(cfg),[KEY],'full'); s.on('open',on_open); s.on('message',on_message); s.on('error',on_error); s.auto_reconnect(True,10,10); print('Starting live collector. Ctrl+C to stop.')
    try:
        s.connect()
        while True: time.sleep(1)
    except KeyboardInterrupt:
        try:s.disconnect()
        except Exception:pass
if __name__=='__main__':main()
