def _parts(r):
    o,h,l,c=map(float,(r.open,r.high,r.low,r.close)); body=abs(c-o); rng=max(h-l,1e-9); return o,h,l,c,body,rng,h-max(o,c),min(o,c)-l

def detect_candlestick_patterns(df):
    found=[]
    if len(df)<3:return found
    for i in range(max(2,len(df)-120),len(df)):
        r=df.iloc[i]; o,h,l,c,b,rg,u,d=_parts(r); ts=r['timestamp']
        if b/rg<=.10: found.append({'pattern':'Doji','index':i,'timestamp':ts,'confidence':.75})
        if d>=2*max(b,1e-9) and u<=.5*max(b,1e-9): found.append({'pattern':'Hammer','index':i,'timestamp':ts,'confidence':.72})
        if u>=2*max(b,1e-9) and d<=.5*max(b,1e-9): found.append({'pattern':'Inverted Hammer' if c>=o else 'Shooting Star','index':i,'timestamp':ts,'confidence':.72})
        p=df.iloc[i-1]; po,ph,pl,pc,pb,pr,pu,pd=_parts(p)
        if pc<po and c>o and o<=pc and c>=po: found.append({'pattern':'Bullish Engulfing','index':i,'timestamp':ts,'confidence':.82})
        if pc>po and c<o and o>=pc and c<=po: found.append({'pattern':'Bearish Engulfing','index':i,'timestamp':ts,'confidence':.82})
        r0,r1,r2=df.iloc[i-2],df.iloc[i-1],df.iloc[i]; o0,h0,l0,c0,b0,_,_,_=_parts(r0); o1,h1,l1,c1,b1,_,_,_=_parts(r1); o2,h2,l2,c2,b2,_,_,_=_parts(r2)
        if c0<o0 and b1<b0*.55 and c2>o2 and c2>(o0+c0)/2: found.append({'pattern':'Morning Star','index':i,'timestamp':ts,'confidence':.78})
        if c0>o0 and b1<b0*.55 and c2<o2 and c2<(o0+c0)/2: found.append({'pattern':'Evening Star','index':i,'timestamp':ts,'confidence':.78})
    uniq={}
    for x in found: uniq[(x['pattern'],str(x['timestamp']))]=x
    return list(uniq.values())
