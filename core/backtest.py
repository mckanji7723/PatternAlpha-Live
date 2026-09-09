import pandas as pd
from .patterns import detect_all_patterns

def backtest_pattern(df,cfg,target_pattern,forward_bars=10,step=3,min_history=60,bullish_threshold=.01,bearish_threshold=-.01):
    rows=[]; seen=set()
    for end in range(min_history,len(df)-forward_bars,step):
        for d in detect_all_patterns(df.iloc[:end+1].reset_index(drop=True),cfg):
            if d['pattern']!=target_pattern or d['end_idx'] in seen:continue
            i=d['end_idx']; seen.add(i); ret=float(df.close.iloc[i+forward_bars]/df.close.iloc[i]-1); outcome='Bullish' if ret>bullish_threshold else ('Bearish' if ret<bearish_threshold else 'Neutral'); rows.append({'pattern':target_pattern,'end_idx':i,'timestamp':df.timestamp.iloc[i],'confidence':d['confidence'],'forward_return':ret,'outcome':outcome})
    return pd.DataFrame(rows)
