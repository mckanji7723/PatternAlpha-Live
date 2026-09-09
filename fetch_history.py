import argparse
from datetime import date,timedelta
from pathlib import Path
from core.data_upstox import fetch_historical

def main():
    p=argparse.ArgumentParser(); p.add_argument('--instrument',required=True); p.add_argument('--unit',default='minutes',choices=['minutes','hours','days','weeks','months']); p.add_argument('--interval',type=int,default=5); p.add_argument('--days',type=int,default=20); p.add_argument('--output',default='data/historical.csv'); a=p.parse_args(); to=date.today(); fr=to-timedelta(days=a.days); df=fetch_historical(a.instrument,a.unit,a.interval,fr,to)
    if df.empty: raise RuntimeError('Upstox returned no candles for the requested range.')
    out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True); df.to_csv(out,index=False); print(f'Saved {len(df)} candles to {out}')
if __name__=='__main__': main()
