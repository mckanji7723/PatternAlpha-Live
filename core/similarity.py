import numpy as np

def normalize_shape(arr):
    x=np.asarray(arr,float)
    if len(x)==0:return x
    first=x[0] if abs(x[0])>1e-12 else 1.; x=x/first-1; s=np.std(x); return (x-np.mean(x))/s if s>1e-12 else x

def historical_shape_matches(df,end_idx=None,lookback=40,top_k=20,forward_bars=10,bullish_threshold=.01,bearish_threshold=-.01):
    if end_idx is None:end_idx=len(df)-1
    if end_idx<lookback or len(df)<lookback+forward_bars+5:return {'matches':[],'bullish':0,'neutral':0,'bearish':0,'count':0}
    cur=normalize_shape(df.close.iloc[end_idx-lookback+1:end_idx+1]); cand=[]; last=end_idx-lookback-forward_bars
    for i in range(lookback-1,max(lookback-1,last)+1):
        sh=normalize_shape(df.close.iloc[i-lookback+1:i+1]);
        if len(sh)!=len(cur):continue
        dist=float(np.mean((sh-cur)**2)); ret=float(df.close.iloc[i+forward_bars]/df.close.iloc[i]-1); cand.append((dist,i,ret))
    sel=sorted(cand)[:top_k]; bu=sum(r>bullish_threshold for _,_,r in sel); be=sum(r<bearish_threshold for _,_,r in sel); ne=len(sel)-bu-be
    return {'matches':[{'distance':d,'end_idx':i,'forward_return':r} for d,i,r in sel],'bullish':bu,'neutral':ne,'bearish':be,'count':len(sel)}
