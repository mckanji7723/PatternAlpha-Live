
from __future__ import annotations

from datetime import date
from pathlib import Path
import os
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yaml
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh

from core.data_upstox import fetch_market_window, load_csv
from core.instrument_search import search_instruments
from core.indicators import add_indicators
from core.patterns import detect_all_patterns
from core.candlesticks import detect_candlestick_patterns
from core.regimes import recognize_regimes
from core.similarity import historical_shape_matches
from core.backtest import backtest_pattern
from core.plotting import make_chart
from core.template_recognition import base_templates, score_detection

load_dotenv()
st.set_page_config(page_title="PatternAlpha Live", layout="wide")

with open("config/settings.yaml", "r", encoding="utf-8") as f:
    CFG = yaml.safe_load(f)
PCFG, SIM, DASH = CFG["patterns"], CFG["similarity"], CFG["dashboard"]

TIMEFRAMES = {
    "1 minute": ("minutes", 1, 5),
    "5 minutes": ("minutes", 5, 20),
    "15 minutes": ("minutes", 15, 30),
    "30 minutes": ("minutes", 30, 90),
    "1 hour": ("hours", 1, 90),
    "1 day": ("days", 1, 365),
}

def token_ready():
    return bool(os.getenv("UPSTOX_ACCESS_TOKEN", "").strip())

def ensure_demo():
    p = Path("data/demo_market.csv")
    if not p.exists():
        import generate_demo_data
        generate_demo_data.generate()
    return p

@st.cache_data(ttl=300, show_spinner=False)
def cached_historical(instrument_key, unit, interval, days):
    return fetch_market_window(
        instrument_key,
        unit=unit,
        interval=interval,
        days=days,
        include_intraday=True,
    )

@st.cache_data(ttl=15, show_spinner=False)
def cached_live(instrument_key, unit, interval, days):
    return fetch_market_window(
        instrument_key,
        unit=unit,
        interval=interval,
        days=days,
        include_intraday=True,
    )

@st.cache_data(show_spinner=False)
def historical_examples_from_file(path_string):
    path = Path(path_string)
    if not path.exists():
        return []
    df = load_csv(path)
    examples = []
    seen = set()
    # Scan overlapping historical windows so older occurrences can be surfaced.
    for end in range(120, len(df) + 1, 35):
        start = max(0, end - 220)
        window = add_indicators(df.iloc[start:end].reset_index(drop=True))
        dets = detect_all_patterns(window, PCFG)
        for d in dets:
            global_s = start + int(d["start_idx"])
            global_e = start + int(d["end_idx"])
            key = (d["pattern"], global_s // 10, global_e // 10)
            if key in seen:
                continue
            seen.add(key)
            examples.append({
                "pattern": d["pattern"],
                "confidence": float(d["confidence"]),
                "start": global_s,
                "end": global_e,
            })
    examples.sort(key=lambda x: x["confidence"], reverse=True)
    return examples[:20]

def example_chart(df, example):
    s = max(0, example["start"] - 8)
    e = min(len(df), example["end"] + 9)
    view = df.iloc[s:e].copy()
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=view.timestamp, open=view.open, high=view.high,
        low=view.low, close=view.close, name="Historical candles"
    ))
    fig.update_layout(
        height=430,
        xaxis_rangeslider_visible=False,
        margin=dict(l=15, r=15, t=45, b=15),
        title=f'{example["pattern"]} — detected historical example',
    )
    return fig

st.title("PatternAlpha Live")
st.caption("Automated stock selection, live/historical market data and pattern-recognition analysis")

# --------------------------- Sidebar ---------------------------
with st.sidebar:
    st.header("Market")
    mode = st.radio("Data mode", ["Historical Upstox", "Live Upstox", "Demo / Replay"])

    selected = None
    if mode != "Demo / Replay":
        if not token_ready():
            st.error("Add UPSTOX_ACCESS_TOKEN to .env first.")
        query = st.text_input("Search NSE stock", value=st.session_state.get("stock_query", "RELIANCE"))
        if st.button("Search stock", use_container_width=True):
            try:
                with st.spinner("Searching Upstox..."):
                    st.session_state.search_results = search_instruments(query, exchange="NSE", segment="EQ", records=20)
                    st.session_state.stock_query = query
            except Exception as exc:
                st.session_state.search_results = []
                st.error(f"Stock search failed: {exc}")

        results = st.session_state.get("search_results", [])
        if results:
            labels = [
                f'{x["trading_symbol"]} — {x["name"]} ({x["exchange"]})'
                for x in results
            ]
            idx = st.selectbox("Select stock", range(len(labels)), format_func=lambda i: labels[i])
            selected = results[idx]
            st.session_state.selected_instrument = selected
        else:
            selected = st.session_state.get("selected_instrument")
            if selected:
                st.info(f'Current: {selected["trading_symbol"]}')

        tf_label = st.selectbox("Timeframe", list(TIMEFRAMES.keys()), index=2)
        unit, interval, recommended_days = TIMEFRAMES[tf_label]
        max_days = 30 if unit == "minutes" and interval <= 15 else (90 if unit in {"minutes", "hours"} else 3650)
        default_days = min(recommended_days, max_days)
        history_days = st.number_input(
            "History range (days)",
            min_value=1,
            max_value=max_days,
            value=default_days,
            step=1,
            help="Limited automatically to Upstox V3 retrieval constraints for the chosen timeframe.",
        )
        analyze = st.button("Load / Analyze", type="primary", use_container_width=True)

        if mode == "Live Upstox":
            refresh_seconds = st.slider("Live refresh (seconds)", 10, 60, 15, 5)
            st.caption("Live mode refreshes the selected stock automatically using current Upstox intraday candles.")
    else:
        replay = st.toggle("Replay animation", False)
        speed_ms = st.slider("Replay speed (ms)", 500, 5000, 1500, 100)
        tf_label, unit, interval, history_days, analyze = "Demo", None, None, None, True

    st.divider()
    show_ema = st.checkbox("Show EMAs", True)
    show_bb = st.checkbox("Show Bollinger Bands", False)
    max_rows = st.slider("Chart candles", 80, 600, int(DASH["default_rows"]), 20)

# --------------------------- Data loading ---------------------------
df_all = None
symbol_title = "Demo Market"

if mode == "Demo / Replay":
    path = ensure_demo()
    df_source = load_csv(path)
    if "replay_n" not in st.session_state:
        st.session_state.replay_n = min(100, len(df_source))
    if st.sidebar.button("Restart replay"):
        st.session_state.replay_n = min(100, len(df_source))
    if replay:
        st_autorefresh(interval=speed_ms, key="replay_refresh")
        st.session_state.replay_n = min(
            len(df_source),
            st.session_state.replay_n + int(DASH["replay_step"]),
        )
    else:
        st.session_state.replay_n = st.sidebar.slider(
            "Replay position",
            30,
            len(df_source),
            min(max(st.session_state.replay_n, 30), len(df_source)),
        )
    df_all = df_source.iloc[:st.session_state.replay_n].reset_index(drop=True)

else:
    if analyze and selected:
        st.session_state.selected_instrument = selected
        st.session_state.selected_tf = tf_label
        st.session_state.selected_days = int(history_days)
        st.cache_data.clear()

    selected = st.session_state.get("selected_instrument")
    active_tf = st.session_state.get("selected_tf", tf_label)
    active_days = int(st.session_state.get("selected_days", history_days))
    unit, interval, _ = TIMEFRAMES[active_tf]

    if selected is None:
        st.info("Search for a stock in the sidebar, select it, and click **Load / Analyze**.")
        st.stop()

    symbol_title = selected["trading_symbol"]
    try:
        if mode == "Live Upstox":
            st_autorefresh(interval=int(refresh_seconds * 1000), key="market_refresh")
            with st.spinner(f"Refreshing {symbol_title}..."):
                df_all = cached_live(selected["instrument_key"], unit, interval, active_days)
        else:
            with st.spinner(f"Loading {symbol_title} historical candles..."):
                df_all = cached_historical(selected["instrument_key"], unit, interval, active_days)
    except Exception as exc:
        st.error(f"Upstox data request failed: {exc}")
        st.caption("Check that the Analytics Token in .env is valid and that the selected instrument is available.")
        st.stop()

if df_all is None or df_all.empty:
    st.warning("No candles were returned for this selection.")
    st.stop()
if len(df_all) < 20:
    st.warning(f"Only {len(df_all)} candles are available. At least 20 are needed.")
    st.stop()

# --------------------------- Recognition pipeline ---------------------------
enriched_all = recognize_regimes(add_indicators(df_all))
view = enriched_all.tail(max_rows).reset_index(drop=True)
raw_patterns = detect_all_patterns(view, PCFG)
patterns = [score_detection(view, p) for p in raw_patterns]
cps = detect_candlestick_patterns(view)
last = view.iloc[-1]
regime = str(last.get("regime", "Unknown"))
ema_state = "Bullish alignment" if last.ema20 > last.ema50 else "Bearish/neutral alignment"

st.subheader(f"{symbol_title} — {tf_label if mode != 'Demo / Replay' else 'Replay'}")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Last Price", f"{last.close:.2f}")
c2.metric("RSI 14", f"{last.rsi14:.1f}" if pd.notna(last.rsi14) else "—")
c3.metric("Market Regime", regime)
c4.metric("EMA State", ema_state)
best_score = max((p.get("match_score", 0) for p in patterns), default=0)
c5.metric("Best Pattern Match", f"{best_score:.0%}" if best_score else "None")

tabs = st.tabs([
    "Live / Historical Analysis",
    "Pattern Library",
    "Recognition Details",
    "Backtest",
])

with tabs[0]:
    st.plotly_chart(make_chart(view, patterns, cps, show_ema, show_bb), use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.subheader("Detected geometric patterns")
        if patterns:
            rows = []
            for p in patterns:
                rec = p.get("recognition", {})
                rows.append({
                    "Pattern": p["pattern"],
                    "Geometry": f'{p["confidence"]:.0%}',
                    "Template/KNN class": rec.get("predicted_pattern", "—"),
                    "Template similarity": f'{rec.get("template_similarity", 0):.0%}',
                    "Match score": f'{p.get("match_score", p["confidence"]):.0%}',
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No geometric pattern currently passes the configured threshold.")

    with right:
        st.subheader("Recent candlestick patterns")
        if cps:
            cp = pd.DataFrame(cps[-15:])
            cp["confidence"] = cp.confidence.map(lambda x: f"{x:.0%}")
            st.dataframe(
                cp[["timestamp", "pattern", "confidence"]].sort_values("timestamp", ascending=False),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No recent candlestick pattern detected.")

    st.subheader("Historical shape similarity")
    sim = historical_shape_matches(
        enriched_all,
        lookback=int(SIM["lookback"]),
        top_k=int(SIM["top_k"]),
        forward_bars=int(SIM["forward_bars"]),
        bullish_threshold=float(SIM["bullish_threshold"]),
        bearish_threshold=float(SIM["bearish_threshold"]),
    )
    if sim["count"]:
        total = sim["count"]
        a, b, c = st.columns(3)
        a.metric("Bullish outcomes", f'{sim["bullish"]/total:.0%}', f'{sim["bullish"]}/{total}')
        b.metric("Neutral outcomes", f'{sim["neutral"]/total:.0%}', f'{sim["neutral"]}/{total}')
        c.metric("Bearish outcomes", f'{sim["bearish"]/total:.0%}', f'{sim["bearish"]}/{total}')
        st.caption(
            f'Nearest {total} normalized historical price windows; forward window = {SIM["forward_bars"]} candles. '
            "These are historical observations, not forecasts."
        )
    else:
        st.info("Not enough earlier history for similarity analysis.")

with tabs[1]:
    st.subheader("Pattern reference templates")
    st.write(
        "These idealized shapes are the reference templates used by the normalization + KNN/template-similarity layer. "
        "They are educational templates, not claimed to be real market observations."
    )
    templates = base_templates()
    template_name = st.selectbox("Reference pattern", list(templates.keys()), key="template_name")
    y = templates[template_name]
    fig = go.Figure(go.Scatter(x=list(range(len(y))), y=y, mode="lines", name=template_name))
    fig.update_layout(height=360, title=f"{template_name} — normalized reference shape", xaxis_title="Normalized time", yaxis_title="Normalized price")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Detected historical examples")
    bundled = Path("data/RELIANCE.csv")
    example_source = bundled if bundled.exists() else Path("data/historical.csv")
    examples = historical_examples_from_file(str(example_source))
    if examples:
        ex_df = load_csv(example_source)
        options = [
            f'{x["pattern"]} — {x["confidence"]:.0%} — candles {x["start"]}-{x["end"]}'
            for x in examples
        ]
        ex_idx = st.selectbox("Historical example", range(len(options)), format_func=lambda i: options[i])
        st.plotly_chart(example_chart(ex_df, examples[ex_idx]), use_container_width=True)
        st.caption(f"Source: {example_source}. These examples are detections from the bundled historical OHLCV data.")
    else:
        st.info("No historical examples passed the detector threshold in the bundled data. The reference templates above remain available.")

with tabs[2]:
    st.subheader("Pattern Recognition concepts used")
    st.markdown(
        """
- **Pre-processing:** OHLCV candles are converted into numerical price sequences and technical features.
- **Extrema detection:** local peaks and troughs generate geometric pattern candidates.
- **Normalization:** each candidate window is resampled to a fixed length and standardized, making recognition scale-independent.
- **Template matching:** normalized candidates are compared with reference pattern shapes.
- **K-Nearest Neighbours:** the five nearest perturbed reference templates vote on the candidate class.
- **Geometric discriminants:** shoulder symmetry, neckline similarity, cup depth, trend-line slopes and related features contribute a geometry score.
- **Score fusion:** geometry, template similarity and KNN agreement are combined into a pattern-match score.
- **GMM clustering:** return, volatility, EMA-gap and RSI features are clustered to recognize the current market regime.
- **Historical nearest-shape search:** similar past normalized windows are retrieved and their subsequent historical outcomes are summarized.
        """
    )
    if patterns:
        chosen_i = st.selectbox(
            "Inspect detected pattern",
            range(len(patterns)),
            format_func=lambda i: f'{patterns[i]["pattern"]} — match {patterns[i].get("match_score", 0):.0%}',
        )
        p = patterns[chosen_i]
        rec = p.get("recognition", {})
        st.json({
            "geometric_pattern": p["pattern"],
            "geometric_confidence": round(p["confidence"], 4),
            "knn_prediction": rec.get("predicted_pattern"),
            "knn_vote": round(rec.get("knn_vote", 0), 4),
            "template_similarity": round(rec.get("template_similarity", 0), 4),
            "combined_match_score": round(p.get("match_score", 0), 4),
            "nearest_reference_patterns": rec.get("neighbors", []),
        })
    else:
        st.info("Load a stock/window containing a detected geometric pattern to inspect the classifier details.")

with tabs[3]:
    st.subheader("Historical pattern backtest")
    if not patterns:
        st.info("A currently detected pattern is required before running its historical scan.")
    elif len(enriched_all) < 150:
        st.info("Load a longer history range for backtesting.")
    else:
        names = [p["pattern"] for p in patterns]
        selected_name = st.selectbox("Pattern to backtest", names)
        if st.button(f"Backtest {selected_name}", type="primary"):
            with st.spinner("Scanning historical windows..."):
                bt = backtest_pattern(
                    add_indicators(df_all),
                    PCFG,
                    selected_name,
                    forward_bars=int(SIM["forward_bars"]),
                    bullish_threshold=float(SIM["bullish_threshold"]),
                    bearish_threshold=float(SIM["bearish_threshold"]),
                )
            if bt.empty:
                st.warning("No historical occurrences passed the detector threshold.")
            else:
                st.write(f"Occurrences: **{len(bt)}**")
                st.bar_chart(bt.outcome.value_counts())
                st.dataframe(
                    bt.sort_values("timestamp", ascending=False).head(50),
                    use_container_width=True,
                    hide_index=True,
                )

st.caption(
    "Academic Pattern Recognition tool. Pattern matches and historical outcomes are descriptive analyses, "
    "not investment advice or guaranteed price forecasts."
)
