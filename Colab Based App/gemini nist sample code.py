import numpy as np
import re
from scipy.special import erf

def parse_all_nist_descriptors(intensity_str):
    """
    Parses any raw NIST intensity string to extract the numerical value
    and maps all 29 official descriptor codes into a clean boolean dictionary.
    """
    if not intensity_str or str(intensity_str).strip() == "":
        return 0.0, {}
    
    s = str(intensity_str).strip()
    
    # 1. Strip and capture numerical value
    num_match = re.search(r"[-+]?\d*\.\d+|\d+", s)
    intensity_val = float(num_match.group()) if num_match else 1.0
    
    # 2. Extract remaining characters to isolate descriptors
    desc_part = s.replace(num_match.group() if num_match else "", "").strip()
    
    # Initialize all 29 descriptors as False
    flags = {
        '*': False, ':': False, '-': False, 'a': False, 'b': False, 
        'bl': False, 'B': False, 'c': False, 'd': False, 'D': False, 
        'E': False, 'f': False, 'g': False, 'G': False, 'H': False, 
        'h': False, 'hfs': False, 'i': False, 'j': False, 'l': False, 
        'm': False, 'p': False, 'q': False, 'r': False, 's': False, 
        't': False, 'u': False, 'w': False, 'x': False
    }
    
    # Check multi-character strings first to avoid false parsing
    if 'hfs' in desc_part:
        flags['hfs'] = True
        desc_part = desc_part.replace('hfs', '')
    if 'bl' in desc_part:
        flags['bl'] = True
        desc_part = desc_part.replace('bl', '')
        
    # Check every remaining isolated character 
    for char in desc_part:
        if char in flags:
            flags[char] = True
            
    return intensity_val, flags


def evaluate_complete_nist_renderer(wave_grid, center_wl, base_intensity, flags, global_resolution=0.15):
    """
    Generates a 1D NumPy array across the wave_grid implementing 
    every active NIST relative intensity flag condition mathematically.
    """
    # Baseline line-width calculations (Standard deviation derived from FWHM)
    sigma = global_resolution / 2.35482
    intensity = base_intensity
    target_wl = center_wl
    
    # ----------------------------------------------------
    # CATEGORY 1: WAVELENGTH ACCURACY / POSITION SHIFTS (: , G , x)
    # ----------------------------------------------------
    # (i, j, m, t calculations don't change physical look; they are kept for user metadata)
    if flags['G']:
        # Roughly estimated: Inject a tiny fractional positional uncertainty fuzz
        target_wl += (sigma * 0.1) 
        
    # ----------------------------------------------------
    # CATEGORY 2: INTENSITY AMPLITUDE MODIFIERS (* , - , bl , E , f , g , m , p)
    # ----------------------------------------------------
    if flags['*']:
        intensity *= 0.5    # Intensity shared by several lines -> Divide down energy contribution
    if flags['-']:
        intensity *= 0.85   # Somewhat lower intensity than value given
    if flags['bl'] or flags['p']:
        intensity *= 1.2    # Blended/perturbed by close line -> Apparent intensity boosted by background noise
    if flags['f']:
        intensity *= 0.7    # Forbidden line -> Inherently weak probabilistic emission transition
    if flags['g']:
        intensity *= 1.3    # Transition to ground term -> Highly populated, crisp, energetic line

    # ----------------------------------------------------
    # CATEGORY 3: MATHEMATHICAL PROFILE PROFILE LOGIC GENERATOR
    # ----------------------------------------------------
    # Pre-calculate baseline profile dimensions based on broadening classes
    if flags['w']:
        sigma *= 2.2         # Wide line
    if flags['B']:
        sigma *= 4.5         # Massive autoionization broadening width
    if flags['h']:
        sigma *= 3.0         # Hazy line (diffuse)
    if flags['H']:
        sigma *= 6.0         # Very hazy line
    if flags['E']:
        sigma *= 2.5         # Broadened purely due to instrument overexposure
        intensity *= 1.4     # Saturated intensity look

    # Profile Canvas Evaluation Arrays
    profile = np.zeros_like(wave_grid)
    
    # Shape Type A: Asymmetric Distributions (b, l, s, q)
    if flags['b'] or flags['l'] or flags['s'] or flags['q']:
        # Set up skew factor directional weight (alpha)
        alpha = 0.0
        if flags['b'] or flags['l']: alpha = 4.5   # Shaded to longer wavelengths (Tail Right)
        elif flags['s']:              alpha = -4.5  # Shaded to shorter wavelengths (Tail Left)
        elif flags['q']:              alpha = 2.0   # General asymmetry
        
        # Mathematical Skew-Normal execution
        dx = (wave_grid - target_wl) / sigma
        gauss = np.exp(-0.5 * dx**2)
        cdf = 0.5 * (1.0 + erf((alpha * dx) / np.sqrt(2)))
        profile = intensity * gauss * cdf
        
    # Shape Type B: Splitting and Multiplet Arrays (d, D, hfs, u)
    elif flags['d'] or flags['D'] or flags['hfs']:
        if flags['hfs']:
            # Hyperfine structure: Render as 3 overlapping split sub-peaks
            offsets = [-0.6 * sigma, 0.0, 0.5 * sigma]
            weights = [0.3 * intensity, 0.5 * intensity, 0.2 * intensity]
            for o, w in zip(offsets, weights):
                profile += w * np.exp(-0.5 * ((wave_grid - (target_wl + o)) / (sigma * 0.6))**2)
        else:
            # Double lines / Diffuse unresolved lines: Double Peak formation
            offset = 1.1 * sigma
            p1 = (intensity * 0.5) * np.exp(-0.5 * ((wave_grid - (target_wl - offset)) / sigma)**2)
            p2 = (intensity * 0.5) * np.exp(-0.5 * ((wave_grid - (target_wl + offset)) / sigma)**2)
            profile = p1 + p2

    elif flags['u']:
        # Unresolved side shoulder bump on a stronger background line
        main = intensity * np.exp(-0.5 * ((wave_grid - target_wl) / sigma)**2)
        bump = (intensity * 0.25) * np.exp(-0.5 * ((wave_grid - (target_wl + 1.4 * sigma)) / (sigma * 0.7))**2)
        profile = main + bump

    # Shape Type C: Multi-Pronged Structures (c)
    elif flags['c']:
        # Complex line profiles: Cluster 3 unique components closely packed
        c1 = (intensity * 0.35) * np.exp(-0.5 * ((wave_grid - (target_wl - 0.5 * sigma)) / (sigma * 0.4))**2)
        c2 = (intensity * 0.45) * np.exp(-0.5 * ((wave_grid - target_wl) / (sigma * 0.3))**2)
        c3 = (intensity * 0.25) * np.exp(-0.5 * ((wave_grid - (target_wl + 0.6 * sigma)) / (sigma * 0.4))**2)
        profile = c1 + c2 + c3

    # Shape Type D: Standard Default Profile (Gaussian Distribution)
    else:
        profile = intensity * np.exp(-0.5 * ((wave_grid - target_wl) / sigma)**2)

    # ----------------------------------------------------
    # CATEGORY 4: POST-PROCESSING FILTER MODIFICATION (a , r)
    # ----------------------------------------------------
    if flags['r']:
        # Easily reversed line core calculation (Self-absorption dip)
        absorption_sigma = sigma * 0.25
        dip = (intensity * 0.9) * np.exp(-0.5 * ((wave_grid - target_wl) / absorption_sigma)**2)
        profile = np.clip(profile - dip, 0, None)
        
    if flags['a']:
        # Observed in absorption: Invert emission signal downward 
        # (Assuming renderer baseline background is black = 0, absorption makes it a negative dip)
        # Note: If drawing onto a continuous background spectrum, subtract this profile from it.
        profile = -profile 

    return profile
