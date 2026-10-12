import plotly.graph_objects as go
from plotly.subplots import make_subplots

def make_chart(df,patterns=None,candle_patterns=None,show_ema=True,show_bb=False):
    patterns=patterns or []; candle_patterns=candle_patterns or []
    fig=make_subplots(rows=3,cols=1,shared_xaxes=True,vertical_spacing=.035,row_heights=[.66,.17,.17],specs=[[{'secondary_y':True}],[{}],[{}]])
    fig.add_trace(go.Candlestick(x=df.timestamp,open=df.open,high=df.high,low=df.low,close=df.close,name='Price'),row=1,col=1)
    if show_ema:
        for span in [20,50,200]:
            k=f'ema{span}'
            if k in df: fig.add_trace(go.Scatter(x=df.timestamp,y=df[k],mode='lines',name=f'EMA {span}',line={'width':1.4}),row=1,col=1)
    if show_bb and {'bb_upper','bb_lower'}.issubset(df.columns):
        fig.add_trace(go.Scatter(x=df.timestamp,y=df.bb_upper,mode='lines',name='BB Upper',line={'width':1,'dash':'dot'}),row=1,col=1); fig.add_trace(go.Scatter(x=df.timestamp,y=df.bb_lower,mode='lines',name='BB Lower',line={'width':1,'dash':'dot'}),row=1,col=1)
    fig.add_trace(go.Bar(x=df.timestamp,y=df.volume,name='Volume',opacity=.35),row=2,col=1)
    fig.add_trace(go.Scatter(x=df.timestamp,y=df.rsi14,name='RSI 14'),row=3,col=1); fig.add_hline(y=70,line_dash='dot',row=3,col=1); fig.add_hline(y=30,line_dash='dot',row=3,col=1)
    for det in patterns:
        pts=[p for p in det.get('points',[]) if 0<=p['index']<len(df)]
        if not pts:continue
        xs=[df.timestamp.iloc[p['index']] for p in pts]; ys=[p['price'] for p in pts]; labels=[p['label'] for p in pts]
        fig.add_trace(go.Scatter(x=xs,y=ys,mode='lines+markers+text',text=labels,textposition='top center',name=f"{det['pattern']} {det['confidence']:.0%}",marker={'size':9},line={'width':2,'dash':'dash'}),row=1,col=1)
        neck=[p for p in pts if 'Neckline' in p['label']]
        if len(neck)==2:
            fig.add_trace(go.Scatter(x=[df.timestamp.iloc[neck[0]['index']],df.timestamp.iloc[neck[1]['index']]],y=[neck[0]['price'],neck[1]['price']],mode='lines',name='Neckline',line={'dash':'dot','width':2}),row=1,col=1)
    rec=sorted(candle_patterns,key=lambda x:x['index'])[-12:]
    if rec:
        valid=[x for x in rec if x['index']<len(df)]
        fig.add_trace(go.Scatter(x=[df.timestamp.iloc[x['index']] for x in valid],y=[float(df.high.iloc[x['index']])*1.002 for x in valid],mode='markers+text',text=[x['pattern'] for x in valid],textposition='top center',marker={'symbol':'diamond','size':7},name='Candlestick pattern'),row=1,col=1)
    fig.update_layout(height=760,xaxis_rangeslider_visible=False,hovermode='x unified',margin={'l':20,'r':20,'t':45,'b':20},legend={'orientation':'h','y':1.02,'x':0},title='PatternAlpha Live — annotated market structure')
    fig.update_xaxes(type="category")
    fig.update_yaxes(title_text='Price',row=1,col=1); fig.update_yaxes(title_text='Volume',row=2,col=1); fig.update_yaxes(title_text='RSI',range=[0,100],row=3,col=1)
    return fig
