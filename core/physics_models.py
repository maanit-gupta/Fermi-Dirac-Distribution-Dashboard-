import numpy as np
import streamlit as st

# Physical Constants
k_B = 8.617e-5      # Boltzmann constant in eV/K
q = 1.602e-19       # Elementary charge in C
eps_0 = 8.854e-14   # Vacuum permittivity in F/cm
eps_s = 11.7 * eps_0 # Si permittivity in F/cm
E_g = 1.12          # Si Bandgap in eV

@st.cache_data
def calculate_fermi_dirac(E: np.ndarray, E_F: float, T: float) -> np.ndarray:
    """
    Highly optimized NumPy function to calculate the Fermi-Dirac probability distribution.
    
    Equation: f(E) = 1 / (e^((E - E_F)/kT) + 1)
    
    Args:
        E (np.ndarray): Energy array in electron-volts (eV). 
        E_F (float): Fermi energy level in eV.
        T (float): Absolute temperature in Kelvin (K).
        
    Returns:
        np.ndarray: Probability distribution f(E).
    """
    if T == 0.0:
        prob = np.zeros_like(E, dtype=float)
        prob[E < E_F] = 1.0
        prob[E == E_F] = 0.5
        return prob
    
    kT = k_B * T
    power = np.clip((E - E_F) / kT, -700, 700)
    f_E = 1.0 / (np.exp(power) + 1.0)
    return f_E

@st.cache_data
def calculate_pn_junction(N_A: float, N_D: float, T: float, x_array: np.ndarray):
    """
    Computes PN Junction parameters and energy bands.
    Args:
        N_A: Acceptor concentration (cm^-3)
        N_D: Donor concentration (cm^-3)
        T: Temperature (K)
        x_array: Position array in um to evaluate bands
        
    Returns:
        dict with keys: n_i, V_bi, x_p, x_n, E_c, E_v, E_i
    """
    # 1. Intrinsic Carrier Concentration for Si
    n_i_300 = 1e10
    if T > 0:
        n_i = n_i_300 * ((T / 300.0) ** 1.5) * np.exp(-(E_g / (2 * k_B)) * (1.0 / T - 1.0 / 300.0))
    else:
        n_i = 1e-20 # prevent div by zero
        
    n_i = max(n_i, 1e-20) # ensure strictly positive
    
    # 2. Built-in Potential V_bi
    V_bi = (k_B * T) * np.log((N_A * N_D) / (n_i**2))
    
    # 3. Depletion Widths
    coef = 2.0 * eps_s * V_bi / q
    x_n_cm = np.sqrt(coef * (N_A / (N_D * (N_A + N_D))))
    x_p_cm = np.sqrt(coef * (N_D / (N_A * (N_A + N_D))))
    
    x_n = x_n_cm * 1e4 # convert to um
    x_p = x_p_cm * 1e4 # convert to um
    
    # 4. Energy Bands
    E_i_p = k_B * T * np.log(N_A / n_i)
    E_i_n = - k_B * T * np.log(N_D / n_i)
    
    V_p = V_bi * (N_D / (N_A + N_D))
    V_n = V_bi * (N_A / (N_A + N_D))
    
    E_i = np.zeros_like(x_array)
    
    mask_p = x_array <= -x_p
    mask_n = x_array >= x_n
    mask_dep_p = (x_array > -x_p) & (x_array < 0)
    mask_dep_n = (x_array >= 0) & (x_array < x_n)
    
    E_i[mask_p] = E_i_p
    E_i[mask_n] = E_i_n
    
    # Parabolic blending in depletion region
    if x_p > 0:
        E_i[mask_dep_p] = E_i_p - V_p * ((x_array[mask_dep_p] + x_p) / x_p)**2
    if x_n > 0:
        E_i[mask_dep_n] = E_i_p - V_p - V_n * (1.0 - ((x_n - x_array[mask_dep_n]) / x_n)**2)
        
    E_c = E_i + E_g / 2.0
    E_v = E_i - E_g / 2.0
    
    return {
        "n_i": n_i,
        "V_bi": V_bi,
        "x_p": x_p,
        "x_n": x_n,
        "E_c": E_c,
        "E_v": E_v,
        "E_i": E_i
    }
