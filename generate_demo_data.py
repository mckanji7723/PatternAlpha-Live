from pathlib import Path
import numpy as np,pandas as pd

def seg(points,lengths):
    v=[]
    for (a,b),n in zip(zip(points[:-1],points[1:]),lengths):v.extend(np.linspace(a,b,n,endpoint=False))
    v.append(points[-1]); return np.array(v,float)
def generate():
    rng=np.random.default_rng(42); base=100+np.cumsum(rng.normal(.03,.22,110)); hs=seg([base[-1],108,104,112,103.8,108.2,101.5],[10,8,10,8,10,12])+rng.normal(0,.1,59); mid=hs[-1]+np.cumsum(rng.normal(.04,.18,70)); x=np.linspace(-1,1,58); rim=mid[-1]+7; cup=rim-7*(1-x*x)+rng.normal(0,.08,len(x)); handle=np.concatenate([np.linspace(cup[-1],cup[-1]-2,9,endpoint=False),np.linspace(cup[-1]-2,cup[-1]+1.2,10)])+rng.normal(0,.08,19); tail=handle[-1]+np.cumsum(rng.normal(.06,.18,70)); close=np.concatenate([base,hs[1:],mid,cup,handle,tail]); ts=pd.date_range('2026-07-01 09:15',periods=len(close),freq='5min'); op=np.r_[close[0],close[:-1]]+rng.normal(0,.08,len(close)); hi=np.maximum(op,close)+rng.uniform(.08,.35,len(close)); lo=np.minimum(op,close)-rng.uniform(.08,.35,len(close)); vol=rng.integers(50000,250000,len(close)); df=pd.DataFrame({'timestamp':ts,'open':op,'high':hi,'low':lo,'close':close,'volume':vol}); Path('data').mkdir(exist_ok=True); df.to_csv('data/demo_market.csv',index=False); print('Generated',len(df),'candles')
if __name__=='__main__':generate()
