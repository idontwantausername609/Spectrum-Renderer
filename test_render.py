from spectrum.rendering import render_spectrum

spectral_data = {
    'title': 'Test Render',
    'wavelengths': [486.1, 656.3, 589.0],
    'intensities': [1.0, 0.8, 0.9],
    'width_factors': [1.0, 1.0, 1.0],
    'actions': ['', '', '']
}

fig = render_spectrum(spectral_data, dark_mode=True)
fig.savefig('outputs/test_render.png')
print('Saved outputs/test_render.png')
