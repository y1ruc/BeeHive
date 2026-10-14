"""
BeeHive GUI launcher.

This file lives at the project root so you can start the GUI with:
    python gui.py
"""

import sys
import os

# Ensure project root is on path.
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from gui.app import main

if __name__ == "__main__":
    main()
