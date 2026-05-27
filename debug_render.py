from spectrum.loader import load_spectral_data
from spectrum.rendering import render_spectrum
import matplotlib.pyplot as plt

# Load the bundled test file
sd = load_spectral_data('he test.xlsx', sheet_name=None)
# Match webapp defaults
sd['keep_top_n'] = 0
fig = render_spectrum(sd, dark_mode=True, figsize=(14,4))
fig.savefig('outputs/debug_web_render.png', dpi=150, bbox_inches='tight')
plt.close(fig)
print('Wrote outputs/debug_web_render.png')
