import streamlit as st
import pandas as pd
from api import get_plants, get_predictions_by_plant_id, get_measurements_by_plant_id, get_panels_by_plant_id, get_meaurements_by_panel_id, get_predictions_by_panel_id



st.set_page_config(page_title="Plants Dashboard", layout="wide")

st.title("Plant Monitoring Dashboard")

st.sidebar.header("Select a plant")

plants = get_plants()

if not plants:
    st.sidebar.error("No plants available")
    st.stop()

plant_name_to_id = {
    plant["name"]: plant["id"]
    for plant in plants
}

selected_plant_name = st.sidebar.selectbox(
    "Plant",
    options=list(plant_name_to_id.keys())
)

selected_plant_id = plant_name_to_id[selected_plant_name]



st.subheader(f"Selected plant: {selected_plant_name}")


measurement = get_measurements_by_plant_id(selected_plant_id)
predictions = get_predictions_by_plant_id(selected_plant_id)

def to_dataframe(data):
    if not data:
        return pd.DataFrame(columns=["timestamp", "power"])
    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df.sort_values("timestamp")

df_measurements = to_dataframe(measurement)
df_predictions = to_dataframe(predictions)


st.markdown("### Measurements vs Predictions")

if not df_measurements.empty or not df_predictions.empty:
    df_measurements["type"] = "measured"
    df_predictions["type"] = "predicted"

    combined = pd.concat([df_measurements, df_predictions])

    st.line_chart(
        combined.pivot(
            index="timestamp",
            columns="type",
            values="ac_power"
        )
    )
else:
    st.info("No data to display")





# --------------------------------------------------
# Panels 
# --------------------------------------------------

if "selected_panel_id" not in st.session_state:
    st.session_state.selected_panel_id = None
    

panels = get_panels_by_plant_id(selected_plant_id)

if panels:
    st.markdown("### Panels")

    cols = st.columns(4)

    for i, panel in enumerate(panels):
        with cols[i % 4]:
            if st.button(f"Panel {i + 1}", use_container_width=True):
                st.session_state.selected_panel_id = panel["id"]
else:
    st.info("No panels available for this plant")



if st.session_state.selected_panel_id is not None:
    panel_id = st.session_state.selected_panel_id

    st.markdown("---")
    st.subheader("Panel measurements vs predictions")

    panel_measurements = get_meaurements_by_panel_id(panel_id)
    panel_predictions = get_predictions_by_panel_id(panel_id)

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
                values="ac_power"
            )
        )
    else:
        st.info("No data available for this panel")

    if st.button("Clear panel selection"):
        st.session_state.selected_panel_id = None
