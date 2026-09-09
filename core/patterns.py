import numpy as np
from scipy.stats import linregress
from .extrema import alternating_extrema, find_price_extrema

def _clamp(x): return float(max(0,min(1,x)))
def _rd(a,b): return abs(a-b)/max(abs(a),abs(b),1e-9)
def _res(name,conf,pts,s,e,extra=None): return {'pattern':name,'confidence':_clamp(conf),'points':pts,'start_idx':int(s),'end_idx':int(e),'extra':extra or {}}

def detect_head_shoulders(close,cfg):
    ext=alternating_extrema(close,cfg['peak_distance'],cfg['peak_prominence_pct']); out=[]
    for j in range(len(ext)-4):
        s=ext[j:j+5]; ty=[x[1] for x in s]
        if ty==['peak','trough','peak','trough','peak']:
            p1,t1,h,t2,p3=s; shoulder=1-_rd(p1[2],p3[2])/cfg['shoulder_tolerance']; margin=(h[2]-max(p1[2],p3[2]))/max(h[2],1e-9); neck=1-_rd(t1[2],t2[2])/cfg['neckline_tolerance']; space=1-abs((h[0]-p1[0])-(p3[0]-h[0]))/max(p3[0]-p1[0],1); conf=.3*_clamp(shoulder)+.3*_clamp(margin/.03)+.2*_clamp(neck)+.2*_clamp(space)
            if conf>=cfg['min_confidence']:
                out.append(_res('Head & Shoulders',conf,[{'label':'Left Shoulder','index':p1[0],'price':p1[2]},{'label':'Neckline 1','index':t1[0],'price':t1[2]},{'label':'Head','index':h[0],'price':h[2]},{'label':'Neckline 2','index':t2[0],'price':t2[2]},{'label':'Right Shoulder','index':p3[0],'price':p3[2]}],p1[0],p3[0]))
        if ty==['trough','peak','trough','peak','trough']:
            p1,t1,h,t2,p3=s; shoulder=1-_rd(p1[2],p3[2])/cfg['shoulder_tolerance']; margin=(min(p1[2],p3[2])-h[2])/max(abs(h[2]),1e-9); neck=1-_rd(t1[2],t2[2])/cfg['neckline_tolerance']; space=1-abs((h[0]-p1[0])-(p3[0]-h[0]))/max(p3[0]-p1[0],1); conf=.3*_clamp(shoulder)+.3*_clamp(margin/.03)+.2*_clamp(neck)+.2*_clamp(space)
            if conf>=cfg['min_confidence']:
                out.append(_res('Inverse Head & Shoulders',conf,[{'label':'Left Shoulder','index':p1[0],'price':p1[2]},{'label':'Neckline 1','index':t1[0],'price':t1[2]},{'label':'Head','index':h[0],'price':h[2]},{'label':'Neckline 2','index':t2[0],'price':t2[2]},{'label':'Right Shoulder','index':p3[0],'price':p3[2]}],p1[0],p3[0]))
    return out

def detect_double_patterns(close,cfg):
    peaks,troughs=find_price_extrema(close,cfg['peak_distance'],cfg['peak_prominence_pct']); out=[]
    for arr,name,sign in [(peaks,'Double Top',1),(troughs,'Double Bottom',-1)]:
        for a,b in zip(arr[:-1],arr[1:]):
            if b-a<4 or b-a>45: continue
            pa,pb=float(close.iloc[a]),float(close.iloc[b]); sim=1-_rd(pa,pb)/cfg['double_tolerance']; seg=close.iloc[a:b+1]; vals=seg.to_numpy(float)
            if sign==1: midrel=int(np.argmin(vals)); middle=float(vals[midrel]); swing=(min(pa,pb)-middle)/max(abs(pa),1e-9)
            else: midrel=int(np.argmax(vals)); middle=float(vals[midrel]); swing=(middle-max(pa,pb))/max(abs(pa),1e-9)
            conf=.6*_clamp(sim)+.4*_clamp(swing/.025)
            if conf>=cfg['min_confidence']:
                out.append(_res(name,conf,[{'label':'Top 1' if sign==1 else 'Bottom 1','index':a,'price':pa},{'label':'Middle','index':a+midrel,'price':middle},{'label':'Top 2' if sign==1 else 'Bottom 2','index':b,'price':pb}],a,b))
    return out

def detect_cup_handle(close,cfg):
    out=[]; n=len(close)
    for w in range(cfg['cup_window_min'],min(cfg['cup_window_max'],n)+1,5):
        start=n-w; y=close.iloc[start:n].to_numpy(float)
        if len(y)<40: continue
        cut=int(len(y)*.78); cup,handle=y[:cut],y[cut:]; left,right=float(cup[0]),float(cup[-1]); bi=int(np.argmin(cup)); bottom=float(cup[bi]); rim=1-_rd(left,right)/.07; depth=(min(left,right)-bottom)/max(min(left,right),1e-9); center=1-abs(bi-(len(cup)-1)/2)/max((len(cup)-1)/2,1); hlow=float(handle.min()); hdrop=(right-hlow)/max(right,1e-9); hscore=1-abs(hdrop-min(max(depth*.35,.01),.08))/.08; x=np.linspace(-1,1,len(cup)); coef=np.polyfit(x,cup,2); pred=np.polyval(coef,x); r2=1-float(np.sum((cup-pred)**2))/(float(np.sum((cup-cup.mean())**2))+1e-9); uscore=_clamp(r2) if coef[0]>0 else 0; conf=.23*_clamp(rim)+.22*_clamp(depth/.08)+.18*_clamp(center)+.17*_clamp(hscore)+.20*uscore
        if conf>=max(cfg['min_confidence'],.58) and depth>.025:
            hi=start+cut+int(np.argmin(handle)); out.append(_res('Cup & Handle',conf,[{'label':'Cup Start','index':start,'price':left},{'label':'Cup Bottom','index':start+bi,'price':bottom},{'label':'Cup Rim','index':start+cut-1,'price':right},{'label':'Handle','index':hi,'price':hlow},{'label':'Current','index':n-1,'price':float(y[-1])}],start,n-1)); break
    return out

def detect_triangles_wedges(close,cfg):
    peaks,troughs=find_price_extrema(close,cfg['peak_distance'],cfg['peak_prominence_pct']); rs=max(0,len(close)-80); peaks=[i for i in peaks if i>=rs][-4:]; troughs=[i for i in troughs if i>=rs][-4:]; out=[]
    if len(peaks)<2 or len(troughs)<2:return out
    px=np.array(peaks,float); py=np.array([close.iloc[i] for i in peaks],float); tx=np.array(troughs,float); ty=np.array([close.iloc[i] for i in troughs],float); ps=linregress(px,py).slope/max(float(close.iloc[-1]),1e-9); ts=linregress(tx,ty).slope/max(float(close.iloc[-1]),1e-9); pts=[{'label':'Resistance A','index':peaks[0],'price':py[0]},{'label':'Resistance B','index':peaks[-1],'price':py[-1]},{'label':'Support A','index':troughs[0],'price':ty[0]},{'label':'Support B','index':troughs[-1],'price':ty[-1]}]; s,e=min(peaks[0],troughs[0]),max(peaks[-1],troughs[-1]); flat=.0007; req=.0002
    if abs(ps)<flat and ts>req: out.append(_res('Ascending Triangle',_clamp(.65+min(ts*200,.3)),pts,s,e))
    elif abs(ts)<flat and ps<-req: out.append(_res('Descending Triangle',_clamp(.65+min(abs(ps)*200,.3)),pts,s,e))
    elif ps>0 and ts>0:
        conf=.62 if ts>ps else .56
        if conf>=cfg['min_confidence']:out.append(_res('Rising Wedge',conf,pts,s,e))
    elif ps<0 and ts<0:
        conf=.62 if abs(ps)>abs(ts) else .56
        if conf>=cfg['min_confidence']:out.append(_res('Falling Wedge',conf,pts,s,e))
    return out

def detect_all_patterns(df,cfg):
    if len(df)<20:return []
    c=df.close.reset_index(drop=True); r=detect_head_shoulders(c,cfg)+detect_double_patterns(c,cfg)+detect_cup_handle(c,cfg)+detect_triangles_wedges(c,cfg); best={}
    for x in r:
        if x['end_idx']<len(c)-120:continue
        sc=x['confidence']+.0005*x['end_idx']; prev=best.get(x['pattern'])
        if prev is None or sc>prev[0]:best[x['pattern']]=(sc,x)
    return sorted([x for _,x in best.values()],key=lambda z:(z['end_idx'],z['confidence']),reverse=True)
