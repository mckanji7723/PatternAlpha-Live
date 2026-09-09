import numpy as np
from scipy.signal import find_peaks

def find_price_extrema(close,distance=4,prominence_pct=0.006):
    v=close.astype(float).to_numpy()
    if len(v)<12:return [],[]
    prom=max(float(np.nanmedian(v)),1e-9)*float(prominence_pct)
    p,_=find_peaks(v,distance=distance,prominence=prom); t,_=find_peaks(-v,distance=distance,prominence=prom); return p.tolist(),t.tolist()

def alternating_extrema(close,distance=4,prominence_pct=0.006):
    p,t=find_price_extrema(close,distance,prominence_pct); items=[(i,'peak',float(close.iloc[i])) for i in p]+[(i,'trough',float(close.iloc[i])) for i in t]; items.sort()
    cleaned=[]
    for item in items:
        if not cleaned or cleaned[-1][1]!=item[1]: cleaned.append(item)
        elif item[1]=='peak' and item[2]>cleaned[-1][2]: cleaned[-1]=item
        elif item[1]=='trough' and item[2]<cleaned[-1][2]: cleaned[-1]=item
    return cleaned
