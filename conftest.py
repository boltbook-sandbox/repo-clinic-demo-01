"""pytest configuration — adds repo root to sys.path so 'src' is importable.

Without this, running pytest from the repo root raises:
    ModuleNotFoundError: No module named 'src'
because the repo root is not on sys.path by default in all CI environments.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
