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

def render_controls():
    """
    Renders sliders and dropdowns for the Fermi-Dirac Visualizer sidebar.
    Returns:
        tuple: Selection for (Temperature in K, Fermi Energy in eV)
    """
    with st.sidebar:
        st.header("Controls Configuration")
        st.markdown("---")
        
        # Initialize session state variables safely on first run
        if "ef_slider_val" not in st.session_state:
            st.session_state.ef_slider_val = 0.00
        if "material_preset_val" not in st.session_state:
            st.session_state.material_preset_val = "Custom"
            
        preset_names = list(PRESETS.keys())
        
        # Material Preset Selectbox linked to session state
        st.selectbox(
            "Material Preset",
            options=preset_names,
            key="material_preset_val",
            on_change=on_preset_change
        )
        
        # Temperature slider
        T = st.slider(
            "Temperature (K)",
            min_value=0,
            max_value=1000,
            value=300,
            step=1,
            help="Adjust the absolute temperature of the system."
        )
        
        # Fermi Energy slider linked to session state
        E_F = st.slider(
            "Fermi Energy (eV)",
            min_value=-0.50,
            max_value=0.50,
            step=0.01,
            key="ef_slider_val",
            on_change=on_slider_change,
            help="Adjust the core Energy Fermi Level relative to intrinsic state."
        )
        
    return T, E_F
