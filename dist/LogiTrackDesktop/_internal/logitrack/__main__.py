#!/usr/bin/env python3
"""
LogiTrack Desktop - Punto de entrada
Ejecuta: python -m logitrack
"""

import sys
import os
from pathlib import Path


def setup_frozen_paths():
    """
    Configura las rutas cuando la aplicación está empaquetada con PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        # Estamos empaquetados con PyInstaller
        base_path = Path(sys._MEIPASS)
        
        # Añadir la carpeta base al path de Python
        if str(base_path) not in sys.path:
            sys.path.insert(0, str(base_path))
        
        # Añadir también la carpeta donde está el ejecutable
        exe_dir = Path(sys.executable).parent
        if str(exe_dir) not in sys.path:
            sys.path.insert(0, str(exe_dir))
        
        return base_path
    else:
        # Estamos en desarrollo
        return Path(__file__).parent.parent


def main():
    """Punto de entrada principal"""
    # Configurar rutas para empaquetado
    base_path = setup_frozen_paths()
    
    # Importar y ejecutar la aplicación
    try:
        from logitrack.app import main as app_main
        app_main()
    except ImportError as e:
        # Si falla la importación relativa, intentar con absoluta
        import importlib.util
        
        # Buscar app.py en la carpeta base
        app_path = base_path / 'logitrack' / 'app.py'
        if app_path.exists():
            spec = importlib.util.spec_from_file_location('logitrack.app', app_path)
            if spec and spec.loader:
                app_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(app_module)
                app_module.main()
        else:
            raise e


if __name__ == "__main__":
    main()