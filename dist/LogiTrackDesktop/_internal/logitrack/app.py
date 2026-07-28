#!/usr/bin/env python3
"""
LogiTrack Desktop - Bootstrap e Inyección de Dependencias
Fase 8: Empaquetado y distribución
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon


def get_base_path() -> Path:
    """
    Obtiene la ruta base de la aplicación.
    Funciona tanto en desarrollo como en empaquetado.
    """
    if getattr(sys, 'frozen', False):
        # Empaquetado con PyInstaller
        return Path(sys._MEIPASS)
    else:
        # Desarrollo
        return Path(__file__).parent.parent


def get_data_path() -> Path:
    """
    Obtiene la ruta para datos persistentes.
    En empaquetado, usa la carpeta de usuario.
    """
    if getattr(sys, 'frozen', False):
        # En empaquetado, usar AppData/Local (Windows) o ~/.local (Linux)
        if sys.platform == 'win32':
            app_data = Path(os.environ.get('LOCALAPPDATA', ''))
            return app_data / 'LogiTrackDesktop' / 'data'
        elif sys.platform == 'darwin':
            return Path.home() / 'Library' / 'Application Support' / 'LogiTrackDesktop' / 'data'
        else:
            return Path.home() / '.local' / 'share' / 'logitrack' / 'data'
    else:
        # En desarrollo, usar carpeta local
        return get_base_path() / 'data'


def get_icon_path() -> Path:
    """Obtiene la ruta del icono"""
    base = get_base_path()
    icon_path = base / 'resources' / 'icon.ico'
    if icon_path.exists():
        return icon_path
    
    # Buscar también en la carpeta del ejecutable
    if getattr(sys, 'frozen', False):
        exe_dir = Path(sys.executable).parent
        icon_path = exe_dir / 'resources' / 'icon.ico'
        if icon_path.exists():
            return icon_path
    
    return None


def create_app():
    """
    Fábrica de la aplicación.
    Inyecta todas las dependencias.
    """
    from .services import ShipmentService
    from .controllers import ShipmentController
    from .views.main_window import LogiTrackWindow
    from .ui.theme import ThemeMode, apply_theme
    
    # Asegurar que existe la carpeta de datos
    data_path = get_data_path()
    data_path.mkdir(parents=True, exist_ok=True)
    
    # Crear servicio con ruta de base de datos
    db_path = data_path / 'logitrack.db'
    service = ShipmentService(str(db_path))
    
    # Crear controlador
    controller = ShipmentController(service)
    
    # Crear vista
    window = LogiTrackWindow(controller)
    
    # Configurar icono
    icon_path = get_icon_path()
    if icon_path and icon_path.exists():
        window.setWindowIcon(QIcon(str(icon_path)))
    
    return window


def main():
    """Punto de entrada principal"""
    from .ui.theme import apply_theme, ThemeMode
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Configurar icono de la aplicación
    icon_path = get_icon_path()
    if icon_path and icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Aplicar tema
    apply_theme(app, ThemeMode.LIGHT)
    
    # Crear y mostrar ventana
    window = create_app()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()