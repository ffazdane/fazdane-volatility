import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="FazDane Analytics | Volatility", layout="wide", page_icon="📈")

# Custom CSS for premium look
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
    }
    h1 {
        color: #00ADB5 !important;
        font-family: 'Inter', sans-serif;
    }
    div[data-testid="stMetricValue"] {
        color: #00ADB5;
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 FazDane Analytics: Volatility Engine")
st.markdown("Proprietary analysis of historical stock prices and annualized rolling volatility. Powered by **FazDane Analytics**.")

# Sidebar for inputs
with st.sidebar:
    st.markdown("### 🏢 FazDane Analytics")
    st.markdown("---")
    st.header("⚙️ Parameters")
    ticker = st.text_input("Ticker Symbol", value="AAPL")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.today() - timedelta(days=365))
    with col2:
        end_date = st.date_input("End Date", value=datetime.today())
        
    window = st.slider("Volatility Window (Days)", min_value=5, max_value=60, value=20)
    
@st.cache_data
def load_data(ticker, start, end):
    try:
        # yf.download can return MultiIndex columns in the newest versions depending on parameters.
        # using yf.Ticker(ticker).history is often cleaner for single tickers to avoid multi-index.
        stock = yf.Ticker(ticker)
        data = stock.history(start=start, end=end)
        if data is None or data.empty:
            return None
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

@st.cache_data(ttl=3600)
def get_current_iv(ticker):
    try:
        stock = yf.Ticker(ticker)
        expirations = stock.options
        if not expirations:
            return None
            
        # Get options for the nearest expiration date
        opt = stock.option_chain(expirations[0])
        calls = opt.calls
        valid_calls = calls[calls['impliedVolatility'] > 0.01]
        
        if not valid_calls.empty:
            # Find the call option with strike closest to the current stock price
            current_price = stock.fast_info['lastPrice']
            idx = (valid_calls['strike'] - current_price).abs().idxmin()
            closest_call = valid_calls.loc[idx]
            return float(closest_call['impliedVolatility']) * 100 # Convert to percentage
            
        return None
    except Exception as e:
        return None

if ticker:
    with st.spinner(f"Fetching data for {ticker}..."):
        df = load_data(ticker, start_date, end_date)
        
    if df is not None and not df.empty:
        # Ticker.history gives standard camel case column names like 'Close', 'Open' without MultiIndex.
        df['Return'] = df['Close'].pct_change()

        # Calculate annualized rolling volatility (std dev * sqrt(252 trading days))
        df['Volatility'] = df['Return'].rolling(window=window).std() * (252 ** 0.5) * 100 # In percentage
        
        # Calculate Historical Volatility Rank (HVR) over the past year (252 days)
        df['Vol_High'] = df['Volatility'].rolling(window=252, min_periods=1).max()
        df['Vol_Low'] = df['Volatility'].rolling(window=252, min_periods=1).min()
        df['HVR'] = ((df['Volatility'] - df['Vol_Low']) / (df['Vol_High'] - df['Vol_Low'])) * 100
        
        # Latest metrics
        latest_close = float(df['Close'].iloc[-1])
        latest_vol = float(df['Volatility'].iloc[-1])
        latest_hvr = float(df['HVR'].iloc[-1]) if not pd.isna(df['HVR'].iloc[-1]) else None
        
        with st.spinner("Fetching current Implied Volatility (IV)..."):
            current_iv = get_current_iv(ticker)
        
        # Layout columns for metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Latest Close Price", f"${latest_close:.2f}")
        
        if not pd.isna(latest_vol):
            m2.metric(f"{window}-Day Historical Vol", f"{latest_vol:.2f}%")
        else:
            m2.metric(f"{window}-Day Historical Vol", "N/A")
            
        if latest_hvr is not None:
            m3.metric("Historical Vol Rank (HVR)", f"{latest_hvr:.1f}")
        else:
            m3.metric("Historical Vol Rank (HVR)", "N/A")
            
        if current_iv is not None:
            m4.metric("Current Implied Vol (IV)", f"{current_iv:.2f}%")
        else:
            m4.metric("Current Implied Vol (IV)", "N/A")
            
        st.markdown("---")
        
        # Plotly chart
        fig = go.Figure()
        
        # Price trace
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'],
            name="Price",
            line=dict(color="#00ADB5", width=2),
            yaxis="y1"
        ))
        
        # Volatility trace
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Volatility'],
            name=f"{window}-Day Historical Volatility",
            line=dict(color="#F8B195", width=2, dash="dot"),
            yaxis="y2"
        ))
        
        # Update layout for dual axis
        fig.update_layout(
            title=f"{ticker.upper()} Price & Historical Volatility",
            xaxis=dict(title="Date", showgrid=False),
            yaxis=dict(
                title="Price ($)",
                title_font=dict(color="#00ADB5"),
                tickfont=dict(color="#00ADB5"),
                showgrid=True,
                gridcolor="rgba(255,255,255,0.1)"
            ),
            yaxis2=dict(
                title="Historical Volatility (%)",
                title_font=dict(color="#F8B195"),
                tickfont=dict(color="#F8B195"),
                anchor="x",
                overlaying="y",
                side="right",
                showgrid=False
            ),
            legend=dict(x=0.01, y=0.99, bgcolor="rgba(0,0,0,0)"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.warning("No data found for the given parameters. Please check the ticker symbol and dates.")
