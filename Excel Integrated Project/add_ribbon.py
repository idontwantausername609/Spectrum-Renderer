import os
import sys
import zipfile
import shutil
import tempfile
from pathlib import Path

try:
    import win32com.client
except Exception as e:
    print('pywin32 missing:', e)
    sys.exit(1)

proj = Path.cwd()
wb_path = proj / 'sample_workbook.xlsm'
if not wb_path.exists():
    print('sample_workbook.xlsm not found; ensure you ran import_vba earlier')
    sys.exit(1)

bas_path = proj / 'vba' / 'ribbon_callback.bas'
if not bas_path.exists():
    print('ribbon_callback.bas not found')
    sys.exit(1)

# 1) Import the VBA module into the workbook
excel = win32com.client.DispatchEx('Excel.Application')
excel.Visible = False
excel.DisplayAlerts = False
try:
    wb = excel.Workbooks.Open(str(wb_path))
    try:
        vbproj = wb.VBProject
    except Exception as e:
        print('Cannot access VBProject. Enable Trust access to VBA project object model in Excel Trust Center.')
        wb.Close(SaveChanges=False)
        excel.Quit()
        sys.exit(1)

    comp_name = 'RibbonModule'
    existing = None
    for comp in vbproj.VBComponents:
        if comp.Name == comp_name:
            existing = comp
            break
    if existing is not None:
        try:
            vbproj.VBComponents.Remove(existing)
            print('Removed existing component', comp_name)
        except Exception:
            pass
    vbproj.VBComponents.Import(str(bas_path))
    print('Imported ribbon_callback.bas')
    wb.Save()
    wb.Close(SaveChanges=True)
finally:
    excel.Quit()

# 2) Embed customUI XML into the xlsm (zip)
custom_ui = r'''<?xml version="1.0" encoding="UTF-8"?>
<customUI xmlns="http://schemas.microsoft.com/office/2009/07/customui">
  <ribbon>
    <tabs>
      <tab id="CustomTab" label="Annotator">
        <group id="AnnotatorGroup" label="Spectrum">
          <button id="LaunchAnnotator" label="Launch Annotator" size="large" onAction="RibbonLaunch" imageMso="HappyFace"/>
        </group>
      </tab>
    </tabs>
  </ribbon>
</customUI>
'''

orig = str(wb_path)
fd, tmpname = tempfile.mkstemp(suffix='.zip')
os.close(fd)
try:
    with zipfile.ZipFile(orig, 'r') as zin:
        with zipfile.ZipFile(tmpname, 'w') as zout:
            # copy existing entries
            for item in zin.infolist():
                data = zin.read(item.filename)
                zout.writestr(item, data)
            # add customUI folder/file
            ui_path = 'customUI/customUI.xml'
            if ui_path in [i.filename for i in zin.infolist()]:
                print('customUI already present; overwriting')
            zout.writestr(ui_path, custom_ui)
    # replace original file
    shutil.move(tmpname, orig)
    print('Embedded customUI into', orig)
except Exception as e:
    if os.path.exists(tmpname):
        os.remove(tmpname)
    print('Failed to embed customUI:', e)
    sys.exit(1)

print('Ribbon added. Open sample_workbook.xlsm to see the "Annotator" tab.')
