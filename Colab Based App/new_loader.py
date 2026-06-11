"""
Load Excel workbooks and extract spectral line data with NIST descriptor parsing.
"""

import openpyxl
import io

def _open_workbook_from_input(input_source):
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

def list_sheets(excel_file_path):
    wb = _open_workbook_from_input(excel_file_path)
    sheets = [ws.title for ws in wb.worksheets]
    try:
        wb.close()
    except Exception:
        pass
    return sheets
