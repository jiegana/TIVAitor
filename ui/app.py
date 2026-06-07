import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from core.patient import Patient
from core.models.propofol import PropofolMarsh, PropofolModifiedMarsh
from core.engine import run_simulation

# 1. Set up the page
st.set_page_config(page_title="TIVAitor", layout="wide")
st.title("💉 TIVAitor: Educational PK Simulator")
st.write("Simulating Real OR Scenarios (Manual Mode)")

# 2. Sidebar: Patient & Model
st.sidebar.header("Patient Demographics")
sex = st.sidebar.radio("Sex", ['M', 'F'], index=0)
age = st.sidebar.number_input("Age (years)", min_value=1, max_value=100, value=40, step=1, format="%d")
height_cm = st.sidebar.number_input("Height (cm)", min_value=100, max_value=250, value=170, step=1, format="%d")
weight_kg = st.sidebar.number_input("Weight (kg)", min_value=30, max_value=200, value=70, step=1, format="%d")

st.sidebar.header("PK Model Selection")
model_choice = st.sidebar.selectbox(
    "Propofol Model",
    ["Marsh (Diprifusor)", "Modified Marsh (Base Primea)"],
    index=1 
)

st.sidebar.header("Simulation Settings")
duration_min = st.sidebar.number_input("Total Duration (min)", min_value=10, max_value=240, value=60, step=10, format="%d")

# --- Display Calculated Patient Metrics ---
st.sidebar.subheader("Calculated Metrics")
my_patient = Patient(age=age, height_cm=height_cm, weight_kg=weight_kg, sex=sex)

col1, col2 = st.sidebar.columns(2)
col1.metric("BMI", f"{my_patient.bmi:.1f} kg/m²")
col2.metric("ABW", f"{my_patient.abw:.1f} kg")

st.sidebar.write("**Ideal Body Weight (IBW)**")
st.sidebar.write(f"• Devine: {my_patient.ibw_devine:.1f} kg")
st.sidebar.write(f"• Robinson: {my_patient.ibw_robinson:.1f} kg")
st.sidebar.write(f"• Lorentz: {my_patient.ibw_lorentz:.1f} kg")

st.sidebar.write("**Lean / Fat-Free Mass**")
st.sidebar.write(f"• LBM (James): {my_patient.lbm_james:.1f} kg")
st.sidebar.write(f"• FFM (Janmahasatian): {my_patient.ffm:.1f} kg")

# 3. Initialize the Event Timeline in Session State
# UPDATED: New defaults (1.5 mg/kg bolus, 4 mg/kg/hr at 10 min, stop at 45 min)
if 'events_list' not in st.session_state:
    default_weight = 70.0 # Based on the default sidebar weight
    bolus_dose = 1.5 * default_weight # 105 mg
    infusion_rate = 4.0               # 4.0 mg/kg/hr
    
    st.session_state.events_list = [
        {'time': 0.0, 'type': 'bolus', 'dose_mg': bolus_dose, 'rate_mg_min': 0.0, 'display': f'Bolus {bolus_dose:.1f} mg (1.50 mg/kg)'},
        {'time': 10.0, 'type': 'infusion', 'dose_mg': 0.0, 'rate_mg_min': (infusion_rate * default_weight)/60.0, 'display': f'Infusion {infusion_rate} mg/kg/hr ({infusion_rate * default_weight:.1f} mg/hr)'},
        {'time': 45.0, 'type': 'stop', 'dose_mg': 0.0, 'rate_mg_min': 0.0, 'display': 'Stop Infusion'}
    ]

# 4. The Dynamic Event Builder Form
st.subheader("Add New Event")
st.write("Build your timeline step-by-step.")

col1, col2 = st.columns(2)
with col1:
    new_time = st.number_input("Time (min)", min_value=0.0, step=1.0, key="input_time")
with col2:
    new_action = st.selectbox("Action", ["bolus", "infusion", "stop"], key="input_action")

new_dose = 0.0
new_rate = 0.0

if new_action == "bolus":
    new_dose = st.number_input("Dose (mg)", min_value=0.0, step=10.0, key="input_dose")
    if new_dose > 0:
        st.caption(f"💊 Equivalent to: **{new_dose / weight_kg:.2f} mg/kg**")
elif new_action == "infusion":
    new_rate = st.number_input("Rate (mg/kg/hr)", min_value=0.0, step=1.0, format="%.1f", key="input_rate")
    if new_rate > 0:
        st.caption(f"💧 Total pump rate: **{new_rate * weight_kg:.1f} mg/hr**")

if st.button("➕ Add Event to Timeline", type="primary"):
    if new_action == "bolus":
        display_str = f"Bolus {new_dose} mg ({new_dose / weight_kg:.2f} mg/kg)"
    elif new_action == "infusion":
        display_str = f"Infusion {new_rate} mg/kg/hr ({new_rate * weight_kg:.1f} mg/hr)"
    else:
        display_str = "Stop Infusion"

    engine_rate = (new_rate * weight_kg) / 60.0 if new_action == 'infusion' else 0.0

    new_event = {
        'time': new_time, 'type': new_action, 'dose_mg': new_dose,
        'rate_mg_min': engine_rate, 'display': display_str
    }
    
    st.session_state.events_list.append(new_event)
    st.session_state.events_list.sort(key=lambda x: x['time'])
    st.rerun()

# 5. Display the Current Timeline
st.subheader("Current Timeline")
if not st.session_state.events_list:
    st.info("No events added yet. Use the form above to add one.")
else:
    for i, event in enumerate(st.session_state.events_list):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"**t = {event['time']} min:** {event['display']}")
        with col2:
            if st.button("Delete", key=f"del_{i}"):
                st.session_state.events_list.pop(i)
                st.rerun()

if st.button(" Reset Timeline to Default"):
    default_weight = 70.0
    bolus_dose = 1.5 * default_weight
    infusion_rate = 4.0
    st.session_state.events_list = [
        {'time': 0.0, 'type': 'bolus', 'dose_mg': bolus_dose, 'rate_mg_min': 0.0, 'display': f'Bolus {bolus_dose:.1f} mg (1.50 mg/kg)'},
        {'time': 10.0, 'type': 'infusion', 'dose_mg': 0.0, 'rate_mg_min': (infusion_rate * default_weight)/60.0, 'display': f'Infusion {infusion_rate} mg/kg/hr ({infusion_rate * default_weight:.1f} mg/hr)'},
        {'time': 45.0, 'type': 'stop', 'dose_mg': 0.0, 'rate_mg_min': 0.0, 'display': 'Stop Infusion'}
    ]
    st.rerun()

# 6. Run the Math Engine
if model_choice == "Marsh (Diprifusor)":
    pk_model = PropofolMarsh()
else:
    pk_model = PropofolModifiedMarsh()

pk_model.set_patient(my_patient)
results = run_simulation(pk_model, st.session_state.events_list, duration_min)
params = pk_model.get_parameters()

# 7. Display the Graph
st.subheader("Concentration-Time Profile")
fig = go.Figure()
fig.add_trace(go.Scatter(x=results.t, y=results.y[0], mode='lines', name='Plasma (Cp)', line=dict(color='blue', width=3)))
fig.add_trace(go.Scatter(x=results.t, y=results.y[3], mode='lines', name='Effect Site (Ce)', line=dict(color='red', width=3, dash='dot')))

fig.update_layout(
    title=f"Propofol Concentrations: {pk_model.name}",
    xaxis_title="Time (minutes)", 
    yaxis_title="Concentration (µg/mL)",
    yaxis=dict(range=[0, None]), 
    # --- UPDATED: Force X-axis grid lines and ticks every 10 minutes ---
    xaxis=dict(dtick=10, tick0=0, showgrid=True),
    hovermode="x unified", 
    template="plotly_white"
)
st.plotly_chart(fig, use_container_width=True)

# 8. Expandable Details
st.subheader("Technical Details")
with st.expander("View Model Parameters"):
    param_df = pd.DataFrame(list(params.items()), columns=['Parameter', 'Value'])
    param_df['Unit'] = ['L', '1/min', '1/min', '1/min', '1/min', '1/min', '1/min']
    st.dataframe(param_df, hide_index=True, use_container_width=True)

with st.expander("View Raw Data Table"):
    df = pd.DataFrame({
        'Time (min)': results.t,
        'Plasma C1 (µg/mL)': results.y[0],
        'Effect Site Ce (µg/mL)': results.y[3]
    })
    st.dataframe(df)