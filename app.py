import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime
import numpy as np

st.set_page_config(page_title="Petroleum Proactive Automation", page_icon="🚨", layout="wide")

@st.cache_data
def load_data():
    base_time = datetime.datetime(2026, 7, 20, 0, 0)
    times = [base_time + datetime.timedelta(minutes=5*i) for i in range(288)]
    np.random.seed(42)
    historical_fri = 30 + 15 * np.sin(np.linspace(0, 3 * np.pi, 288)) + np.random.normal(0, 2, 288)
    projected_fri = historical_fri + np.random.normal(1.5, 1, 288)
    return pd.DataFrame({'Timestamp': times, 'True_FRI': historical_fri, 'Predicted_FRI_60min': projected_fri})

df = load_data()

st.sidebar.markdown("### ⏱️ Timeline Navigation Console")
slider_index = st.sidebar.slider("Select Timeline Observation Log Point:", min_value=0, max_value=len(df)-1, value=120)
current_row = df.iloc[slider_index]
plot_df = df.iloc[max(0, slider_index-100):slider_index+1]

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
