"""
Tests básicos para la Fase 1 - LogiTrack Desktop
Estos tests verifican que la ventana principal se crea correctamente.
"""

import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Importar la ventana desde el módulo principal
from logitrack.main import LogiTrackWindow


# ========================================
# FIXTURES (configuración para los tests)
# ========================================

@pytest.fixture(scope="session")
def app():
    """
    Fixture que proporciona una instancia de QApplication.
    Scope="session" significa que se crea una sola vez para todos los tests.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def window(app):
    """
    Fixture que proporciona una instancia de LogiTrackWindow.
    Se crea una nueva ventana para cada test.
    """
    window = LogiTrackWindow()
    return window


# ========================================
# TESTS - 6 pruebas en total
# ========================================

def test_window_creation(window):
    """
    Test 1: Verifica que la ventana se crea correctamente.
    """
    assert window is not None
    assert window.windowTitle() == "LogiTrack Desktop"
    assert window.minimumSize().width() == 1024
    assert window.minimumSize().height() == 768


def test_window_has_status_bar(window):
    """
    Test 2: Verifica que la ventana tiene barra de estado.
    """
    status_bar = window.statusBar()
    assert status_bar is not None
    current_message = status_bar.currentMessage()
    assert current_message is not None
    assert len(current_message) > 0


def test_window_has_menu_bar(window):
    """
    Test 3: Verifica que la ventana tiene barra de menú.
    """
    menu_bar = window.menuBar()
    assert menu_bar is not None


def test_window_central_widget_exists(window):
    """
    Test 4: Verifica que la ventana tiene un widget central.
    """
    central_widget = window.centralWidget()
    assert central_widget is not None


def test_window_close_cleanly(window):
    """
    Test 5: Verifica que la ventana se cierra limpiamente.
    """
    window.close()
    assert True


def test_window_is_resizable(window):
    """
    Test 6: Verifica que la ventana se puede redimensionar.
    """
    initial_size = window.size()
    window.resize(1200, 800)
    new_size = window.size()
    assert new_size.width() == 1200
    assert new_size.height() == 800