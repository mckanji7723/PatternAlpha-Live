# PatternAlpha Live v2

**Automated Real-Time Technical Chart Pattern Recognition and Market-Regime Analysis**

PatternAlpha Live v2 is a Streamlit-based Pattern Recognition course project for analysing Indian equity-market OHLCV data using Upstox. The application allows the user to search for an NSE equity directly inside Streamlit, choose a timeframe and history range, and analyse historical or current intraday candles without manually editing instrument keys or CSV paths.

> **Academic purpose:** PatternAlpha Live is a Pattern Recognition and financial time-series analysis project. It is not an automated trading strategy, a stock-recommendation engine, or financial advice.

---

## 1. Main Features

- Search NSE stocks directly from Streamlit using the Upstox Instrument Search API.
- Automatic `instrument_key` lookup.
- Timeframes: **1m, 5m, 15m, 30m, 1h, 1d**.
- Historical Upstox mode.
- Live Upstox mode with automatic current-day intraday refresh.
- Demo / Replay mode for presentations after market hours.
- Interactive Plotly candlestick charts.
- EMA 20 / 50 / 200, RSI, Bollinger Bands, volume and other derived features.
- Peak and trough extraction.
- Geometric chart-pattern detection.
- Fixed-length resampling and z-normalization.
- Reference-template similarity.
- K-Nearest-Neighbour pattern classification.
- Geometric + template + KNN score fusion.
- GMM market-regime recognition.
- Historical shape matching.
- Historical pattern backtesting.
- Pattern Library with idealized reference templates and detected historical examples.
- Recognition Details tab exposing Pattern Recognition scores and concepts.

---

## 2. Patterns Recognised

PatternAlpha Live v2 is designed to detect the following geometric chart patterns:

- Head & Shoulders
- Inverse Head & Shoulders
- Double Top
- Double Bottom
- Cup & Handle
- Ascending Triangle
- Descending Triangle
- Rising Wedge
- Falling Wedge

The application also includes candlestick-pattern detection and technical indicators for additional market context.

> A stock does **not** have to contain one of these patterns. A valid result may simply be that no strong pattern is currently detected.

---

# 3. Pattern Recognition Concepts Used

This project is not based only on technical-analysis rules. It combines several Pattern Recognition and Machine Learning concepts.

## 3.1 Feature Extraction

Raw OHLCV candles are transformed into features that better describe the structure and behaviour of the price series.

Examples include:

- significant peaks and troughs
- relative peak heights
- relative trough depths
- distances between turning points
- pattern width and depth
- shoulder symmetry
- neckline slope
- short- and medium-term returns
- volatility
- EMA relationships
- RSI

This converts raw market data into a representation that can be used by pattern-recognition algorithms.

## 3.2 Extrema Detection

Local maxima and minima are extracted from the price series and used as structural landmarks.

For example, a possible Head & Shoulders structure can be represented as:

```text
Peak
 ↓
Trough
 ↓
Higher Peak
 ↓
Trough
 ↓
Peak
```

These landmarks can then be interpreted as:

```text
Left Shoulder → Head → Right Shoulder
```

## 3.3 Fixed-Length Resampling

Candidate price windows may contain different numbers of candles. To compare their shapes fairly, candidate windows are resampled into a common fixed-length numerical representation.

This allows patterns of different durations to be compared in the same feature space.

## 3.4 Z-Normalization

The same pattern can appear at very different absolute price levels. A Head & Shoulders pattern around ₹500 and another around ₹3,000 should still be treated as similar shapes.

The project therefore uses normalization conceptually of the form:

```text
z = (x - mean) / standard deviation
```

This makes recognition depend primarily on the **shape and relative movement** of the sequence rather than the absolute stock price.

## 3.5 Reference-Template Matching

Each supported chart-pattern class has an idealized normalized reference representation.

```text
Current candidate
      ↓
Normalize / resample
      ↓
Compare with reference templates
      ↓
Template similarity score
```

The reference curves are **recognition templates**. They are not claimed to be actual historical market observations.

## 3.6 K-Nearest Neighbours (KNN)

KNN is used as a distance-based Pattern Recognition classifier.

A normalized candidate is compared with reference samples and the labels of the nearest neighbours are examined.

Example:

```text
Nearest 5 samples:

Head & Shoulders
Head & Shoulders
Double Top
Head & Shoulders
Head & Shoulders
```

The majority class would favour **Head & Shoulders**. Neighbour agreement is also used as recognition evidence.

## 3.7 Geometric Discriminant Features

The project also checks pattern-specific geometry.

For a Head & Shoulders candidate, useful characteristics include:

- middle peak higher than the shoulders
- similarity between left and right shoulder heights
- spacing between peaks
- similarity between neckline troughs
- symmetry
- head prominence
- neckline slope

These measurements contribute to a geometric confidence score.

## 3.8 Score Fusion

PatternAlpha combines several independent recognition signals rather than trusting only one detector.

```text
Geometric score
+
Template similarity
+
KNN agreement
=
Pattern Match Score
```

The Pattern Match Score describes how strongly the current structure resembles a recognised pattern class. It is **not** the probability that the stock will rise or fall.

## 3.9 Gaussian Mixture Model (GMM)

A Gaussian Mixture Model is used for **unsupervised market-regime recognition**.

The model can use features such as:

- short-term return
- medium-term return
- rolling volatility
- EMA gap
- RSI

The resulting clusters are interpreted as market states such as:

- Bull Trend
- Bear Trend
- Sideways / Low Volatility
- Sideways / High Volatility

This demonstrates **unsupervised learning and clustering**.

## 3.10 Sequential Pattern Recognition

Financial candles form an ordered sequence:

```text
Candle 1 → Candle 2 → Candle 3 → ... → Candle N
```

The ordering of observations is important. PatternAlpha therefore analyses sequential windows rather than treating each candle as an independent sample.

## 3.11 Historical Shape Similarity

The latest normalized price window is compared with earlier windows from the historical data.

The closest historical sequences can be retrieved and their subsequent historical outcomes examined.

This is a similarity-retrieval technique and should be interpreted as **historical comparison**, not future prediction.

## 3.12 Historical Backtesting

Detected patterns can be scanned through previous candles and evaluated empirically.

Conceptually:

```text
Pattern detected at time t
        ↓
Observe price at t + N
        ↓
Calculate forward return
        ↓
Store historical outcome
```

This provides historical validation of the recognition system.

---

# 4. Pattern Recognition Workflow

```text
Selected NSE stock
        |
        v
Upstox Instrument Search
        |
        v
Historical / Intraday OHLCV
        |
        v
Technical feature calculation
        |
        +--> EMA / RSI / volatility --> GMM regime clustering
        |
        v
Peak and trough extraction
        |
        v
Geometric candidate detection
        |
        v
Candidate-window resampling
        |
        v
Z-normalization
        |
        +--> Reference-template similarity
        |
        +--> KNN reference-class voting
        |
        v
Geometry + Template + KNN score fusion
        |
        v
Annotated detected pattern
        |
        +--> nearest historical shape analysis
        |
        +--> historical backtest
```

---

# 5. Recommended Stocks to Search

Individual equities often display stronger short-term structures than analysing only NIFTY 50. The following are good stocks to try during testing and demonstrations:

| Search Symbol | Company |
|---|---|
| `RELIANCE` | Reliance Industries |
| `TCS` | Tata Consultancy Services |
| `INFY` | Infosys |
| `SBIN` | State Bank of India |
| `HDFCBANK` | HDFC Bank |
| `ICICIBANK` | ICICI Bank |
| `TATAMOTORS` | Tata Motors |
| `BAJFINANCE` | Bajaj Finance |
| `ITC` | ITC |
| `ADANIENT` | Adani Enterprises |
| `MARUTI` | Maruti Suzuki |
| `SUNPHARMA` | Sun Pharmaceutical Industries |
| `AXISBANK` | Axis Bank |
| `LT` | Larsen & Toubro |
| `ONGC` | Oil and Natural Gas Corporation |
| `BHARTIARTL` | Bharti Airtel |

### Suggested starting combinations

```text
RELIANCE    → 15-minute candles → 30 days
SBIN        → 15-minute candles → 30 days
TATAMOTORS  → 15-minute candles → 30 days
TCS         → 30-minute candles → 90 days
INFY        → 30-minute candles → 90 days
```

If no clear pattern appears:

1. Try another stock.
2. Increase the history range.
3. Try a larger timeframe such as 15m, 30m or 1h.
4. Use Demo / Replay mode for a reliable presentation example.

There is no guarantee that a particular stock will contain a recognisable pattern during a selected period.

---

# 6. Recommended Timeframes

Available timeframes include:

- 1 minute
- 5 minutes
- 15 minutes
- 30 minutes
- 1 hour
- 1 day

For geometric pattern recognition, a good starting point is:

```text
15 minutes
30 minutes
1 hour
```

Very short intervals can contain substantial market noise. Larger structures such as Head & Shoulders or Cup & Handle may also require many candles to develop.

---

# 7. Application Modes

## Historical Upstox

Use this mode for historical analysis of an NSE stock.

```text
Search stock
→ Select NSE equity
→ Choose timeframe
→ Choose history range
→ Load / Analyze
→ Run Pattern Recognition
```

No manual `instrument_key` or `fetch_history.py` command is required.

## Live Upstox

Use this mode during market hours.

The application automatically loads historical context and current Upstox intraday candles before re-running the recognition pipeline.

Historical context is important because indicators and large chart patterns cannot be calculated reliably from only one or two live candles.

This version uses the Upstox V3 intraday-candle workflow for normal in-app live analysis, so only one Streamlit server is required. The existing `live_collector.py` can remain as an optional WebSocket experiment but is not required for ordinary use.

## Demo / Replay

Use this mode when:

- NSE is closed
- internet/API access is temporarily unavailable
- no obvious live pattern is currently visible
- a reliable classroom or viva demonstration is required

The synthetic demo data is intended to contain recognisable structures so the annotation and classification pipeline can be demonstrated consistently.

---

# 8. Streamlit Tabs

## Live / Historical Analysis

Displays the main candlestick chart, pattern annotations, technical indicators, market regime and historical-similarity information.

## Pattern Library

Displays idealized normalized recognition templates and historical examples detected from the bundled OHLCV data.

## Recognition Details

Shows the Pattern Recognition methods being used and exposes scores such as template similarity and KNN recognition information.

## Backtest

Scans previous candles for historical occurrences of the selected/detected pattern and summarises subsequent historical outcomes.

---

# 9. Installation

## Recommended Python Version

Use **Python 3.12** for this project.

This is recommended for compatibility with NumPy, SciPy, Pandas, scikit-learn and Streamlit.

## Step 1 — Open the project folder

Example:

```powershell
cd C:\PatternAlpha_Live_v2
```

## Step 2 — Create the virtual environment

```powershell
py -3.12 -m venv .venv
```

## Step 3 — Activate the environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Step 4 — Upgrade pip and build tools

```powershell
python -m pip install --upgrade pip setuptools wheel
```

## Step 5 — Install dependencies

```powershell
python -m pip install -r requirements.txt
```

---

# 10. Upstox Configuration

Create `.env` from the provided example if necessary:

```powershell
Copy-Item .env.example .env
notepad .env
```

Add only your private Upstox Analytics Token:

```env
UPSTOX_ACCESS_TOKEN=PASTE_YOUR_PRIVATE_ANALYTICS_TOKEN_HERE
```

You no longer need to store:

```text
UPSTOX_INSTRUMENT_KEY
UPSTOX_SYMBOL
```

The app resolves the selected stock and corresponding instrument key automatically.

## Token Security

Never:

- commit `.env` to GitHub
- publish the token
- include the token in screenshots
- share the token with another person

Keep `.env` excluded through `.gitignore`.

---

# 11. Run the Tests

Run:

```powershell
python -m pytest -q
```

The project test suite should complete successfully before running the app.

You can also verify the scientific libraries with:

```powershell
python -c "import numpy; print(numpy.__version__)"
python -c "import scipy; print(scipy.__version__)"
python -c "import sklearn; print(sklearn.__version__)"
```

---

# 12. Start the Streamlit Server

Run:

```powershell
python -m streamlit run app.py
```

Streamlit should open automatically. If it does not, open:

```text
http://localhost:8501
```

---

# 13. Recommended First Test

Inside Streamlit select:

```text
Mode: Historical Upstox
Search: RELIANCE
Timeframe: 15 minutes
History: 30 days
```

Then click:

```text
Load / Analyze
```

If no strong pattern appears, try:

```text
SBIN
TATAMOTORS
TCS
INFY
ICICIBANK
BAJFINANCE
```

or increase the timeframe/history range.

---

# 14. Daily Startup

After the first installation, you do not need to reinstall packages.

Each time you return to the project:

```powershell
cd C:\PatternAlpha_Live_v2
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py
```

That is all that is required for normal use.

---

# 15. Understanding the Output

The dashboard may display:

- selected stock
- candlestick chart
- technical indicators
- detected geometric pattern
- pattern landmarks
- geometric score
- KNN prediction
- KNN neighbour agreement
- template similarity
- Pattern Match Score
- GMM market regime
- similar historical windows
- historical outcomes
- backtest results

Example:

```text
Detected Pattern: Head & Shoulders
Geometric Score: 0.78
KNN Prediction: Head & Shoulders
Template Similarity: 0.84
Pattern Match Score: 0.81
Market Regime: Bear Trend
```

These values describe the Pattern Recognition system's interpretation of the current data. They are not buy/sell recommendations.

---

# 16. Academic Relevance

| Pattern Recognition Topic | Application in PatternAlpha |
|---|---|
| Feature extraction | Turning points, geometry, returns, volatility and indicators |
| Extrema detection | Locates important peaks and troughs |
| Fixed-length representation | Makes candidate windows comparable |
| Normalization | Makes shapes comparable across stocks and price levels |
| Distance measures | Compares normalized pattern sequences |
| Template matching | Compares candidates with reference prototypes |
| KNN | Classifies candidate shapes using nearest reference examples |
| Geometric discriminant features | Separates pattern classes using structural properties |
| Score fusion | Combines multiple recognition signals |
| Unsupervised learning | GMM recognises market regimes |
| Clustering | Similar market states are grouped together |
| Sequential recognition | Ordered OHLCV windows are analysed over time |
| Similarity retrieval | Finds historical windows resembling the current structure |
| Empirical validation | Backtesting evaluates historical detections |

This makes PatternAlpha a **Pattern Recognition project**, rather than only a financial charting application.

---

# 17. Suggested Viva / Presentation Flow

1. Open the **Pattern Library**.
2. Show a Head & Shoulders reference template.
3. Explain peak/trough extraction.
4. Explain fixed-length resampling.
5. Explain z-normalization.
6. Explain reference-template similarity.
7. Explain KNN classification.
8. Explain geometric feature scoring and score fusion.
9. Open **Demo / Replay** and show automatic annotation.
10. Open **Historical Upstox**.
11. Search `RELIANCE`.
12. Analyse a 15-minute / 30-day window.
13. Search a second stock without changing any source code.
14. Explain the Pattern Match Score.
15. Show GMM market-regime recognition.
16. Show historical similar windows.
17. Show the backtesting tab.
18. If NSE is open, demonstrate **Live Upstox** mode.

---

# 18. Important Interpretation and Limitations

The idealized reference curves in the Pattern Library are **recognition templates**, not claimed to be actual market observations. Historical Examples are based on detections from the bundled historical OHLCV data.

Technical chart patterns are inherently variable and may not form perfectly. Therefore:

- not every stock or timeframe will contain a recognised pattern
- a pattern may be incomplete or developing
- different timeframes can reveal different structures
- short intervals can contain substantial noise
- historical similarity does not guarantee future similarity
- detected patterns do not guarantee future price movement
- the Pattern Match Score is not a probability of trading success
- results should not be interpreted as investment advice

The primary purpose of the project is **financial time-series Pattern Recognition and academic analysis**.

---

# 19. Short Project Description

**PatternAlpha Live v2: Automated Real-Time Technical Chart Pattern Recognition and Market-Regime Analysis**

PatternAlpha Live v2 analyses historical and current OHLCV market data to recognise technical chart structures such as Head & Shoulders, Double Tops/Bottoms, Cup & Handle, Triangles and Wedges. The system combines extrema-based feature extraction, fixed-length resampling, z-normalization, template similarity, K-Nearest-Neighbour classification, geometric pattern scoring and Gaussian Mixture Model clustering. Recognised structures are annotated on an interactive Streamlit/Plotly chart, while historical shape similarity and backtesting provide empirical context for detections.

---

# 20. Technology Summary

**Domain:** Financial Time-Series Pattern Recognition  
**Application:** Streamlit  
**Visualisation:** Plotly  
**Market Data:** Upstox  
**Core Methods:** Feature Extraction, Extrema Detection, Resampling, Z-Normalization, Template Matching, KNN, Geometric Pattern Recognition, Score Fusion, GMM Clustering, Sequential Analysis, Historical Similarity Retrieval and Backtesting

---

# 21. Disclaimer

PatternAlpha Live v2 is an educational academic project.

It is not:

- an automated trading system
- a stock-recommendation engine
- financial advice
- a guarantee of future market behaviour

All detections, indicators, market-regime labels, historical comparisons and backtesting outputs should be interpreted only as analytical results produced by the Pattern Recognition system.
