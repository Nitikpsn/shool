import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

PYTHON_DEPS_DIR = ROOT_DIR / "python"
if PYTHON_DEPS_DIR.exists() and str(PYTHON_DEPS_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DEPS_DIR))

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.main import app
