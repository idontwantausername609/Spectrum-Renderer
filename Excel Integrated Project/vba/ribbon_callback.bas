Attribute VB_Name = "RibbonModule"
Sub RibbonLaunch(control As IRibbonControl)
    ' Ribbon callback — launch the Panel app using the current selection
    On Error GoTo use_shell
    Dim sPath As String, sEsc As String, pyCmd As String
    sPath = "C:\Users\viran\Downloads\indep. project\Graphing\Excel Integrated Project\sample_workbook.xlsm;C:\Users\viran\Downloads\indep. project\Graphing\Excel Integrated Project\.venv\Lib\site-packages\xlwings\addin\xlwings.xlam"
    sEsc = Replace(sPath, "\", "\\")
    pyCmd = "import xlwings as xw; xw.utils.prepare_sys_path('true;" & sEsc & ";;;;'); import annotator; annotator.launch_with_selection()"
    Application.Run "RunPython", pyCmd
    Exit Sub
use_shell:
    Err.Clear
    Dim py As String, cmd As String
    py = "C:\Users\viran\Downloads\indep. project\Graphing\Excel Integrated Project\.venv\Scripts\python.exe"
    cmd = Chr(34) & py & Chr(34) & " -c " & Chr(34) & "import annotator; annotator.launch_with_selection()" & Chr(34)
    Shell cmd, vbNormalFocus
End Sub
