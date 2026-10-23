import sys
sys.dont_write_bytecode=True

from pathlib import Path

def add_root(level: int = 2):
    ROOT_DIR = Path(__file__).resolve().parents[level]

    if str(ROOT_DIR) not in sys.path:
        sys.path.insert(0, str(ROOT_DIR))

    return ROOT_DIR