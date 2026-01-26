import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from api import (
    get_plants,
    get_predictions_by_plant_id,
    get_measurements_by_plant_id,
    get_panels_by_plant_id,
    get_meaurements_by_panel_id,
    get_predictions_by_panel_id,
)


st.set_page_config(page_title="Plants Dashboard", layout="wide")
st.title("Plant Monitoring Dashboard")

START_TIME = "2020-06-14T10:45:00"
TIME_STEP_MINUTES = 15

if "sim_time" not in st.session_state:
    st.session_state.sim_time = datetime.fromisoformat(START_TIME)

if "selected_panel_id" not in st.session_state:
    st.session_state.selected_panel_id = None

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
    if st.button("Previous 15 minutes"):
        st.session_state.sim_time -= timedelta(minutes=TIME_STEP_MINUTES)
with col2:
    if st.button("Next 15 minutes"):
        st.session_state.sim_time += timedelta(minutes=TIME_STEP_MINUTES)
with col3:
    if st.button("⟲ Reset"):
        st.session_state.sim_time = datetime.fromisoformat(START_TIME)

sim_time_str = st.session_state.sim_time.isoformat()


# --------------------------------------------------
# Helper to convert API data to DataFrame
# --------------------------------------------------
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
    selected_plant_id,
    time=sim_time_str,
)

predictions = get_predictions_by_plant_id(
    selected_plant_id,
    time=sim_time_str,
)

df_m = to_dataframe(measurements)
df_p = to_dataframe(predictions)

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
        )
    )
else:
    st.info("No data to display")

# --------------------------------------------------
# Panels list
# --------------------------------------------------
panels = get_panels_by_plant_id(selected_plant_id)

if panels:
    st.markdown("### Panels")
    cols = st.columns(6)
    for i, panel in enumerate(panels):
        with cols[i % 6]:
            if st.button(f"Panel {i + 1}", use_container_width=True):
                st.session_state.selected_panel_id = panel["id"]
else:
    st.info("No panels available")

# --------------------------------------------------
# Panel-level view
# --------------------------------------------------
if st.session_state.selected_panel_id:
    panel_id = st.session_state.selected_panel_id

    st.markdown("---")
    st.subheader(f"Panel {panel_id} — measurements vs predictions")

    panel_measurements = get_meaurements_by_panel_id(
        selected_plant_id,
        panel_id,
        time=sim_time_str,
    )

    panel_predictions = get_predictions_by_panel_id(
        selected_plant_id,
        panel_id,
        time=sim_time_str,
    )

    df_pm = to_dataframe(panel_measurements)
    df_pp = to_dataframe(panel_predictions)

    if not df_pm.empty or not df_pp.empty:
        df_pm["type"] = "measured"
        df_pp["type"] = "predicted"

        combined_panel = pd.concat([df_pm, df_pp])

        st.line_chart(
            combined_panel.pivot(
                index="timestamp",
                columns="type",
                values="ac_power",
            )
        )
    else:
        st.info("No data available for this panel")

    if st.button("Clear panel selection"):
        st.session_state.selected_panel_id = None
