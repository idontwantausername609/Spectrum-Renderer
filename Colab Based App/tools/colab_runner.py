import argparse
import os
from pathlib import Path
from datetime import datetime
import pandas as pd

from spectrum.colab_renderer import plot_emission_spectrum_colab_style


def load_input(path: Path) -> pd.DataFrame:
    lower = path.suffix.lower()
    if lower in ('.xlsx', '.xls'):
        return pd.read_excel(path, sheet_name=0)
    else:
        return pd.read_csv(path)


def save_outputs(fig, peaks_df: pd.DataFrame, out_prefix: str, mode_tag: str, dpi: int, out_dir: Path, formats):
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    out_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    for fmt in formats:
        out_png = out_dir / f"{out_prefix}_{mode_tag}_{ts}.{fmt}"
        fig.savefig(out_png, facecolor=fig.get_facecolor(), bbox_inches='tight', dpi=dpi)
        results[f'image_{fmt}'] = str(out_png)
    out_csv = out_dir / f"{out_prefix}_peaks_{mode_tag}_{ts}.csv"
    peaks_df.to_csv(out_csv, index=False)
    results['csv'] = str(out_csv)
    return results


def main():
    p = argparse.ArgumentParser(description='Run Colab-style renderer on a data file')
    p.add_argument('--input', '-i', required=True, help='Input CSV or Excel file')
    p.add_argument('--out-prefix', default='emulate_colab', help='Output filename prefix')
    p.add_argument('--dpi', type=int, default=300)
    p.add_argument('--out-dir', default='outputs')
    p.add_argument('--formats', default='png', help='Comma-separated image formats (png, svg, pdf)')
    args = p.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        raise SystemExit(f'Input file not found: {inp}')

    df = load_input(inp)

    formats = [s.strip() for s in args.formats.split(',') if s.strip()]
    out_dir = Path(args.out_dir)

    for dark in (True, False):
        fig, peaks_df = plot_emission_spectrum_colab_style(
            df,
            dark_mode=dark,
            dpi=args.dpi
        )
        mode_tag = 'dark' if dark else 'light'
        res = save_outputs(fig, peaks_df, args.out_prefix, mode_tag, args.dpi, out_dir, formats)
        print('Wrote:', res)
        # close fig to free memory
        try:
            import matplotlib.pyplot as plt
            plt.close(fig)
        except Exception:
            pass


if __name__ == '__main__':
    main()
