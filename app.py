import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="Volatility Dashboard", layout="wide", page_icon="📈")

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

st.title("📈 Real-Time Volatility Dashboard")
st.markdown("Analyze historical stock price and its annualized rolling volatility. Designed for institutional-grade visual clarity.")

# Sidebar for inputs
with st.sidebar:
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

if ticker:
    with st.spinner(f"Fetching data for {ticker}..."):
        df = load_data(ticker, start_date, end_date)
        
    if df is not None and not df.empty:
        # Ticker.history gives standard camel case column names like 'Close', 'Open' without MultiIndex.
        df['Return'] = df['Close'].pct_change()

        # Calculate annualized rolling volatility (std dev * sqrt(252 trading days))
        df['Volatility'] = df['Return'].rolling(window=window).std() * (252 ** 0.5) * 100 # In percentage
        
        # Latest metrics
        latest_close = float(df['Close'].iloc[-1])
        latest_vol = float(df['Volatility'].iloc[-1])
        
        # Layout columns for metrics
        m1, m2 = st.columns(2)
        m1.metric("Latest Close Price", f"${latest_close:.2f}")
        if not pd.isna(latest_vol):
            m2.metric(f"{window}-Day Annualized Volatility", f"{latest_vol:.2f}%")
        else:
            m2.metric(f"{window}-Day Annualized Volatility", "N/A")
            
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
            name=f"{window}-Day Volatility (%)",
            line=dict(color="#F8B195", width=2, dash="dot"),
            yaxis="y2"
        ))
        
        # Update layout for dual axis
        fig.update_layout(
            title=f"{ticker.upper()} Price & Volatility",
            xaxis=dict(title="Date", showgrid=False),
            yaxis=dict(
                title="Price ($)",
                titlefont=dict(color="#00ADB5"),
                tickfont=dict(color="#00ADB5"),
                showgrid=True,
                gridcolor="rgba(255,255,255,0.1)"
            ),
            yaxis2=dict(
                title="Volatility (%)",
                titlefont=dict(color="#F8B195"),
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
