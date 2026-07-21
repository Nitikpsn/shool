import sys
from pathlib import Path

file = Path(__file__).resolve()
root = file.parents[1]

sys.path.insert(0, str(root / "backend"))

from main import app
