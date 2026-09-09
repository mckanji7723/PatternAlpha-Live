import pandas as pd,numpy as np
from core.indicators import add_indicators
from core.similarity import normalize_shape
from core.candlesticks import detect_candlestick_patterns

def sample_df(n=220):
    rng=np.random.default_rng(0); close=100+np.cumsum(rng.normal(0,.3,n)); op=np.r_[close[0],close[:-1]]; return pd.DataFrame({'timestamp':pd.date_range('2026-01-01',periods=n,freq='5min'),'open':op,'high':np.maximum(op,close)+.2,'low':np.minimum(op,close)-.2,'close':close,'volume':1000})
def test_indicators_columns():
    df=add_indicators(sample_df());
    for c in ['ema20','ema50','ema200','rsi14','macd','bb_upper','atr14']: assert c in df.columns
def test_normalize_shape():
    x=normalize_shape([100,101,102,101]); assert len(x)==4 and np.isfinite(x).all()
def test_candlestick_runs():assert isinstance(detect_candlestick_patterns(sample_df()),list)
