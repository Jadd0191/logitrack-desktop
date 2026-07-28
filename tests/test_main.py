"""
Tests para la Fase 2 - Widgets básicos
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
    assert window.minimumSize().width() == 1200
    assert window.minimumSize().height() == 700


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


def test_save_shipment_validates_fields(window):
    """Test 5: Verifica que valida campos obligatorios"""
    window.destinatario_input.clear()
    window.direccion_input.clear()
    initial_count = window.table.rowCount()
    window._save_shipment()
    assert window.table.rowCount() == initial_count


def test_save_shipment_adds_row(window):
    """Test 6: Verifica que guardar añade una fila"""
    initial_count = window.table.rowCount()
    window.destinatario_input.setText("Test User")
    window.direccion_input.setText("Test Address")
    window._save_shipment()
    assert window.table.rowCount() == initial_count + 1


def test_clear_form_clears_fields(window):
    """Test 7: Verifica que limpiar el formulario funciona"""
    window.destinatario_input.setText("Test")
    window.direccion_input.setText("Test")
    window._clear_form()
    assert window.destinatario_input.text() == ""
    assert window.direccion_input.text() == ""