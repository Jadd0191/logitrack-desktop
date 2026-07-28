#!/usr/bin/env python3
"""
LogiTrack Desktop - Bootstrap e Inyección de Dependencias
Fase 6: Arquitectura MVC/MVVM
"""

import sys
from PyQt6.QtWidgets import QApplication

from .services import ShipmentService
from .controllers import ShipmentController
from .views.main_window import LogiTrackWindow
from .ui.theme import ThemeMode, apply_theme


def create_app():
    """
    Fábrica de la aplicación.
    Inyecta todas las dependencias.
    """
    # 1. Crear servicio (con inyección de dependencias)
    service = ShipmentService()
    
    # 2. Crear controlador con el servicio
    controller = ShipmentController(service)
    
    # 3. Crear vista con el controlador
    window = LogiTrackWindow(controller)
    
    return window


def main():
    """Punto de entrada principal"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Aplicar tema
    apply_theme(app, ThemeMode.LIGHT)
    
    # Crear y mostrar ventana
    window = create_app()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()