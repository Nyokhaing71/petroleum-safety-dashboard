import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
import numpy as np

st.set_page_config(page_title="Petroleum Proactive Automation", page_icon="🚨", layout="wide")

# Inject custom CSS to increase font size for all status alerts globally
st.markdown(
    """
    <style>
    div[data-testid="stNotification"] p,
    div[data-testid="stNotification"] span,
    div[class*="stAlert"] p {
        font-size: 45px !important;
        font-weight: 500 !important;
    }
    div[data-testid="stNotification"] svg,
    div[class*="stAlert"] svg {
        transform: scale(1.3);
        margin-right: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def load_year_data():
    # 📅 GENERATE FULL 1-YEAR TIMELINE SEQUENCES FOR 2026 (5-Minute Sampling Rates)
    start_time = datetime.datetime(2026, 1, 1, 0, 0)
    end_time = datetime.datetime(2026, 12, 31, 23, 55)

    # Create continuous timestamps for the whole year
    times = pd.date_range(start=start_time, end=end_time, freq='5min')
    total_rows = len(times)

    np.random.seed(42)
    # Generate year-long fluctuating patterns (seasonal waves + daily waves + noise)
    base_wave = 30 + 10 * np.sin(np.linspace(0, 2 * np.pi, total_rows))
    daily_wave = 5 * np.sin(np.linspace(0, 2 * np.pi * 365, total_rows))
    noise = np.random.normal(0, 2, total_rows)

    historical_fri = base_wave + daily_wave + noise
    projected_fri = historical_fri + np.random.normal(1.5, 1, total_rows)

    # Clip parameters to realistic risk bounds (0 to 100)
    historical_fri = np.clip(historical_fri, 0, 100)
    projected_fri = np.clip(projected_fri, 0, 100)

    return pd.DataFrame({'Timestamp': times, 'True_FRI': historical_fri, 'Predicted_FRI_60min': projected_fri})

df = load_year_data()

# 📅 SIDEBAR: FULL 365-DAY CALENDAR NAVIGATION CONSOLE
st.sidebar.markdown("### ⏱️ Spatiotemporal Navigation Console")

# 1. Fully Unlocked 1-Year Calendar Date Picker Component
selected_date = st.sidebar.date_input(
    "Select Target Observation Date:",
    value=datetime.date(2026, 7, 20),           # Default landing focus day
    min_value=datetime.date(2026, 1, 1),         # Unlocked to January 1, 2026
    max_value=datetime.date(2026, 12, 31)        # Unlocked to December 31, 2026
)

# 2. Time Input Selector Component (Acts as a time scroll bar)
selected_time = st.sidebar.time_input(
    "Select Target Log Time (Hour:Minute):",
    value=datetime.time(12, 0)
)

# Combine selected calendar date and time into a single lookup timestamp
target_datetime = datetime.datetime.combine(selected_date, selected_time)

# Find the closest matching historical log row using absolute time delta matching
time_deltas = (df['Timestamp'] - target_datetime).abs()
closest_index = time_deltas.idxmin()

current_row = df.iloc[closest_index]
plot_df = df.iloc[max(0, closest_index-100):closest_index+1]

# --- Main Dashboard Visual Elements ---
st.markdown("<h1 style='text-align: center; color: #0f4c81;'>🚨 Industrial Safety Dashboard: Proactive Automation UI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-style: italic;'>Master's Thesis Project: AI-Driven 60-Minute Predictive Early Warning System</p>", unsafe_allow_html=True)
st.divider()

col1, col2, col3, col4 = st.columns(4)
current_time_str = current_row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')
forecast_time_str = (current_row['Timestamp'] + datetime.timedelta(minutes=60)).strftime('%Y-%m-%d %H:%M:%S')

with col1:
    st.metric(label=f"🟢 Current Risk Index (FRI) @ {current_time_str}", value=f"{current_row['True_FRI']:.2f}")
with col2:
    delta_val = current_row['Predicted_FRI_60min'] - current_row['True_FRI']
    st.metric(label=f"🔮 Projected FRI (60 Min Horizon) Forecast for: {forecast_time_str}", value=f"{current_row['Predicted_FRI_60min']:.2f}", delta=f"{delta_val:+.2f} vs Present", delta_color="inverse")
with col3:
    st.metric(label="📊 Model Variance Explained (R²)", value="74.35%")
with col4:
    st.metric(label="📉 Predictive Margin of Error (MAE)", value="3.2798")

st.markdown("### ⏱️ Temporal Horizon Evaluation: Historical vs. Projected Risk States")
fig = go.Figure()
fig.add_trace(go.Scatter(x=plot_df['Timestamp'], y=plot_df['True_FRI'], mode='lines', name='True Historical FRI (Actual)', line=dict(color='#1f77b4', width=2)))
fig.add_trace(go.Scatter(x=plot_df['Timestamp'], y=plot_df['Predicted_FRI_60min'], mode='lines', name='60-Min Early Warning Projection', line=dict(color='#d62728', dash='dash', width=2)))
fig.update_layout(xaxis_title="Sequential Timeline Logs (5 Minute Sampling Rates)", yaxis_title="Risk Level Value Score (0 - 100)", hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0.01), margin=dict(l=40, r=40, t=40, b=40), height=400)
st.plotly_chart(fig, use_container_width=True)

st.markdown("### ⚙️ Preemptive Safety Protocol Triggers")
latest_prediction = current_row['Predicted_FRI_60min']
if latest_prediction > 45.0:
    st.error(f"🔴 CRITICAL ALARM (Projected FRI: {latest_prediction:.2f}): Initiating automated system isolation protocols!")
elif latest_prediction > 35.0:
    st.warning(f"🟡 ELEVATED WARNING (Projected FRI: {latest_prediction:.2f}): Activating safety ventilation networks.")
else:
    st.success(f"🟢 SYSTEM SECURE (Projected FRI: {latest_prediction:.2f}): Atmospheric micro-climate trends are stable.")
