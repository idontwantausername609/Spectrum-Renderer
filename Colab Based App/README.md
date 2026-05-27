# Colab Based App

Standalone Colab-style emission spectrum renderer extracted from the working notebook.

Usage (from project root):

```
python "Colab Based App/tools/colab_runner.py" --input "path/to/he test.xlsx" --out-prefix emulate_colab
```

This will write dark and light PNG(s) and CSVs into the `outputs/` folder with timestamped filenames.

Design decisions:
- `spectrum/colab_renderer.py` contains the pure rendering function (no file I/O).
- `tools/colab_runner.py` handles file loading and saving.
