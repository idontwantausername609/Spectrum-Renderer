import pandas as pd
from spectrum.colab_renderer import plot_emission_spectrum_colab_style


def test_renderer_runs():
    # tiny synthetic dataset
    df = pd.DataFrame({
        'nm': [450, 500, 550, 589, 650],
        'Grey Val': [100, 150, 120, 200, 90]
    })
    fig, peaks_df = plot_emission_spectrum_colab_style(df)
    assert hasattr(fig, 'savefig')
    assert isinstance(peaks_df, pd.DataFrame)
