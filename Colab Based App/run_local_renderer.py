import sys
from pathlib import Path
from datetime import datetime

# Ensure local package dir is first on sys.path
p = Path(__file__).resolve().parent
if str(p) not in sys.path:
    sys.path.insert(0, str(p))

from colab_renderer import plot_emission_spectrum
import pandas as pd


def main():
    inp = p / 'he test.xlsx'
    if not inp.exists():
        raise SystemExit(f'Missing input workbook: {inp}')

    df = pd.read_excel(inp, sheet_name=0)

    out_dir = p / 'outputs'
    out_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')

    for mode in ('dark', 'light'):
        fig = plot_emission_spectrum(df, mode=mode)
        fname = out_dir / f'local_render_{mode}_{ts}.png'
        fig.savefig(fname, facecolor=fig.get_facecolor(), bbox_inches='tight', dpi=300)
        try:
            import matplotlib.pyplot as plt
            plt.close(fig)
        except Exception:
            pass
        print('Wrote', fname)


if __name__ == '__main__':
    main()
