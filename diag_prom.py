import numpy as np
from spectrum.loader import load_spectral_data
from scipy.signal import find_peaks

sd = load_spectral_data('he test.xlsx')
input_wls = np.array(sd['wavelengths'])
input_vals = np.array(sd['intensities'])
mask = (input_wls >= 400) & (input_wls <= 750)
input_vals_f = input_vals[mask]
min_g = float(np.min(input_vals_f))
max_g = float(np.max(input_vals_f))
rng = max_g - min_g
print('min,max,rng:', min_g, max_g, rng)
for pct in [0.01,0.02,0.04,0.06,0.08,0.10,0.12,0.15,0.2]:
    dyn = pct * rng
    peaks, props = find_peaks(input_vals_f, prominence=dyn)
    print(f'pct={pct:.3f} dyn={dyn:.3f} -> {len(peaks)} peaks')
# Also try normalization variant (0-1)
norm_vals = (input_vals_f - min_g) / (rng if rng!=0 else 1)
for pct in [0.01,0.02,0.04,0.06,0.08,0.10,0.12]:
    dyn2 = pct * 1.0
    peaks2, _ = find_peaks(norm_vals, prominence=dyn2)
    print(f'normalized pct={pct:.3f} dyn={dyn2:.3f} -> {len(peaks2)} peaks')
