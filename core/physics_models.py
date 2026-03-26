import numpy as np
import streamlit as st

# Boltzmann constant in eV/K
k_B = 8.617e-5

@st.cache_data
def calculate_fermi_dirac(E: np.ndarray, E_F: float, T: float) -> np.ndarray:
    """
    Highly optimized NumPy function to calculate the Fermi-Dirac probability distribution.
    
    Equation: f(E) = 1 / (e^((E - E_F)/kT) + 1)
    
    Args:
        E (np.ndarray): Energy array in electron-volts (eV). 
                        Expected shape: e.g., np.linspace(-1.0, 1.0, 1000)
        E_F (float): Fermi energy level in eV.
        T (float): Absolute temperature in Kelvin (K).
        
    Returns:
        np.ndarray: Probability distribution f(E), same shape as E.
    """
    if T == 0.0:
        # Strict error handling: Perfect step function for Absolute Zero
        prob = np.zeros_like(E, dtype=float)
        prob[E < E_F] = 1.0
        prob[E == E_F] = 0.5
        # Where E > E_F, it remains 0.0
        return prob
    
    # Valid T > 0 K case
    kT = k_B * T
    
    # Clip exponent argument to avoid OverflowError with np.exp()
    power = np.clip((E - E_F) / kT, -700, 700)
    
    f_E = 1.0 / (np.exp(power) + 1.0)
    return f_E
