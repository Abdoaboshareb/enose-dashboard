# dashboard.py
import streamlit as st
import requests
import time
import pandas as pd
import plotly.express as px

# Configuration
API_URL = "https://abdulrahman-266-enose-api.hf.space/latest"
REFRESH_RATE = 2  # seconds

# Streamlit Page Config
st.set_page_config(
    page_title="E-Nose Live Dashboard",
    page_icon="👃",
    layout="wide"
)

st.title("👃 E-Nose Real-Time Monitor")
st.markdown("Monitoring the live chemical signatures and predicting Quality (Good/Bad) using our deployed Machine Learning model.")

def fetch_latest_data():
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.ConnectionError:
        return None

data = fetch_latest_data()

if data is None:
    st.error("🔴 Cannot connect to the FastAPI server. Is `api_server.py` running?")
    time.sleep(REFRESH_RATE)
    st.rerun()

st.success(f"🟢 Connected to server. Last update: {data.get('timestamp', 'N/A')}")

predicted_label = data.get("predicted_label", "Waiting for data...")
actual_label = data.get("actual_label", "Unknown")
raw_curve = data.get("raw_curve", [])

# Check if correct (Compare predicted Quality to actual Quality)
is_correct = predicted_label == actual_label
status_color = "#4CAF50" if is_correct else "#F44336"
status_icon = "✅ Correct" if is_correct else "❌ Incorrect"

# If we are just starting and have no data, hide the correctness
if predicted_label == "Waiting for data...":
    status_color = "#4CAF50"
    status_icon = "⏳ Waiting"
    actual_label = "-"

# Display the metric using columns
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
        <div style="background-color: #1e1e1e; padding: 20px; border-radius: 10px; text-align: center; border: 2px solid {status_color};">
            <h2 style="color: {status_color}; margin-bottom: 0;">Predicted Quality</h2>
            <h1 style="font-size: 3rem; margin-top: 10px;">{predicted_label}</h1>
            <h3 style="color: {status_color}; margin-top: 5px;">{status_icon}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div style="background-color: #1e1e1e; padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #555;">
            <h2 style="color: #bbb; margin-bottom: 0;">Actual Quality (Ground Truth)</h2>
            <h1 style="font-size: 3rem; margin-top: 10px; color: #ddd;">{actual_label}</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

# Display the chart
if len(raw_curve) > 0:
    df = pd.DataFrame({
        "Time": range(len(raw_curve)),
        "Sensor Reading": raw_curve
    })
    
    # Using Plotly for a beautiful interactive chart
    fig = px.line(
        df, 
        x="Time", 
        y="Sensor Reading", 
        title="Live Sensor Chemical Curve",
        labels={"Sensor Reading": "Amplitude", "Time": "Time Step (0-256)"},
        template="plotly_dark"
    )
    fig.update_traces(line=dict(color="#00FFAA", width=2))
    
    st.plotly_chart(fig, use_container_width=True, key="live_sensor_chart")
else:
    st.info("Waiting for the mock sensor to emit gas signatures...")
        
# Wait before the next refresh
time.sleep(REFRESH_RATE)
st.rerun()
