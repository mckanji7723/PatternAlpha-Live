import numpy as np
import pandas as pd

def ema(series, span): return series.ewm(span=span, adjust=False).mean()

def rsi(series, period=14):
    delta=series.diff(); gain=delta.clip(lower=0).ewm(alpha=1/period,adjust=False).mean(); loss=(-delta.clip(upper=0)).ewm(alpha=1/period,adjust=False).mean(); rs=gain/loss.replace(0,np.nan); return 100-(100/(1+rs))

def macd(series, fast=12, slow=26, signal=9):
    line=ema(series,fast)-ema(series,slow); sig=ema(line,signal); return line,sig,line-sig

def bollinger(series, period=20, std_mult=2.0):
    mid=series.rolling(period).mean(); std=series.rolling(period).std(); return mid,mid+std_mult*std,mid-std_mult*std

def atr(df, period=14):
    prev=df['close'].shift(1); tr=pd.concat([df['high']-df['low'],(df['high']-prev).abs(),(df['low']-prev).abs()],axis=1).max(axis=1); return tr.ewm(alpha=1/period,adjust=False).mean()

def add_indicators(df):
    out=df.copy(); out['ema20']=ema(out['close'],20); out['ema50']=ema(out['close'],50); out['ema200']=ema(out['close'],200); out['rsi14']=rsi(out['close']); out['macd'],out['macd_signal'],out['macd_hist']=macd(out['close']); out['bb_mid'],out['bb_upper'],out['bb_lower']=bollinger(out['close']); out['atr14']=atr(out); out['return']=out['close'].pct_change(); return out
