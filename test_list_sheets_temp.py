import tempfile, shutil, os
from spectrum.loader import list_sheets
fp = 'Oxygen NIST.xlsx'
if not os.path.exists(fp):
    print('Test file missing')
else:
    fd, tmp = tempfile.mkstemp(suffix='.xlsx')
    os.close(fd)
    shutil.copyfile(fp, tmp)
    try:
        sheets = list_sheets(tmp)
        print('Sheets:', sheets[:5])
    except Exception as e:
        print('Error during list_sheets:', e)
    finally:
        try:
            os.unlink(tmp)
            print('Temp file removed')
        except Exception as e:
            print('Error removing temp file:', e)
