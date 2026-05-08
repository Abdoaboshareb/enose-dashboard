import streamlit as st
import requests
import time
import pandas as pd
import plotly.express as px

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
    # THE BUTTON (UI only for now)
    if st.button("🚀 Request New Scan", use_container_width=True):
        st.info("Scan command sent! (Logic not yet implemented)")

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
timestamp = data.get("timestamp", "N/A")
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
    df = pd.DataFrame({
        "Time": range(len(raw_curve)),
        "Sensor Reading": raw_curve
    })

    fig = px.line(
        df, 
        x="Time", 
        y="Sensor Reading", 
        title="Live Chemical Signature (Spectral Array)",
        labels={"Sensor Reading": "Amplitude", "Time": "Sensor Index (0-256)"},
        template="plotly_dark"
    )
    fig.update_traces(line=dict(color="#00FFAA", width=2))
    
    # Add a slight glow effect to the line
    fig.update_layout(
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20)
    )

    st.plotly_chart(fig, use_container_width=True, key="live_sensor_chart")
else:
    st.info("⏳ Waiting for the sensor to emit gas signatures...")

# --- AUTO REFRESH ---
time.sleep(REFRESH_RATE)
st.rerun()
