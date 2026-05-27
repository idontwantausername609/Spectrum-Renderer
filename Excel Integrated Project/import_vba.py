import os
import sys
from pathlib import Path

try:
    import win32com.client
except Exception as e:
    print('pywin32 is not installed in this Python environment:', e)
    sys.exit(1)

proj_root = Path.cwd()
wb_xlsx = proj_root / 'sample_workbook.xlsx'
bas_file = proj_root / 'vba' / 'RunAnnotator.bas'
wb_xlsm = proj_root / 'sample_workbook.xlsm'

if not wb_xlsx.exists():
    print('sample_workbook.xlsx not found at', wb_xlsx)
    sys.exit(1)
if not bas_file.exists():
    print('VBA module not found at', bas_file)
    sys.exit(1)

excel = win32com.client.DispatchEx('Excel.Application')
excel.Visible = False
excel.DisplayAlerts = False
try:
    wb = excel.Workbooks.Open(str(wb_xlsx))
    # Ensure VBProject is accessible
    try:
        vbproj = wb.VBProject
    except Exception as e:
        print('Could not access VBProject. Excel must allow programmatic access to VBA.\nError:', e)
        wb.Close(SaveChanges=False)
        excel.Quit()
        sys.exit(1)

    # Import .bas module (if a module with same name exists, remove it first)
    comp_name = 'RunAnnotatorModule'
    existing = None
    for comp in vbproj.VBComponents:
        if comp.Name == comp_name:
            existing = comp
            break
    if existing is not None:
        try:
            vbproj.VBComponents.Remove(existing)
            print('Removed existing VB component', comp_name)
        except Exception:
            print('Failed to remove existing VB component; will attempt to import anyway')
    try:
        vbproj.VBComponents.Import(str(bas_file))
        print('Imported', bas_file.name)
    except Exception as e:
        print('Failed to import VB module:', e)
        wb.Close(SaveChanges=False)
        excel.Quit()
        sys.exit(1)

    # Add a Form Control button to first sheet and assign macro
    sht = wb.Worksheets(1)
    # Determine placement: below existing data (approx)
    used = sht.UsedRange
    last_row = used.Row + used.Rows.Count
    left = sht.Range('A1').Left
    top = sht.Range(f'A{last_row+2}').Top
    width = 100
    height = 24
    try:
        btn = sht.Buttons().Add(left, top, width, height)
        btn.Characters().Text = 'Launch Annotator'
        # Assign the macro name in OnAction
        btn.OnAction = 'RunAnnotatorModule.RunAnnotator'
        print('Added form button and assigned macro RunAnnotatorModule.RunAnnotator')
    except Exception as e:
        print('Failed to add Form button via Buttons().Add:', e)
        print('Attempting to add a shape button instead')
        try:
            shp = sht.Shapes.AddFormControl(1, left, top, width, height)  # 1 = xlButtonControl
            shp.Name = 'LaunchAnnotatorButton'
            # OnAction for shape
            shp.OnAction = 'RunAnnotatorModule.RunAnnotator'
            print('Added FormControl shape and assigned macro')
        except Exception as e2:
            print('Failed to add shape button:', e2)

    # Save as macro-enabled workbook
    try:
        if wb_xlsm.exists():
            wb_xlsm.unlink()
        wb.SaveAs(str(wb_xlsm), FileFormat=52)  # 52 = xlOpenXMLWorkbookMacroEnabled
        print('Saved macro-enabled workbook as', wb_xlsm.name)
    except Exception as e:
        print('Failed to save as xlsm:', e)
        wb.Close(SaveChanges=False)
        excel.Quit()
        sys.exit(1)

    wb.Close(SaveChanges=False)
finally:
    excel.Quit()

print('Done')
