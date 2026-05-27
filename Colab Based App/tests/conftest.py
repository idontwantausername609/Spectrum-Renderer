import sys
from pathlib import Path

# Ensure the local `Colab Based App` package root is on sys.path so
# `import spectrum.colab_renderer` resolves to the bundled module here.
p = Path(__file__).resolve().parents[1]
if str(p) not in sys.path:
    sys.path.insert(0, str(p))
