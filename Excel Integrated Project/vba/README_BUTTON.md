How to add the 'Launch Annotator' button to the sample workbook

1. Open `sample_workbook.xlsx` in Excel.
2. Install the xlwings add-in if you haven't already:

   ```powershell
   xlwings addin install
   ```

3. Open the VBA editor (Alt+F11).
4. In the VBA editor, choose File → Import File... and select `vba/RunAnnotator.bas` from this project folder.
5. Back in Excel, go to the Developer tab → Insert → Form Controls → Button (Form Control). Draw the button on the sheet.
6. When prompted to assign a macro, pick `RunAnnotatorModule.RunAnnotator` and click OK.
7. Save the workbook as a macro-enabled workbook (`File` → `Save As` → choose `Excel Macro-Enabled Workbook (*.xlsm)`).

Now, select the two columns of your data (wavelength, intensity) in the workbook, and click the button — it will export the selection and launch the interactive Panel UI (ensure the project's `.venv` is set up and has dependencies installed).

If you prefer the button to always use the entire sheet, modify the `RunAnnotator` macro to call `RunPython("import annotator; annotator.launch_panel()")` instead.
