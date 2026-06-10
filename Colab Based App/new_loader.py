"""
Load Excel workbooks and extract spectral line data with NIST descriptor parsing.
"""

import numpy as np
import openpyxl
import os
import io
from collections import Counter
import temp_utils
import nist_codes


def find_spectral_sheet(workbook):

    wavelength_tokens = temp_utils.lambda_tokens
    intensity_tokens = temp_utils.int_tokens
    title_tokens = ('spectrum', 'element', 'species', 'ion', 'atom', 'source')
    
    for sheet in workbook.worksheets:
        for header_row in range(1, min(sheet.max_row, 10) + 1):
            headers = [temp_utils.normalize_header(cell.value) for cell in sheet[header_row]]
            wavelength_col = next((i for i, header in enumerate(headers) if any(token in header for token in wavelength_tokens)), None)
            intensity_col = next((i for i, header in enumerate(headers) if any(token in header for token in intensity_tokens)), None)
            
            if wavelength_col is None or intensity_col is None:
                continue
            
            title_col = next((i for i, header in enumerate(headers) if any(token in header for token in title_tokens)), None)
            return sheet, header_row, wavelength_col, intensity_col, title_col
    
    return None, None, None, None, None


def _open_workbook_from_input(input_source):
    """Open an openpyxl Workbook from a path, bytes, or file-like object.

    Returns: openpyxl.Workbook
    """
    # Bytes passed directly (e.g., from web upload)
    if isinstance(input_source, (bytes, bytearray)):
        return openpyxl.load_workbook(io.BytesIO(input_source), data_only=True)

    # File-like object (has .read()); ensure position at start then load
    if hasattr(input_source, 'read'):
        try:
            input_source.seek(0)
        except Exception:
            pass
        return openpyxl.load_workbook(input_source, data_only=True)

    # Assume a filesystem path (string). Try to read bytes first to avoid
    # letting openpyxl open the file path directly (this helps with Windows locks).
    try:
        with open(input_source, 'rb') as f:
            data = f.read()
        return openpyxl.load_workbook(io.BytesIO(data), data_only=True)
    except PermissionError:
        # If reading bytes fails due to permission/locking, fall back to
        # openpyxl attempting to open the path (will likely raise same error).
        # Raise a clearer exception so callers can warn the user.
        try:
            return openpyxl.load_workbook(input_source, data_only=True)
        except Exception as e:
            raise PermissionError(
                f"Unable to open workbook at path '{input_source}'. "
                "This may be because the file is locked by another application "
                "(e.g., Excel). Try closing the file in Excel or upload the file "
                "via the web interface so it is read as bytes.") from e
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {input_source}")


def load_spectral_data(excel_file_path, sheet_name=None, user_title=None):
    """
    Load spectral data from an Excel file.
    
    High-level function: given a file path, returns structured spectral data
    ready for rendering.
    
    Args:
        excel_file_path (str): Path to Excel workbook
        sheet_name (str, optional): Sheet to load; if None, uses first valid
        user_title (str, optional): User-provided spectrum title; if blank or None,
                                     infers from workbook or generates random code
    
    Returns:
        dict: {
            'wavelengths': np.array,      # Parsed wavelengths in nm
            'intensities': np.array,      # Corrected intensities (numeric × multiplier)
            'width_factors': np.array,    # Width multipliers per line
            'actions': list[str],         # Visual actions per line ('line', 'broad', etc.)
            'confidences': list[str],     # Confidence levels per line
            'title': str,                 # Final spectrum title
            'sheet_name': str,            # Name of loaded sheet
            'diagnostics': dict           # Parser diagnostics (raw counts, unknown tokens, etc.)
        }
    
    Raises:
        ValueError: If no valid sheet or spectral rows found
    """
    
    wb = _open_workbook_from_input(excel_file_path)
    
    if sheet_name:
        ws = wb[sheet_name]
        header_row = None
        wavelength_col = None
        intensity_col = None
        title_col = None
        
        # Scan this sheet for columns
        for row_idx in range(1, min(ws.max_row, 10) + 1):
            headers = [temp_utils.normalize_header(cell.value) for cell in ws[row_idx]]
            wavelength_tokens = temp_utils.lambda_tokens
            intensity_tokens = temp_utils.int_tokens
            title_tokens = ('spectrum', 'element', 'species', 'ion', 'atom', 'source')
            
            wavelength_col = next((i for i, header in enumerate(headers) if any(token in header for token in wavelength_tokens)), None)
            intensity_col = next((i for i, header in enumerate(headers) if any(token in header for token in intensity_tokens)), None)
            
            if wavelength_col is not None and intensity_col is not None:
                header_row = row_idx
                title_col = next((i for i, header in enumerate(headers) if any(token in header for token in title_tokens)), None)
                break
        
        if header_row is None:
            raise ValueError(f'No wavelength and intensity columns found in sheet {sheet_name}')
    else:
        ws, header_row, wavelength_col, intensity_col, title_col = find_spectral_sheet(wb)
        if ws is None:
            wb.close()
            raise ValueError('No sheet with wavelength and intensity columns found')
    
    # Parse spectral rows
    wavelengths = []
    intensities = []
    width_factors = []
    actions_list = []
    confidences = []
    title_candidates = []
    
    raw_descriptor_counts = Counter()
    parsed_descriptor_counts = Counter()
    unknown_descriptor_counts = Counter()
    skipped_masked_lines = 0
    
    for row in ws.iter_rows(min_row=header_row + 1, values_only=True):
        if row is None:
            continue
        if wavelength_col >= len(row) or intensity_col >= len(row):
            continue

        wavelength_value = row[wavelength_col]
        intensity_value = row[intensity_col]
        if wavelength_value is None or intensity_value is None:
            continue

        try:
            wl = float(wavelength_value)
        except (ValueError, TypeError):
            continue

        numeric_intensity, raw_descriptor, tokens, intensity_multiplier, width_multiplier, confidence, actions, unknown_tokens = nist_codes.parse_nist_intensity(intensity_value)
        
        if numeric_intensity is None:
            continue

        if raw_descriptor:
            raw_descriptor_counts[raw_descriptor] += 1
        for token in tokens:
            parsed_descriptor_counts[token] += 1
        for token in unknown_tokens:
            unknown_descriptor_counts[token] += 1

        # Skip masked lines (`m`)
        if 'm' in tokens:
            skipped_masked_lines += 1
            continue

        corrected_intensity = numeric_intensity * intensity_multiplier

        wavelengths.append(wl)
        intensities.append(corrected_intensity)
        width_factors.append(width_multiplier)
        confidences.append(confidence)
        actions_list.append('+'.join(actions) if actions else 'line')

        if title_col is not None and title_col < len(row) and row[title_col] is not None:
            candidate = temp_utils.clean_title(row[title_col])
            if candidate:
                title_candidates.append(candidate)
        elif title_col is None:
            for value in row:
                if value is None or temp_utils.looks_like_number(value):
                    continue
                candidate = temp_utils.clean_title(value)
                if candidate:
                    title_candidates.append(candidate)
                    break

    if not wavelengths:
        wb.close()
        raise ValueError(f'No spectral rows found in sheet {ws.title}')

    # Resolve spectrum title
    if user_title and str(user_title).strip():
        spectrum_title = str(user_title).strip()
    else:
        sheet_title = temp_utils.clean_title(ws.title)
        is_generic = ws.title.strip().lower().startswith('sheet')
        if sheet_title and not is_generic:
            spectrum_title = sheet_title
        elif title_candidates:
            spectrum_title = title_candidates[0]
        else:
            spectrum_title = None

    result = {
        'wavelengths': np.array(wavelengths),
        'intensities': np.array(intensities, dtype=float),
        'width_factors': np.array(width_factors, dtype=float),
        'actions': actions_list,
        'confidences': confidences,
        'title': spectrum_title,
        'sheet_name': ws.title,
        'diagnostics': {
            'raw_descriptors': dict(raw_descriptor_counts),
            'parsed_tokens': dict(parsed_descriptor_counts),
            'unknown_tokens': dict(unknown_descriptor_counts),
            'skipped_masked': skipped_masked_lines,
            'total_lines': len(wavelengths)
        }
    }
    # Close workbook to release file handles on Windows
    try:
        wb.close()
    except Exception:
        pass

    return result


def list_sheets(excel_file_path):
    """
    List all sheet names in an Excel file.
    
    Args:
        excel_file_path (str): Path to Excel workbook
    
    Returns:
        list[str]: Sheet names
    """
    wb = _open_workbook_from_input(excel_file_path)
    sheets = [ws.title for ws in wb.worksheets]
    try:
        wb.close()
    except Exception:
        pass
    return sheets
