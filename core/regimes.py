import numpy as np, pandas as pd
from sklearn.mixture import GaussianMixture

def recognize_regimes(df,n_components=4):
    out=df.copy(); x=pd.DataFrame(index=out.index); x['ret5']=out.close.pct_change(5); x['ret15']=out.close.pct_change(15); x['vol10']=out.close.pct_change().rolling(10).std(); x['ema_gap']=(out.ema20-out.ema50)/out.close; x['rsi']=(out.rsi14-50)/50; x=x.replace([np.inf,-np.inf],np.nan).dropna(); out['regime']='Insufficient data'
    if len(x)<60:return out
    k=min(n_components,max(2,len(x)//30)); labels=GaussianMixture(n_components=k,random_state=42).fit_predict(x); tmp=x.copy(); tmp['cluster']=labels; meta={c:(float(g.ret15.mean()),float(g.vol10.mean())) for c,g in tmp.groupby('cluster')}; cut=float(np.median([v for _,v in meta.values()])); mapping={}
    for c,(r,v) in meta.items(): mapping[c]='Sideways / High Volatility' if abs(r)<.002 and v>=cut else ('Bull Trend' if r>.002 else ('Bear Trend' if r<-.002 else 'Sideways / Low Volatility'))
    m=pd.Series(labels,index=x.index).map(mapping); out.loc[m.index,'regime']=m; return out
