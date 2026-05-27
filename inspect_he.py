import numpy as np
from spectrum.loader import load_spectral_data
from spectrum.rendering import wavelength_to_rgb

sd = load_spectral_data('he test.xlsx')
print('Title:', sd.get('title'))
input_wls = np.array(sd['wavelengths'])
input_vals = np.array(sd['intensities'])
print('Loaded', input_wls.size, 'lines')
mask = (input_wls >= 400) & (input_wls <= 750)
print('In-range count:', mask.sum())
input_wls_f = input_wls[mask]
input_vals_f = input_vals[mask]
if input_vals_f.size:
    min_g = float(np.min(input_vals_f))
    max_g = float(np.max(input_vals_f))
    rng = max_g - min_g
    print('sample vals:', input_vals_f[:20])
    print('min,max,rng:', min_g, max_g, rng)
    if rng==0:
        norm_vals = np.ones_like(input_vals_f)
    else:
        norm_vals = (input_vals_f - min_g) / rng
    prom_pct = 0.08
    dyn = prom_pct * rng
    print('dyn prom', dyn)
    try:
        from scipy.signal import find_peaks
        peaks_idx, props = find_peaks(input_vals_f, prominence=dyn)
        print('peaks_idx:', peaks_idx)
    except Exception as e:
        print('scipy find_peaks failed:', e)
else:
    print('no in-range vals')
