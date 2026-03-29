import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="FazDane Analytics | Volatility Engine",
    layout="wide",
    page_icon="📈"
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .main { background-color: #0E1117; }
    h1 { color: #00ADB5 !important; }

    div[data-testid="stMetricValue"] {
        color: #00ADB5;
        font-size: 1.4rem !important;
        font-weight: 600;
    }
    div[data-testid="stMetricLabel"] {
        color: #8B9CB6;
        font-size: 0.78rem !important;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Asset info banner */
    .asset-banner {
        background: linear-gradient(135deg, rgba(0,173,181,0.12), rgba(0,173,181,0.05));
        border: 1px solid rgba(0,173,181,0.3);
        border-radius: 10px;
        padding: 12px 20px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .asset-ticker {
        font-size: 1.5rem;
        font-weight: 700;
        color: #00ADB5;
    }
    .asset-badge {
        background: rgba(0,173,181,0.2);
        color: #00ADB5;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .asset-proxy {
        background: rgba(248,177,149,0.2);
        color: #F8B195;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 20px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .asset-note {
        color: #8B9CB6;
        font-size: 0.8rem;
    }

    /* Quick buttons */
    div[data-testid="column"] button {
        width: 100%;
        border-radius: 8px !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        padding: 4px 8px !important;
        background: rgba(0,173,181,0.08) !important;
        border: 1px solid rgba(0,173,181,0.25) !important;
        color: #00ADB5 !important;
        transition: all 0.15s ease !important;
    }
    div[data-testid="column"] button:hover {
        background: rgba(0,173,181,0.2) !important;
        border-color: rgba(0,173,181,0.6) !important;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #161B22 !important;
        border-right: 1px solid rgba(255,255,255,0.06);
    }
    section[data-testid="stSidebar"] * {
        color: #CDD5E0;
    }

    /* Sidebar section labels */
    .sidebar-section {
        font-size: 0.68rem;
        font-weight: 700;
        color: #00ADB5 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin: 18px 0 4px 0;
        border-bottom: 1px solid rgba(0,173,181,0.2);
        padding-bottom: 4px;
    }

    /* Sidebar input fields - dark background */
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] textarea {
        background-color: #0E1117 !important;
        color: #E0E6F0 !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 6px !important;
    }

    /* Date input containers */
    section[data-testid="stSidebar"] div[data-baseweb="input"] {
        background-color: #0E1117 !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 6px !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="base-input"] {
        background-color: #0E1117 !important;
    }

    /* Selectbox */
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #0E1117 !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        color: #E0E6F0 !important;
    }

    /* Slider accent color - teal */
    section[data-testid="stSidebar"] div[data-testid="stSlider"] div[role="slider"] {
        background-color: #00ADB5 !important;
        border-color: #00ADB5 !important;
    }

    /* Quick buttons */
    div[data-testid="column"] button {
        width: 100%;
        border-radius: 8px !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        padding: 4px 8px !important;
        background: rgba(0,173,181,0.08) !important;
        border: 1px solid rgba(0,173,181,0.25) !important;
        color: #00ADB5 !important;
        transition: all 0.15s ease !important;
    }
    div[data-testid="column"] button:hover {
        background: rgba(0,173,181,0.2) !important;
        border-color: rgba(0,173,181,0.6) !important;
    }

    /* Metric cards */
    div[data-testid="stMetricValue"] {
        color: #00ADB5;
        font-size: 1.4rem !important;
        font-weight: 600;
    }
    div[data-testid="stMetricLabel"] {
        color: #8B9CB6;
        font-size: 0.78rem !important;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 10px;
        padding: 14px 18px;
    }
    div[data-testid="stMetricDelta"] svg { display: none; }

    /* Main area */
    .main { background-color: #0E1117; }
    h1 { color: #00ADB5 !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# TICKER CONSTANTS
# ─────────────────────────────────────────────
INDEX_PROXIES = {
    "SPX": "SPY",
    "NDX": "QQQ",
    "RUT": "IWM",
}

ASSET_TYPES = {
    "SPX": "Index", "NDX": "Index", "RUT": "Index",
    "AAPL": "Stock", "MSFT": "Stock", "NVDA": "Stock",
    "AMZN": "Stock", "GOOGL": "Stock", "META": "Stock", "TSLA": "Stock",
    "SPY": "ETF", "QQQ": "ETF", "IWM": "ETF", "DIA": "ETF",
    "XLE": "ETF", "XLF": "ETF", "XLK": "ETF",
    "SMH": "ETF", "TLT": "ETF", "GLD": "ETF",
    "AMD": "Stock", "NFLX": "Stock", "COIN": "Stock",
    "BA": "Stock", "JPM": "Stock",
}

DROPDOWN_OPTIONS = {
    "── 📊 Indices ──────────────────": ["SPX", "NDX", "RUT"],
    "── 🚀 Mag 7 ────────────────────": ["AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA"],
    "── 💰 Premium Selling Favorites ─": ["SPY", "QQQ", "IWM", "DIA", "XLE", "XLF", "XLK", "SMH", "TLT", "GLD"],
    "── ⚡ High IV / Active Options ──": ["AMD", "NFLX", "COIN", "BA", "JPM"],
}

# Flatten for selectbox (with group headers as disabled separators)
FLAT_OPTIONS = []
OPTION_LABELS = []
for group, tickers in DROPDOWN_OPTIONS.items():
    FLAT_OPTIONS.append(group)
    OPTION_LABELS.append(group)
    for t in tickers:
        FLAT_OPTIONS.append(t)
        OPTION_LABELS.append(t)

QUICK_BUTTONS = ["SPY", "QQQ", "TSLA", "AAPL", "NVDA", "GLD"]

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
if "dropdown_select" not in st.session_state:
    st.session_state.dropdown_select = "SPY"
if "custom_ticker" not in st.session_state:
    st.session_state.custom_ticker = ""

# ─────────────────────────────────────────────
# GET SELECTED TICKER (modular function)
# ─────────────────────────────────────────────
def get_selected_ticker(dropdown_val: str, custom_input: str, use_proxy: bool) -> tuple:
    """
    Returns (display_ticker, data_ticker, note)
    display_ticker: what the user selected (e.g. SPX)
    data_ticker:    what we actually query (e.g. SPY if proxy enabled)
    note:           human-readable proxy note
    """
    raw = custom_input.strip().upper() if custom_input.strip() else dropdown_val.strip()

    # Skip group headers
    if raw.startswith("──"):
        raw = "SPY"

    display = raw
    note = ""

    if use_proxy and raw in INDEX_PROXIES:
        data_ticker = INDEX_PROXIES[raw]
        note = f"Using {data_ticker} as ETF proxy for {raw}"
    elif not use_proxy and raw == "SPX":
        data_ticker = "^GSPC"
        note = "Using ^GSPC (S&P 500 Index)"
    elif not use_proxy and raw == "NDX":
        data_ticker = "^NDX"
        note = "Using ^NDX (Nasdaq-100 Index)"
    elif not use_proxy and raw == "RUT":
        data_ticker = "^RUT"
        note = "Using ^RUT (Russell 2000 Index)"
    else:
        data_ticker = raw

    return display, data_ticker, note

# ─────────────────────────────────────────────
# DATA FUNCTIONS
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_data(ticker, start, end):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(start=start, end=end)
        if data is None or data.empty:
            return None
        return data
    except Exception:
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_current_iv(ticker, dte_target=30):
    """Fetch current IV for the options expiration closest to dte_target days."""
    try:
        stock = yf.Ticker(ticker)
        expirations = stock.options
        if not expirations:
            return None

        # Find the expiration date closest to our DTE target
        today = datetime.today().date()
        best_exp = min(
            expirations,
            key=lambda d: abs((datetime.strptime(d, "%Y-%m-%d").date() - today).days - dte_target)
        )

        opt = stock.option_chain(best_exp)
        calls = opt.calls
        valid_calls = calls[calls['impliedVolatility'] > 0.01].copy()
        if valid_calls.empty:
            return None

        current_price = stock.fast_info['lastPrice']
        idx = (valid_calls['strike'] - current_price).abs().idxmin()
        closest_call = valid_calls.loc[idx]
        return float(closest_call['impliedVolatility']) * 100
    except Exception:
        return None

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📈 FazDane Analytics")
    st.caption("Volatility Engine v2.0")
    st.markdown("---")

    # ── Quick Load Buttons ──
    st.markdown('<p class="sidebar-section">Quick Load</p>', unsafe_allow_html=True)
    qcols = st.columns(3)
    for i, qt in enumerate(QUICK_BUTTONS):
        if qcols[i % 3].button(qt, key=f"quick_{qt}"):
            st.session_state.dropdown_select = qt
            st.session_state.custom_ticker = ""

    st.markdown("---")

    # ── Ticker Selection ──
    st.markdown('<p class="sidebar-section">Ticker</p>', unsafe_allow_html=True)

    selected_dropdown = st.selectbox(
        "Select Ticker",
        options=FLAT_OPTIONS,
        key="dropdown_select",
        label_visibility="collapsed",
    )

    custom_input = st.text_input(
        "Or Enter Custom Ticker",
        value=st.session_state.custom_ticker,
        placeholder="e.g. SHOP, MSTR, UBER...",
        key="custom_input_field"
    )
    st.session_state.custom_ticker = custom_input

    # ── Index Proxy Toggle ──
    use_proxy = st.toggle("Use ETF Proxy for Indices", value=True,
                          help="SPX→SPY, NDX→QQQ, RUT→IWM. Enables live options data.")

    st.markdown("---")

    # ── Date Range ──
    st.markdown('<p class="sidebar-section">Date Range</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", value=datetime.today() - timedelta(days=365))
    with col2:
        end_date = st.date_input("To", value=datetime.today())

    st.markdown("---")

    # ── Volatility Parameters ──
    st.markdown('<p class="sidebar-section">Parameters</p>', unsafe_allow_html=True)
    window = st.slider("HV Window (Days)", min_value=5, max_value=60, value=20,
                        help="Rolling window for Historical Volatility calculation.")
    dte_target = st.slider("IV Target DTE (Days)", min_value=7, max_value=90, value=30,
                           help="Options expiration closest to this DTE will be used for IV.")

# ─────────────────────────────────────────────
# RESOLVE TICKER
# ─────────────────────────────────────────────
raw_dropdown = st.session_state.dropdown_select or "SPY"
if raw_dropdown.startswith("──"):
    raw_dropdown = "SPY"

display_ticker, data_ticker, proxy_note = get_selected_ticker(
    raw_dropdown,
    st.session_state.custom_ticker,
    use_proxy
)

asset_type = ASSET_TYPES.get(display_ticker, "Stock")

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.title("📈 FazDane Analytics: Volatility Engine")
st.markdown("Professional volatility analysis platform powered by **FazDane Analytics**.")

# Asset Info Banner — using native Streamlit components
type_icon = {"Index": "📊", "ETF": "💰", "Stock": "🚀"}.get(asset_type, "📈")
banner_cols = st.columns([1, 6])
with banner_cols[0]:
    st.markdown(f"### {display_ticker}")
with banner_cols[1]:
    label_line = f"**{type_icon} {asset_type}**"
    if proxy_note:
        label_line += f"  |  🔁 {proxy_note}"
    else:
        label_line += f"  |  Ticker: `{data_ticker}`"
    st.info(label_line)

# ─────────────────────────────────────────────
# MAIN ENGINE
# ─────────────────────────────────────────────
if data_ticker:
    with st.spinner(f"Fetching price data for {data_ticker}..."):
        df = load_data(data_ticker, start_date, end_date)

    if df is not None and not df.empty:
        # ── Calculations ──
        df['Return'] = df['Close'].pct_change()
        df['HV'] = df['Return'].rolling(window=window).std() * (252 ** 0.5) * 100

        # Historical Volatility Rank (HVR) — 252-day rolling
        df['Vol_High'] = df['HV'].rolling(window=252, min_periods=1).max()
        df['Vol_Low']  = df['HV'].rolling(window=252, min_periods=1).min()
        range_denom = (df['Vol_High'] - df['Vol_Low'])
        df['HVR'] = ((df['HV'] - df['Vol_Low']) / range_denom.replace(0, float('nan'))) * 100

        latest_close = float(df['Close'].iloc[-1])
        latest_hv    = df['HV'].iloc[-1]
        latest_hvr   = df['HVR'].iloc[-1]

        with st.spinner("Fetching Implied Volatility..."):
            current_iv = get_current_iv(data_ticker, dte_target)

        # ── HVR Signal Helper ──
        def hvr_signal(hvr):
            if pd.isna(hvr): return "N/A"
            if hvr >= 80:    return "🔴 High"
            if hvr >= 50:    return "🟡 Elevated"
            if hvr >= 20:    return "🟢 Low"
            return "🟢 Very Low"

        # ── Metric Row ──
        m1, m2, m3, m4 = st.columns(4)

        m1.metric("Last Price", f"${latest_close:.2f}")

        if not pd.isna(latest_hv):
            m2.metric(f"{window}-Day Historical Vol", f"{latest_hv:.2f}%")
        else:
            m2.metric(f"{window}-Day Historical Vol", "N/A")

        if not pd.isna(latest_hvr):
            m3.metric(
                "Historical Vol Rank (HVR)",
                f"{latest_hvr:.1f}",
                delta=hvr_signal(latest_hvr),
                delta_color="off"
            )
        else:
            m3.metric("Historical Vol Rank (HVR)", "N/A")

        if current_iv is not None:
            m4.metric(f"Implied Vol ~{dte_target}DTE", f"{current_iv:.2f}%")
        else:
            m4.metric(f"Implied Vol ~{dte_target}DTE", "N/A",
                      help="Options data may not be available for this ticker/index.")

        st.markdown("---")

        # ── Chart ──
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'],
            name="Price",
            line=dict(color="#00ADB5", width=2),
            yaxis="y1"
        ))

        fig.add_trace(go.Scatter(
            x=df.index, y=df['HV'],
            name=f"{window}-Day Historical Volatility (%)",
            line=dict(color="#F8B195", width=2, dash="dot"),
            yaxis="y2"
        ))

        fig.update_layout(
            title=dict(
                text=f"{display_ticker} — Price & Historical Volatility",
                font=dict(size=17, color="#E0E0E0")
            ),
            xaxis=dict(title="Date", showgrid=False, color="#8B9CB6"),
            yaxis=dict(
                title="Price ($)",
                title_font=dict(color="#00ADB5"),
                tickfont=dict(color="#00ADB5"),
                showgrid=True,
                gridcolor="rgba(255,255,255,0.05)"
            ),
            yaxis2=dict(
                title="Historical Volatility (%)",
                title_font=dict(color="#F8B195"),
                tickfont=dict(color="#F8B195"),
                anchor="x", overlaying="y", side="right",
                showgrid=False
            ),
            legend=dict(x=0.01, y=0.99, bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#CDD5E0")),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=40, b=0),
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

        # ── HVR Context Box ──
        with st.expander("📖 How to read these metrics", expanded=False):
            st.markdown("""
| Metric | What it means |
|---|---|
| **Historical Vol (HV)** | Annualized std. dev. of past daily returns. Measures how much the asset *has* moved. |
| **Historical Vol Rank (HVR)** | Where current HV sits on a 0–100 scale vs. the past 52 weeks. 0 = annual low, 100 = annual high. |
| **Implied Vol (IV)** | Market's forward-looking expectation of future price movement, derived from options pricing. |

**HVR Signals:**
- 🔴 **≥ 80 (High):** Volatility is elevated. Favor premium *selling* strategies (spreads, strangles).
- 🟡 **50–79 (Elevated):** Moderate regime. Use defined-risk strategies.
- 🟢 **< 50 (Low / Very Low):** Volatility is cheap. Favor premium *buying* or directional strategies.
""")

    else:
        st.warning(f"⚠️ No data found for **{data_ticker}**. Please check the ticker symbol or adjust the date range.")
