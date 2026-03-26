import streamlit as st

def render_impact_panel(temperature: int):
    """
    Renders an educational dashboard panel indicating physical implications
    of the selected temperature.
    """
    st.markdown("---")
    if temperature < 50:
        st.info("Electrons lack the thermal energy to jump states, approximating absolute zero behavior.")
    elif 250 <= temperature <= 350:
        st.info("Standard operating temperature. The distribution tails allow for normal semiconductor operation.")
    elif temperature > 400:
        st.warning("High thermal energy is causing intrinsic carriers to cross the bandgap. This can overwhelm dopants and cause standard computer chips to fail.")
