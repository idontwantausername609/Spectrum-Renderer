import io
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import streamlit as st
import new_loader
import new_renderer
import utils

st.set_page_config(page_title="Visible Spectrum Renderer", layout="centered")

st.title("Visible Spectrum Rendering")
st.caption("Upload your Excel workbook and render visible spectra with NIST descriptor support")

uploaded_file = st.file_uploader("Excel File", type=["xlsx", "xls"])

available_sheets = []
if uploaded_file:
    try:
        file_bytes = uploaded_file.read()
        available_sheets = new_loader.list_sheets(file_bytes)
        uploaded_file.seek(0)
    except Exception as e:
        st.error(f"Error loading sheets: {e}")

sheet_options = ["Auto-detect (no selection)"] + available_sheets
selected_sheet = st.selectbox(
    "Sheet Name",
    options=sheet_options,
    index=0,
    help="Select a sheet to render. Multi-select is not available in Streamlit; run multiple times for different sheets."
)

col1, col2 = st.columns(2)
with col1:
    render_dark = st.checkbox("Dark Mode Image", value=True)
with col2:
    render_light = st.checkbox("Light Mode Image", value=True)

user_title = st.text_input("Spectrum Title", placeholder="e.g., Oxygen")
random_title = st.checkbox("Generate Random Title")

scale_mode = st.selectbox(
    "Scale",
    options=["raw", "normalize"],
    format_func=lambda x: "Raw - Show data as is (Default for NIST detected data)" if x == "raw" else "Normalize - Show only strong lines",
    index=0
)

show_peak_labels = st.checkbox("Show Peak Wavelength Labels", value=True)

render_button = st.button("Render Spectrum", type="primary")

if render_button and uploaded_file and (render_dark or render_light):
    if not render_dark and not render_light:
        st.warning("Please select at least one render mode")
    else:
        sheet_name = None if selected_sheet == "Auto-detect (no selection)" else selected_sheet
        
        modes_to_render = []
        if render_dark:
            modes_to_render.append("dark")
        if render_light:
            modes_to_render.append("light")
        
        for mode in modes_to_render:
            try:
                file_bytes = uploaded_file.getvalue()
                df = pd.read_excel(
                    io.BytesIO(file_bytes),
                    sheet_name=sheet_name if sheet_name is not None else 0,
                    engine='openpyxl'
                )
                
                fig = new_renderer.plot_spec(
                    df,
                    mode=mode,
                    fig_size=utils.FIG_SIZE,
                    scale_mode=scale_mode,
                    title=user_title if user_title else None,
                    random_title=random_title,
                    show_peak_labels=show_peak_labels,
                )
                
                img_bytes = io.BytesIO()
                fig.savefig(img_bytes, format='png', dpi=600, bbox_inches='tight')
                img_bytes.seek(0)
                
                mode_label = "Dark Mode" if mode == "dark" else "Light Mode"
                st.subheader(f"{selected_sheet or 'Auto-detected sheet'} — {mode_label}")
                st.image(img_bytes, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error rendering spectrum: {e}")