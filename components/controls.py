import streamlit as st
import json
import os

# Load material presets
PRESETS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "material_presets.json")
with open(PRESETS_FILE, "r") as f:
    PRESETS = json.load(f)

def on_preset_change():
    """Callback triggered when the user selects a new preset."""
    preset = st.session_state.material_preset_val
    if preset != "Custom":
        st.session_state.ef_slider_val = PRESETS[preset]

def on_slider_change():
    """Callback triggered when the user manually moves the slider."""
    val = st.session_state.ef_slider_val
    # Snap selectbox to a preset if it exactly matches, otherwise revert to Custom
    matched = "Custom"
    for k, v in PRESETS.items():
        if k != "Custom" and abs(v - val) < 1e-4:
            matched = k
            break
    st.session_state.material_preset_val = matched

def render_controls(active_tab="Fermi-Dirac Distribution"):
    """
    Renders sliders and dropdowns for the Visualizer sidebar.
    Returns depends on the active tab.
    """
    with st.sidebar:
        st.header("Controls Configuration")
        st.markdown("---")
        
        if "ef_slider_val" not in st.session_state:
            st.session_state.ef_slider_val = 0.00
        if "material_preset_val" not in st.session_state:
            st.session_state.material_preset_val = "Custom"
            
        preset_names = list(PRESETS.keys())
        
        if active_tab == "Fermi-Dirac Distribution":
            with st.expander("Advanced Material Presets", expanded=True):
                st.radio(
                    "Select Preset",
                    options=preset_names,
                    key="material_preset_val",
                    on_change=on_preset_change,
                    label_visibility="collapsed"
                )
            
            T = st.slider(
                "Temperature (K)",
                min_value=0, max_value=1000, value=300, step=1,
                help="Adjust the absolute temperature of the system."
            )
            
            E_F = st.slider(
                "Fermi Energy (eV)",
                min_value=-0.50, max_value=0.50, step=0.01,
                key="ef_slider_val", on_change=on_slider_change,
                help="Adjust the core Energy Fermi Level relative to intrinsic state."
            )
            
            return {"T": T, "E_F": E_F}
        else:
            na_exp = st.slider(
                "Acceptor Doping N_A (10^x cm⁻³)",
                min_value=14.0, max_value=18.0, value=16.0, step=0.1,
                help="Logarithmic scale for P-type doping."
            )
            nd_exp = st.slider(
                "Donor Doping N_D (10^x cm⁻³)",
                min_value=14.0, max_value=18.0, value=16.0, step=0.1,
                help="Logarithmic scale for N-type doping."
            )
            T = st.slider(
                "Temperature (K)",
                min_value=200, max_value=400, value=300, step=1,
                help="Adjust the ambient thermal energy."
            )
            
            return {"N_A": 10**na_exp, "N_D": 10**nd_exp, "T": T}
