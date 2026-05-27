import numpy as np
from spectrum.loader import load_spectral_data
sd = load_spectral_data('he test.xlsx')
input_wls = np.array(sd['wavelengths'])
input_vals = np.array(sd['intensities'])
mask = (input_wls >= 400) & (input_wls <= 750)
input_wls_f = input_wls[mask]
input_vals_f = input_vals[mask]
order = np.argsort(input_wls_f)
input_wls_f = input_wls_f[order]
input_vals_f = input_vals_f[order]
print('first 30 wavelengths:', input_wls_f[:30])
print('first 30 intensities:', input_vals_f[:30])
print('some percentiles:', np.percentile(input_vals_f, [50,75,90,95,99]))
