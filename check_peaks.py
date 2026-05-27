import numpy as np
from spectrum.loader import load_spectral_data
from scipy.signal import find_peaks
sd = load_spectral_data('he test.xlsx')
input_wls = np.array(sd['wavelengths'])
input_vals = np.array(sd['intensities'])
mask = (input_wls >= 400) & (input_wls <= 750)
input_wls_f = input_wls[mask]
input_vals_f = input_vals[mask]
order = np.argsort(input_wls_f)
input_wls_f = input_wls_f[order]
input_vals_f = input_vals_f[order]
min_g = float(np.min(input_vals_f))
max_g = float(np.max(input_vals_f))
rng = max_g - min_g
for pct in [0.08,0.12]:
    dyn = pct * rng
    peaks, props = find_peaks(input_vals_f, prominence=dyn)
    print('pct',pct,'dyn',dyn,'found',len(peaks))
    if len(peaks):
        for i,p in enumerate(peaks):
            print(input_wls_f[p], input_vals_f[p], 'prom', props['prominences'][i])
