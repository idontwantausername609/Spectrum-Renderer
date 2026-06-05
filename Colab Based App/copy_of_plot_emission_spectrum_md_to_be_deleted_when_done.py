import re
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import utils

try:
    import nist_helper
except Exception:
    nist_helper = None


def parse_nist_intensity(raw_value):
    if pd.isna(raw_value):
        return (np.nan, "")
    text = str(raw_value).strip()
    match = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", text)
    if not match:
        return np.nan, text
    try:
        numeric_value = float(match.group(0))
    except Exception:
        numeric_value = np.nan
    descriptor = (text[: match.start()] + " " + text[match.end() :]).strip()
    descriptor = re.sub(r"[\s,]+", " ", descriptor)
    return numeric_value, descriptor


def prepare_generic_spectrum(df, intensity_col, apply_descriptor_adjustments):
    prepared = df.copy()
    prepared["_raw_intensity"] = pd.to_numeric(prepared[intensity_col], errors="coerce")
    prepared["_descriptor"] = ""
    prepared["_intensity_mult"] = 1.0
    prepared["_width_mult"] = 1.0
    prepared["_include"] = True
    return prepared


def _effects_from_desc(desc):
    if not desc or nist_helper is None:
        return 1.0, 1.0, True

    keys = getattr(nist_helper, "_DESCRIPTOR_KEYS_SORTED", None)
    desc_text = str(desc).lower()
    tokens = []

    if keys:
        remaining = desc_text
        for key in keys:
            if key and key in remaining:
                tokens.append(key)
                remaining = remaining.replace(key, " ")
    else:
        tokens = [tok for tok in re.split(r"[\s,]+", desc_text) if tok]

    eff = nist_helper.compute_descriptor_effects(tokens)
    return (
        eff.get("intensity_multiplier", 1.0),
        eff.get("width_multiplier", 1.0),
        eff.get("include", True),
    )


def prepare_nist_spectrum(df, intensity_col, apply_descriptor_adjustments):
    prepared = df.copy()
    parsed = prepared[intensity_col].apply(parse_nist_intensity)
    prepared["_raw_intensity"] = parsed.apply(lambda value: value[0])
    prepared["_descriptor"] = parsed.apply(lambda value: value[1])

    effs = prepared["_descriptor"].apply(_effects_from_desc)
    prepared["_intensity_mult"] = effs.apply(lambda value: value[0])
    prepared["_width_mult"] = effs.apply(lambda value: value[1])
    prepared["_include"] = effs.apply(lambda value: value[2])
    prepared = prepared[prepared["_include"]].copy()
    return prepared


def identify_spectral_peaks(df, prominence_percentage, peak_wavelengths=None):
    if df.empty:
        return []

    if peak_wavelengths is not None:
        nm_vals = df["_rounded_nm"].values if "_rounded_nm" in df.columns else df.iloc[:, 0].values
        peaks = []
        for peak_wavelength in peak_wavelengths:
            try:
                target_nm = float(peak_wavelength)
            except Exception:
                continue
            peaks.append(int(np.argmin(np.abs(nm_vals - target_nm))))
        return sorted(set(peaks))

    peak_min = float(df["_adj_intensity"].min())
    peak_max = float(df["_adj_intensity"].max())
    dynamic_prominence = prominence_percentage * max(peak_max - peak_min, 1.0)
    peaks, _ = find_peaks(df["_adj_intensity"].values, prominence=dynamic_prominence)
    return list(peaks)


def plot_emission_spectrum(
    data_df,
    nm_col=None,
    intensity_col=None,
    prominence_percentage=0.12,
    x_min=400,
    x_max=750,
    fig_size=(15, 3),
    min_brightness=0.1,
    save_path=None,
    min_needle_max_width_nm=0.1,
    max_needle_max_width_nm=0.3,
    needle_shape_power=4,
    glow_width_multiplier=1.3,
    glow_alpha=0.35,
    dpi=600,
    mode="dark",
    show_grid=False,
    peak_label_y_position=0.77,
    max_needle_y_scale=0.75,
    peak_wavelengths=None,
    force_nist=None,
    apply_descriptor_adjustments=False,
    show_peak_labels=True,
    label_min_normalized_intensity=0.20,
):
    if nm_col is None:
        nm_col = utils.resolve_column(
            data_df,
            ["nm", "wavelength", "wavelength_nm", "lambda", "lambda_nm", "wl", "wl_nm"],
            "wavelength",
        )
    if intensity_col is None:
        intensity_col = utils.resolve_column(
            data_df,
            [
                "Grey Val",
                "grey val",
                "gray val",
                "grayscale",
                "gray value",
                "intensity",
                "signal",
                "counts",
                "value",
                "int",
                "rel. int.",
                "grey",
            ],
            "intensity",
        )

    df_plot_data = data_df.copy()
    df_plot_data[nm_col] = pd.to_numeric(df_plot_data[nm_col], errors="coerce")

    sample_values = df_plot_data[intensity_col].astype(str).fillna("")
    numeric_fraction = float(pd.to_numeric(sample_values, errors="coerce").notna().mean()) if len(sample_values) else 0.0

    nist_tokens = [token.lower() for token in getattr(nist_helper, "NIST_DESCRIPTORS", [])] if nist_helper else []
    token_pattern = "|".join(re.escape(token) for token in nist_tokens if token)
    contains_nist_tokens = bool(sample_values.str.lower().str.contains(token_pattern, na=False).any()) if token_pattern else False
    contains_descriptor_chars = bool(sample_values.str.contains(r"[A-Za-z*:\(\)\[\]/%]", na=False).any())

    if force_nist is True:
        has_any_nist = True
    elif force_nist is False:
        has_any_nist = False
    else:
        has_any_nist = bool(contains_nist_tokens or (numeric_fraction < 0.6 and contains_descriptor_chars))

    if has_any_nist:
        df_plot_data = prepare_nist_spectrum(df_plot_data, intensity_col, apply_descriptor_adjustments)
    else:
        df_plot_data = prepare_generic_spectrum(df_plot_data, intensity_col, apply_descriptor_adjustments)

    df_plot_data = df_plot_data.dropna(subset=[nm_col, "_raw_intensity"]).copy()
    df_plot_data = df_plot_data[(df_plot_data[nm_col] >= x_min) & (df_plot_data[nm_col] <= x_max)].copy()
    df_plot_data = df_plot_data.sort_values(by=nm_col).reset_index(drop=True)

    if df_plot_data.empty:
        fig, ax = plt.subplots(figsize=fig_size, dpi=dpi)
        ax.set_axis_off()
        return fig

    if apply_descriptor_adjustments:
        df_plot_data["_adj_intensity"] = df_plot_data["_raw_intensity"] * df_plot_data["_intensity_mult"]
    else:
        df_plot_data["_adj_intensity"] = df_plot_data["_raw_intensity"]

    adj_min = df_plot_data["_adj_intensity"].min()
    adj_max = df_plot_data["_adj_intensity"].max()
    adj_range = adj_max - adj_min
    if adj_range == 0 or np.isnan(adj_range):
        df_plot_data["Normalized_Intensity"] = 0.0
    else:
        df_plot_data["Normalized_Intensity"] = (df_plot_data["_adj_intensity"] - adj_min) / adj_range

    if peak_wavelengths is not None:
        nm_vals = df_plot_data[nm_col].values
        peaks = []
        for peak_wavelength in peak_wavelengths:
            try:
                target_nm = float(peak_wavelength)
            except Exception:
                continue
            peaks.append(int(np.argmin(np.abs(nm_vals - target_nm))))
        peaks = sorted(set(peaks))
    else:
        peaks = identify_spectral_peaks(df_plot_data.reset_index(drop=True), prominence_percentage, peak_wavelengths=None)

    peak_nms = [float(df_plot_data.iloc[index][nm_col]) for index in peaks]
    peak_ints = [float(df_plot_data.iloc[index]["Normalized_Intensity"]) for index in peaks]
    try:
        label_ys = utils.compute_label_positions(
            peak_nms,
            intensities=peak_ints,
            base_y=peak_label_y_position,
            min_sep_nm=0.4,
            y_step=0.08,
            method="prefer_stronger_top",
            max_y=0.90,
        )
    except Exception:
        label_ys = [peak_label_y_position] * len(peaks)

    fig, ax = plt.subplots(figsize=fig_size, dpi=dpi)

    if mode == "dark":
        figure_bg_color = "black"
        text_color = "white"
        grid_color = "darkgrey"
    else:
        figure_bg_color = "white"
        text_color = "black"
        grid_color = "lightgrey"

    fig.patch.set_facecolor(figure_bg_color)
    ax.set_facecolor("black")
    ax.yaxis.set_visible(False)
    ax.set_xlabel("Wavelength (nm)", color=text_color)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(50))
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(10))
    ax.tick_params(axis="x", which="major", colors=text_color, labelsize=10)
    ax.tick_params(axis="x", which="minor", colors=text_color, length=4, width=0.5)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(0, 1)

    bg_y = np.linspace(0, max_needle_y_scale, 40)
    for _, row in df_plot_data.iterrows():
        nm_value = float(row[nm_col])
        norm_intensity = float(row.get("Normalized_Intensity", 0.0))
        base_rgb = utils.wavelength_to_rgb(nm_value)
        final_scale = min_brightness + (1 - min_brightness) * norm_intensity
        color = (base_rgb[0] * final_scale, base_rgb[1] * final_scale, base_rgb[2] * final_scale)
        width_mult = float(row.get("_width_mult", 1.0))
        bg_width = min_needle_max_width_nm * width_mult
        widths = bg_width * np.ones_like(bg_y)
        ax.fill_betweenx(
            bg_y,
            nm_value - widths / 2,
            nm_value + widths / 2,
            facecolor=color,
            alpha=0.28,
            edgecolor="none",
            linewidth=0,
            zorder=0,
        )

    for peak_position, peak_index in enumerate(peaks):
        peak_nm = float(df_plot_data.iloc[peak_index][nm_col])
        peak_normalized_intensity = float(df_plot_data.iloc[peak_index]["Normalized_Intensity"])
        base_rgb = utils.wavelength_to_rgb(peak_nm)

        peak_gamma = 0.8
        peak_emphasis = 1.4
        final_intensity_scale = min_brightness + (1 - min_brightness) * (peak_normalized_intensity ** peak_gamma)
        final_intensity_scale = min(1.0, final_intensity_scale * peak_emphasis)
        colored_rgb = (
            base_rgb[0] * final_intensity_scale,
            base_rgb[1] * final_intensity_scale,
            base_rgb[2] * final_intensity_scale,
        )

        base_width = min_needle_max_width_nm + (max_needle_max_width_nm - min_needle_max_width_nm) * peak_normalized_intensity
        width_mult = float(df_plot_data.iloc[peak_index].get("_width_mult", 1.0))
        scaled_max_width_nm = base_width * width_mult * 1.6

        y_coords_render = np.linspace(0, max_needle_y_scale, 120)
        y_coords_normalized = y_coords_render / max_needle_y_scale if max_needle_y_scale > 0 else np.zeros_like(y_coords_render)
        width_profile_factor = (4 * y_coords_normalized * (1 - y_coords_normalized)) ** needle_shape_power

        glow_widths_nm = scaled_max_width_nm * glow_width_multiplier * width_profile_factor
        ax.fill_betweenx(
            y_coords_render,
            peak_nm - glow_widths_nm / 2,
            peak_nm + glow_widths_nm / 2,
            facecolor=colored_rgb,
            alpha=glow_alpha,
            edgecolor="none",
            linewidth=0,
            antialiased=True,
            zorder=1,
        )

        needle_widths_nm = scaled_max_width_nm * width_profile_factor
        ax.fill_betweenx(
            y_coords_render,
            peak_nm - needle_widths_nm / 2,
            peak_nm + needle_widths_nm / 2,
            facecolor=colored_rgb,
            edgecolor="none",
            linewidth=0,
            antialiased=True,
            zorder=2,
        )

        if show_peak_labels and peak_normalized_intensity >= label_min_normalized_intensity:
            y_for_label = label_ys[peak_position] if peak_position < len(label_ys) else peak_label_y_position
            ax.text(
                peak_nm,
                y_for_label,
                f"{peak_nm:.2f}",
                color="white",
                ha="left",
                va="bottom",
                fontsize=6,
                rotation=60,
                rotation_mode="anchor",
                zorder=3,
                path_effects=[pe.withStroke(linewidth=1.5, foreground="black")],
            )

    plt.title(
        f"Traditional Emission Spectrum Visualization ({mode.capitalize()} Mode)",
        color=text_color,
        y=1.0,
        pad=10,
    )

    if show_grid:
        ax.grid(True, color=grid_color, linestyle=":", linewidth=0.5)

    if save_path:
        try:
            fig.savefig(save_path, facecolor=fig.get_facecolor(), bbox_inches="tight", dpi=dpi)
        except Exception:
            plt.savefig(save_path, facecolor=plt.gcf().get_facecolor(), bbox_inches="tight", dpi=dpi)

    return fig
