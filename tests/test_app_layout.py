"""Tests for Streamlit app file existence and syntax validity."""
import py_compile
from pathlib import Path

APP_PATH = Path(__file__).resolve().parent.parent / "app.py"

def test_app_file_exists():
    assert APP_PATH.exists()

def test_app_compiles_without_syntax_errors():
    compiled = py_compile.compile(str(APP_PATH))
    assert compiled is not None
