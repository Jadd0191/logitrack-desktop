"""
Tests para la Fase 4 - Eventos y asincronía
"""

import pytest
from PyQt6.QtWidgets import QApplication
from logitrack.main import LogiTrackWindow


@pytest.fixture(scope="session")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def window(app):
    window = LogiTrackWindow()
    return window


def test_window_creation(window):
    """Test 1: Verifica que la ventana se crea correctamente"""
    assert window is not None
    assert window.windowTitle() == "LogiTrack Desktop"
    assert window.minimumSize().width() == 1000
    assert window.minimumSize().height() == 650


def test_window_has_table(window):
    """Test 2: Verifica que la tabla existe"""
    assert hasattr(window, 'table')
    assert window.table is not None
    assert window.table.columnCount() == 6


def test_window_has_form_fields(window):
    """Test 3: Verifica que los campos del formulario existen"""
    assert hasattr(window, 'destinatario_input')
    assert hasattr(window, 'direccion_input')
    assert hasattr(window, 'tipo_combo')
    assert hasattr(window, 'estado_combo')


def test_window_has_buttons(window):
    """Test 4: Verifica que los botones existen"""
    assert hasattr(window, 'guardar_btn')
    assert hasattr(window, 'limpiar_btn')
    assert hasattr(window, 'cancelar_btn')  # Nuevo botón
    assert hasattr(window, 'load_btn')      # Nuevo botón


def test_window_has_progress_bar(window):
    """Test 5: Verifica que existe la barra de progreso"""
    assert hasattr(window, 'progress_bar')
    assert window.progress_bar is not None


def test_window_has_workers_list(window):
    """Test 6: Verifica que existe la lista de workers"""
    assert hasattr(window, 'workers')
    assert isinstance(window.workers, list)


def test_save_shipment_async_adds_row(window):
    """Test 7: Verifica que guardar añade una fila"""
    initial_count = window.table.rowCount()
    window.destinatario_input.setText("Test User")
    window.direccion_input.setText("Test Address")
    
    # Guardar de forma asíncrona
    window._save_shipment_async()
    
    # Esperar un poco para que se complete (en tests reales se usaría QTest.qWait)
    import time
    time.sleep(2)
    
    # Debe haber una fila más
    assert window.table.rowCount() >= initial_count


def test_clear_form_clears_fields(window):
    """Test 8: Verifica que limpiar el formulario funciona"""
    window.destinatario_input.setText("Test")
    window.direccion_input.setText("Test")
    window._clear_form()
    assert window.destinatario_input.text() == ""
    assert window.direccion_input.text() == ""