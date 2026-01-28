import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

from api import (
    get_plants,
    get_predictions_by_plant_id,
    get_measurements_by_plant_id,
    get_panels_by_plant_id,
    get_measurements_by_panel_id,
    get_predictions_by_panel_id,
    get_report,
    get_new_prediction_by_plant_id,
    get_new_prediction_by_panel_id,
    get_LSTM_measurements_by_plant_id_and_panel_id,
    get_LSTM_predictions_by_plant_id_and_panel_id
)


st.set_page_config(page_title="Plants Dashboard", layout="wide")
st.title("Plant Monitoring Dashboard")

START_TIME = "2020-06-14T10:45:00"
TIME_STEP_MINUTES = 15

if "sim_time" not in st.session_state:
    st.session_state.sim_time = datetime.fromisoformat(START_TIME)

if "selected_panel_id" not in st.session_state:
    st.session_state.selected_panel_id = None

if "selected_panel_number" not in st.session_state:
    st.session_state.selected_panel_number = None

st.sidebar.header("Select a plant")

plants = get_plants()
if not plants:
    st.sidebar.error("No plants available")
    st.stop()

plant_name_to_id = {p["name"]: p["id"] for p in plants}

selected_plant_name = st.sidebar.selectbox(
    "Plant",
    options=list(plant_name_to_id.keys())
)

selected_plant_id = plant_name_to_id[selected_plant_name]


# --------------------------------------------------
# Sidebar: time control
# --------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### Time control")

st.sidebar.caption(f"Current simulated time: {st.session_state.sim_time.isoformat()}")

col1, col2, col3 = st.sidebar.columns(3)
with col1:
    if st.button("-15"):
        st.session_state.sim_time -= timedelta(minutes=TIME_STEP_MINUTES)
with col2:
    if st.button("Reset"):
        st.session_state.sim_time = datetime.fromisoformat(START_TIME)
with col3:
    if st.button("+15"):
        st.session_state.sim_time += timedelta(minutes=TIME_STEP_MINUTES)

sim_time_str = st.session_state.sim_time.isoformat()

next_sim_time_str = (st.session_state.sim_time + timedelta(minutes=15)).isoformat()

panels = get_panels_by_plant_id(plant_id=selected_plant_id)

drift_summary = {}
if panels:
    start_drift = (st.session_state.sim_time - timedelta(hours=24)).isoformat()
    drift_summary = get_report(selected_plant_id, st.session_state.sim_time.date().isoformat())


def to_dataframe(data):
    if not data:
        return pd.DataFrame(columns=["timestamp", "ac_power"])
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df.sort_values("timestamp")

# --------------------------------------------------
# Plant-level view
# --------------------------------------------------
st.subheader(f"Selected plant: {selected_plant_name}")

measurements = get_measurements_by_plant_id(
    plant_id=selected_plant_id,
    start_time = (st.session_state.sim_time - timedelta(hours=24)).isoformat(),
    end_time=sim_time_str,
)

past_predictions = get_predictions_by_plant_id(
    plant_id=selected_plant_id,
    start_time = (st.session_state.sim_time - timedelta(hours=24)).isoformat(),
    end_time=sim_time_str,
)

future_pred = get_new_prediction_by_plant_id(selected_plant_id, next_sim_time_str)

df_m = to_dataframe(measurements)
df_p = to_dataframe(past_predictions)

if future_pred:
    df_future = pd.DataFrame([future_pred])
    df_future["timestamp"] = pd.to_datetime(df_future["timestamp"])
    df_p = pd.concat([df_p, df_future]).sort_values("timestamp")

st.markdown("### Measurements vs Predictions")
if not df_m.empty or not df_p.empty:
    df_m["type"] = "measured"
    df_p["type"] = "predicted"

    combined = pd.concat([df_m, df_p])

    st.line_chart(
        combined.pivot(
            index="timestamp",
            columns="type",
            values="ac_power",
        ),
        color=["#1f77b4", "#ff7f0e"]
    )
else:
    st.info("No data to display")


# --------------------------------------------------
# Report button
# --------------------------------------------------

st.markdown("---")
st.subheader("Daily Performance Report")

report_day = st.session_state.sim_time.date() - timedelta(days=1)
report_day = report_day.isoformat()

if st.button(f"Generate Report for {report_day}"):
    
    
    with st.spinner(f"Calculating KPIs for {report_day}..."):
        report_data = get_report(selected_plant_id, report_day)
    
    if report_data:
        
        total_kpi = report_data['total_kpi']
        total_drifts = report_data['total_drifts']
        kpi_dict = report_data["panels_kpis"]
        drift_dict = report_data["panels_drifts"]

        col_a, col_b = st.columns(2)
        col_a.metric(label="Plant Total KPI (Error %)", value=f"{total_kpi:.2f}%")
        col_b.metric(label="Total Drifts", value=total_drifts)
        
        st.markdown("#### KPI per Panel")
        
        if kpi_dict:
            
            df_kpi = pd.DataFrame(list(kpi_dict.items()), columns=["Panel ID", "Error %"])
            df_drift = pd.DataFrame(list(drift_dict.items()), columns=["Panel ID", "Drifts"])
            
            report_df = pd.merge(df_kpi, df_drift, on="Panel ID")

            def get_color(drifts):
                if drifts == 0:
                    return "Stable (0 Drifts)"
                elif drifts <= 2:
                    return "Warning (1-2 Drifts)"
                else:
                    return "Critical (3+ Drifts)"

            report_df["Status"] = report_df["Drifts"].apply(get_color)

            fig = px.bar(
                report_df,
                x="Panel ID",
                y="Error %",
                color="Status",
                color_discrete_map={
                    "Stable (0 Drifts)": "#2ecc71",   # Green
                    "Warning (1-2 Drifts)": "#f1c40f", # Yellow
                    "Critical (3+ Drifts)": "#e74c3c"  # Red
                },
                hover_data=["Drifts", "Error %"],
                title=f"Panel Performance for {report_day}"
            )

            fig.update_layout(xaxis_tickangle=-45)
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(report_df.sort_values("Error %", ascending=False), use_container_width=True)
        else:
            st.warning("No panel data found for this day.")
    else:
        st.error("Could not generate report. Ensure historical predictions exist for this day.")


# --------------------------------------------------
# Panels list
# --------------------------------------------------

if panels:
    st.markdown("### Panels Status")

    drifts_dict = drift_summary.get("panels_drifts", {}) if drift_summary else {}

    cols = st.columns(6)
    for i, panel in enumerate(panels):
        panel_id = panel["id"]
        panel_label = f"Panel {i + 1}"

        drift_count = drifts_dict.get(panel_id, 0)
        
        if drift_count == 0:
            status_color = "green"
            status_icon = "🟢"
        elif drift_count <= 2:
            status_color = "orange"
            status_icon = "🟡"
        else:
            status_color = "red"
            status_icon = "🔴"

        
        with cols[i % 6]:
            st.markdown(f"<p style='text-align:center; margin-bottom:-10px;'>{status_icon}</p>", unsafe_allow_html=True)
            if st.button(panel_label, key=f"btn_{panel_id}", use_container_width=True):
                st.session_state.selected_panel_id = panel_id
                st.session_state.selected_panel_number = i + 1
                st.rerun()
else:
    st.info("No panels available")


# --------------------------------------------------
# Panel-level view
# --------------------------------------------------

if st.session_state.selected_panel_id:
    panel_id = st.session_state.selected_panel_id
    panel_number = st.session_state.selected_panel_number

    st.markdown("---")
    st.subheader(f"Panel {panel_number} Detail")
    st.markdown(f"panel id: {panel_id}")

    with st.spinner("Loading panel data..."):
        p_start = (st.session_state.sim_time - timedelta(hours=24)).isoformat()
        
        p_measurements = get_measurements_by_panel_id(selected_plant_id, panel_id, p_start, sim_time_str)
        
        p_predictions = get_predictions_by_panel_id(selected_plant_id, panel_id, p_start, sim_time_str)
        
        p_future = get_new_prediction_by_panel_id(selected_plant_id, panel_id, next_sim_time_str)
        if p_future:
            p_predictions.extend(p_future)

    df_pm = to_dataframe(p_measurements)
    df_pp = to_dataframe(p_predictions)

    if not df_pm.empty or not df_pp.empty:
        df_pm["type"] = "measured"
        df_pp["type"] = "predicted"
        combined_panel = pd.concat([df_pm, df_pp])
        st.line_chart(
            combined_panel.pivot(index="timestamp", columns="type", values="ac_power"),
            color=["#1f77b4", "#ff7f0e"]
        )

    st.markdown("---")
    st.subheader(f"Panel {panel_number} LSTM predictions")
    st.markdown(f"These predictions shows the difference between the actual 24 hours and the predicted ones. They are stored in memory and they are not elaborated in realtime, referring to the day 16/06/2020. This is only a proof of concept.")
    with st.spinner("Loading LSTM data..."):
        lstm_measurements = get_LSTM_measurements_by_plant_id_and_panel_id(selected_plant_id, panel_id)
        lstm_predictions = get_LSTM_predictions_by_plant_id_and_panel_id(selected_plant_id, panel_id)
    df_lstm_m = to_dataframe(lstm_measurements)
    df_lstm_p = to_dataframe(lstm_predictions)

    if not df_lstm_m.empty and not df_lstm_p.empty:
        df_lstm_m["type"] = "measured"
        df_lstm_p["type"] = "predicted"

        combined_panel = pd.concat([df_lstm_m, df_lstm_p])

        st.line_chart(
            combined_panel.pivot(index="timestamp", columns="type", values="ac_power"),
            color=["#1f77b4", "#ff7f0e"]
        )

    if st.button("Clear panel selection"):
        st.session_state.selected_panel_id = None
        st.rerun()