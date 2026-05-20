import streamlit as st
import requests
import time
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo

# --- CONFIGURATION ---
# Replace with your Hugging Face URL
API_URL = "https://abdulrahman-266-enose-api.hf.space/latest"
REFRESH_RATE = 2 # seconds

# Streamlit Page Config
st.set_page_config(
    page_title="E-Nose Live Monitor",
    page_icon="👃",
    layout="wide"
)

# Custom Styling for the Prediction Metric
st.markdown("""
    <style>
    .prediction-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #1E1E1E;
        border: 1px solid #333;
        text-align: center;
    }
    .prediction-val {
        font-size: 40px;
        font-weight: bold;
    }
    .good-text { color: #00FFAA; }
    .bad-text { color: #FF4B4B; }
    </style>
    """, unsafe_allow_html=True)

st.title("👃 E-Nose Real-Time Monitor")
st.markdown("Monitoring live chemical signatures and predicting Quality using AI.")

# --- SIDEBAR / CONTROL ---
with st.sidebar:
    st.header("Controls")
    if st.button("🚀 Request New Scan", use_container_width=True):
        try:
            # Tell the API to set scan_requested to True
            # Replace URL with your actual HF URL
            resp = requests.post("https://abdulrahman-266-enose-api.hf.space/trigger_scan")
            if resp.status_code == 200:
                st.toast("Scan command sent!")
            else:
                st.toast("Failed to send command.")
        except Exception as e:
            st.error(f"Error: {e}")
            
def fetch_latest_data():
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

data = fetch_latest_data()

if data is None:
    st.error("🔴 Cannot connect to the AI Server. Please ensure the Hugging Face Space is running.")
    time.sleep(REFRESH_RATE)
    st.rerun()

# --- TOP METRIC SECTION ---
predicted_label = data.get("predicted_label", "Waiting...")
raw_timestamp = data.get("timestamp", "")

try:
    # Convert ISO string to datetime
    dt = datetime.fromisoformat(raw_timestamp)

    # Convert to Egypt time
    egypt_time = dt.astimezone(ZoneInfo("Africa/Cairo"))

    # Nice readable format
    timestamp = egypt_time.strftime("%d %b %Y • %I:%M:%S %p")

except:
    timestamp = raw_timestampraw_curve = data.get("raw_curve", [])
raw_curve = data.get("raw_curve", [])
# Determine color based on prediction
color_class = "good-text" if predicted_label == "Good" else "bad-text" if predicted_label == "Bad" else ""

st.markdown(f"""
    <div class="prediction-card">
        <p style="margin:0; color: #888;">LATEST PREDICTED QUALITY</p>
        <div class="prediction-val {color_class}">{predicted_label}</div>
        <p style="margin:0; color: #555; font-size: 12px;">Last Update: {timestamp}</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- CHART SECTION ---
if len(raw_curve) > 0:
    # 1. Fix the "Flipped" view: 
    # We reverse the data points so the first index becomes the last and vice-versa
    fixed_curve = raw_curve[::-1] 

    # 2. Map the 257 points to the 1000nm - 5000nm range
    # np.linspace creates exactly 257 values starting at 1000 and ending at 5000
    wavelengths = np.arange(len(fixed_curve))
    df = pd.DataFrame({
        "Wavelength": wavelengths,
        "PSD": fixed_curve
    })

    # 3. Build the Chart
    fig = px.line(
        df, 
        x="Wavelength", 
        y="PSD", 
        title="Live Chemical Signature (Spectral Analysis)",
        labels={
            "PSD": "PSD (A.U.)", 
            "Wavelength": "Sensor reading index"
        },
        template="plotly_dark"
    )

    # Styling the line and axes
    fig.update_traces(line=dict(color="#00FFAA", width=2.5))
    
    fig.update_layout(
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20),
         xaxis=dict(
            gridcolor="#333",
            showgrid=True,
            zeroline=False,
        
            # Show axis numbers
            tickmode="linear",
            tick0=0,
            dtick=25,
        
            # Force axis range
            range=[0, 256]
        ),
        yaxis=dict(
            gridcolor="#333", 
            showgrid=True,
            zeroline=False
        )
    )

    st.plotly_chart(fig, use_container_width=True, key="live_sensor_chart")

else:
    st.info("⏳ Waiting for the sensor to emit gas signatures...")
# --- HISTORY SECTION ---
st.subheader("📜 Recent Scan History")

history = data.get("history", [])

if history:
    # Create a clean table-like view using Streamlit columns
    # Header
    hcol1, hcol2 = st.columns([1, 2])
    hcol1.markdown("**Result**")
    hcol2.markdown("**Time**")
    st.divider()
    
    for item in history:
        col1, col2 = st.columns([1, 2])
    
        # Style the result (Good/Bad)
        res = item.get("prediction", "N/A")
        color = "green" if res == "Good" else "red"
        col1.markdown(f":{color}[{res}]")
        raw_timestamp = data.get("timestamp", "")
    
    try:
        # Convert ISO string to datetime
        dt = datetime.fromisoformat(raw_timestamp)
    
        # Convert to Egypt time
        egypt_time = dt.astimezone(ZoneInfo("Africa/Cairo"))
    
        # Nice readable format
        timestamp = egypt_time.strftime("%d %b %Y • %I:%M:%S %p")
    
    except:
        timestamp = raw_timestampraw_curve = data.get("raw_curve", [])
    
        col2.write(timestamp)
else:
    st.info("No scan history available yet.")

# --- AUTO REFRESH ---
time.sleep(REFRESH_RATE)
st.rerun()
