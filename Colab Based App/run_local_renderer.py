import sys
from pathlib import Path
from datetime import datetime

import pandas as pd
from colab_renderer import plot_emission_spectrum_colab_style

# Ensure local package dir is first on sys.path
p = Path(__file__).resolve().parent
if str(p) not in sys.path:
    sys.path.insert(0, str(p))

def main():
    inp = p / 'he test.xlsx'
    if not inp.exists():
        raise SystemExit(f'Missing input workbook: {inp}')

    df = pd.read_excel(inp, sheet_name=0)

    out_dir = p / 'outputs'
    out_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')

    for mode in ('dark', 'light'):
        fname = out_dir / f'local_render_{mode}_{ts}.png'
        fig = plot_emission_spectrum_colab_style(
            df,
            mode=mode,
            save_path=fname,
            fig_size=(15, 3),
            peak_label_y_position=0.8,
            max_needle_y_scale=0.8,
            show_grid=False,
            dpi=600,
            min_needle_max_width_nm=0.2,
            max_needle_max_width_nm=0.8,
            needle_shape_power=4,
            glow_width_multiplier=1.5,
            glow_alpha=0.25,
        )
    
        try:
            import matplotlib.pyplot as plt
            plt.close(fig)
        except Exception:
            pass
    
        print('Wrote', fname)


if __name__ == '__main__':
    main()
