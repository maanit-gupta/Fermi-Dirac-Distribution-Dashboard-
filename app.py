import streamlit as st
import numpy as np
import plotly.graph_objects as go

from components.controls import render_controls
from core.physics_models import calculate_fermi_dirac
from components.dashboard import render_impact_panel

# Cache the Plotly figure rendering for zero-latency fluidity
@st.cache_data
def create_plotly_figure(E: np.ndarray, f_E: np.ndarray, E_F: float, T: float):
    """
    Creates a Desmos-style plot for the Fermi-Dirac distribution.
    Requires pure white background, subtle gray grids, and a thick vibrant blue line.
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=E, y=f_E,
        mode='lines',
        name='f(E)',
        line=dict(color='#0066ff', width=5) # Thick, vibrant blue
    ))
    
    fig.update_layout(
        plot_bgcolor='white',        # Desmos clean background
        paper_bgcolor='white',
        font=dict(family='sans-serif', size=14, color="#333"),
        xaxis=dict(
            title="Energy (eV)",
            showgrid=True,
            gridcolor='#e8e8e8',     # Subtle light gray gridlines
            zeroline=True,
            zerolinecolor='#cccccc', # Prominent but clean zero-line
            zerolinewidth=2
        ),
        yaxis=dict(
            title="Probability f(E)",
            showgrid=True,
            gridcolor='#e8e8e8',
            zeroline=True,
            zerolinecolor='#cccccc',
            zerolinewidth=2,
            range=[-0.05, 1.05]      # Slight padding to view edges clearly
        ),
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    fig.update_xaxes(title_font=dict(color="black", size=14), tickfont=dict(color="black"))
    fig.update_yaxes(title_font=dict(color="black", size=14), tickfont=dict(color="black"))
    
    fig.add_hline(y=0.5, line_dash="dash", line_color="gray")
    fig.add_vline(x=E_F, line_dash="dash", line_color="gray")
    
    return fig

def main():
    # Set wide layout as requested
    st.set_page_config(page_title="Fermi-Dirac Visualizer", layout="wide")
    
    # Sleek light-gray sidebar, pure white main canvas CSS
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            background-color: #f7f9fa; /* Sleek light gray */
        }
        [data-testid="stAppViewContainer"] .main {
            background-color: #ffffff;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Render Controls from Sidebar
    T, E_F = render_controls()
    
    with st.sidebar:
        render_impact_panel(T)
    
    st.markdown("<h2 style='text-align: center; color: #333;'>Fermi-Dirac Distribution</h2>", unsafe_allow_html=True)
    
    # Fixed energy domain parameter requirements
    E = np.linspace(-1.0, 1.0, 1000)
    
    # Execute Cached Math Engine
    # Any lag is circumvented by st.cache_data decorating the mathematical step
    f_E = calculate_fermi_dirac(E, E_F, T)
    
    # Generate Cached Plotly Visualization Look
    fig = create_plotly_figure(E, f_E, E_F, T)
    
    # Render the graph in 'massive' full-width container
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
if __name__ == "__main__":
    main()
