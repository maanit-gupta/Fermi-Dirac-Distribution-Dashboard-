import streamlit as st
import numpy as np
import plotly.graph_objects as go

from components.controls import render_controls
from core.physics_models import calculate_fermi_dirac, calculate_pn_junction
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

@st.cache_data
def create_pn_figure(x: np.ndarray, res: dict):
    fig = go.Figure()
    
    # Fermi Level (0 eV)
    fig.add_trace(go.Scatter(
        x=x, y=np.zeros_like(x), mode='lines', name='Fermi Level (E_F)',
        line=dict(color='gray', width=2, dash='dash')
    ))
    
    # Conduction Band
    fig.add_trace(go.Scatter(
        x=x, y=res["E_c"], mode='lines', name='Conduction Band (E_C)',
        line=dict(color='#d62728', width=3) 
    ))
    
    # Intrinsic Level
    fig.add_trace(go.Scatter(
        x=x, y=res["E_i"], mode='lines', name='Intrinsic Level (E_i)',
        line=dict(color='#2ca02c', width=2, dash='dot') 
    ))

    # Valence Band
    fig.add_trace(go.Scatter(
        x=x, y=res["E_v"], mode='lines', name='Valence Band (E_V)',
        line=dict(color='#1f77b4', width=3) 
    ))
    
    # Depletion region boundaries
    fig.add_vline(x=-res["x_p"], line_dash="dash", line_color="rgba(0,0,0,0.15)", annotation_text="-xp", annotation_position="top left")
    fig.add_vline(x=res["x_n"], line_dash="dash", line_color="rgba(0,0,0,0.15)", annotation_text="xn", annotation_position="top right")
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='sans-serif', size=14, color="#333"),
        xaxis=dict(
            title="Position x (μm)",
            showgrid=True,
            gridcolor='#e8e8e8',
            zeroline=True,
            zerolinecolor='#cccccc',
            zerolinewidth=2
        ),
        yaxis=dict(
            title="Energy (eV)",
            showgrid=True,
            gridcolor='#e8e8e8',
            zeroline=False
        ),
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
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
    
    # Top-level navigation mimicking tabs
    active_tab = st.radio(
        "Select View",
        ["Fermi-Dirac Distribution", "PN Junction Band Diagram"],
        horizontal=True,
        label_visibility="collapsed"
    )

    # Render Controls from Sidebar
    controls = render_controls(active_tab)
    
    with st.sidebar:
        if active_tab == "Fermi-Dirac Distribution":
            render_impact_panel(controls["T"])
    
    if active_tab == "Fermi-Dirac Distribution":
        st.markdown("<h2 style='text-align: center; color: #333;'>Fermi-Dirac Distribution</h2>", unsafe_allow_html=True)
        
        T, E_F = controls["T"], controls["E_F"]
        
        # Fixed energy domain parameter requirements
        E = np.linspace(-1.0, 1.0, 1000)
        
        # Execute Cached Math Engine
        # Any lag is circumvented by st.cache_data decorating the mathematical step
        f_E = calculate_fermi_dirac(E, E_F, T)
        
        # Generate Cached Plotly Visualization Look
        fig = create_plotly_figure(E, f_E, E_F, T)
        
        # Render the graph in 'massive' full-width container
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.latex(r"f(E) = \frac{1}{1 + e^{\frac{E - E_F}{kT}}}")
        st.caption("$f(E)$ is the probability of an electron occupying state $E$, $E_F$ is the Fermi energy, $k$ is the Boltzmann constant, and $T$ is the absolute temperature.")
        
    else:
        st.markdown("<h2 style='text-align: center; color: #333;'>PN Junction Band Diagram</h2>", unsafe_allow_html=True)
        
        N_A = controls["N_A"]
        N_D = controls["N_D"]
        T = controls["T"]
        
        # Obtain rough depletion widths temporarily to set appropriate plotting bounds
        res_temp = calculate_pn_junction(N_A, N_D, T, np.array([0.0]))
        x_p, x_n = res_temp["x_p"], res_temp["x_n"]
        total_W = x_p + x_n
        
        # Create positional array centered around the junction 
        x_min = -x_p - 1.5 * total_W
        x_max = x_n + 1.5 * total_W
        
        # Fallback if the width is unreasonably small
        if x_max - x_min < 0.1:
            x_min, x_max = -0.1, 0.1
            
        x_array = np.linspace(x_min, x_max, 1000)
        
        # Perform accurate calculation across spatial dimension
        res = calculate_pn_junction(N_A, N_D, T, x_array)
        
        st.metric("Built-in Potential ($V_{bi}$)", f"{res['V_bi']:.2f} V")
        
        fig = create_pn_figure(x_array, res)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.latex(r"V_{bi} = \frac{kT}{q} \ln\left(\frac{N_A N_D}{n_i^2}\right)")
        st.caption("The P-type region (acceptors) is shown on the negative x-axis, and the N-type region (donors) on the positive x-axis. As doping increases, the built-in potential difference rises causing larger band bending in the depletion zone.")
    
if __name__ == "__main__":
    main()
