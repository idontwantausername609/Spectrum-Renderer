"""
Load Excel workbooks and extract spectral line data with NIST descriptor parsing.
"""

import openpyxl
import csv
import io

def _open_workbook_from_input(input_source):
    """Opens a workbook from bytes, file-like object, or file path.
    
    Supports both XLSX (via openpyxl) and CSV (by converting to an openpyxl Workbook).
    Always returns an openpyxl.Workbook object.
    """
    file_bytes = b""

    # 1. Extract bytes from various input sources
    if isinstance(input_source, (bytes, bytearray)):
        file_bytes = input_source

    elif hasattr(input_source, 'read'):
        try:
            input_source.seek(0)
        except Exception:  # noqa: S110
            pass
        file_bytes = input_source.read()
        
    else:
        try:
            with open(input_source, 'rb') as f:
                file_bytes = f.read()
        except PermissionError as e:
            try:
                return openpyxl.load_workbook(input_source, data_only=True)
            except Exception:
                raise PermissionError(
                    f"Unable to open workbook at path '{input_source}'. "
                    "This may be because the file is locked by another application. "
                    "Try closing the file or upload it via the web interface."
                ) from e
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {input_source}")

    # 2. Handle native Excel files (checking for zip/PK magic bytes)
    if file_bytes.startswith(b'PK\x03\x04'):
        return openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
        
    # 3. Handle CSV parsing by creating an in-memory openpyxl Workbook
    try:
        # 'utf-8-sig' safely ignores or strips the BOM if present
        text_content = file_bytes.decode('utf-8-sig') 
        csv_file = io.StringIO(text_content)
        
        # Sniff delimiter (comma, semicolon, tab) automatically
        dialect = csv.Sniffer().sniff(csv_file.read(2048))
        csv_file.seek(0)
        
        # Read CSV data
        reader = csv.reader(csv_file, dialect)
        
        # Create an openpyxl Workbook to hold the CSV data
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "CSV_Data"
        
        # Stream rows directly into the Excel worksheet
        for row in reader:
            ws.append(row)
            
        return wb
        
    except Exception as e:
        raise ValueError("Unsupported or corrupted file format. Must be XLSX or CSV.") from e

def list_sheets(excel_file_path):
    wb = _open_workbook_from_input(excel_file_path)
    sheets = [ws.title for ws in wb.worksheets]
    try:
        wb.close()
    except Exception:  # noqa: S110
        pass
    return sheets
