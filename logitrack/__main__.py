#!/usr/bin/env python3
"""
LogiTrack Desktop - Punto de entrada
Permite ejecutar: python -m logitrack
"""

import sys
from PyQt6.QtWidgets import QApplication
from .main import LogiTrackWindow


def main():
    """Punto de entrada principal"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = LogiTrackWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()