#!/usr/bin/env python3
"""
LogiTrack Desktop - Componentes Visuales Personalizados
Fase 5: Componentes visuales avanzados y personalización de estilos
"""

from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor

from .theme import get_theme, ThemeColors


class StatusBadge(QWidget):
    """
    Badge visual para mostrar el estado de un envío.
    Hereda de QWidget para permitir personalización completa.
    """

    def __init__(self, status: str = "Pendiente", parent=None):
        super().__init__(parent)
        self._status = status
        self._setup_ui()

    def _setup_ui(self):
        """Configura la interfaz del badge"""
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        # Círculo de color
        self.color_indicator = QLabel()
        self.color_indicator.setFixedSize(12, 12)
        self.color_indicator.setStyleSheet("border-radius: 6px;")
        layout.addWidget(self.color_indicator)

        # Texto del estado
        self.text_label = QLabel(self._status)
        self.text_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        layout.addWidget(self.text_label)

        self.setLayout(layout)
        self._update_style()

    def _update_style(self):
        """Actualiza el estilo según el estado"""
        theme = get_theme()
        status_colors = {
            "Entregado": (theme.success, theme.success_light),
            "En ruta": (theme.warning, theme.warning_light),
            "Pendiente": (theme.info, theme.info_light),
            "Retrasado": (theme.danger, theme.danger_light),
        }

        color, bg_color = status_colors.get(self._status, (theme.text_secondary, theme.background_secondary))

        # Actualizar círculo
        self.color_indicator.setStyleSheet(f"""
            background-color: {color};
            border-radius: 6px;
        """)

        # Actualizar texto
        self.text_label.setStyleSheet(f"""
            color: {color};
            font-weight: bold;
            font-size: 11px;
        """)

        # Fondo del badge
        self.setStyleSheet(f"""
            StatusBadge {{
                background-color: {bg_color};
                border-radius: 12px;
            }}
        """)

    def set_status(self, status: str):
        """Cambia el estado del badge"""
        self._status = status
        self.text_label.setText(status)
        self._update_style()

    def get_status(self) -> str:
        """Obtiene el estado actual"""
        return self._status


class KPICard(QWidget):
    """
    Tarjeta KPI para mostrar métricas clave.
    """

    def __init__(self, title: str, value: str, icon: str = "📊", color: str = None, parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color
        self._setup_ui()

    def _setup_ui(self):
        """Configura la interfaz de la tarjeta KPI"""
        theme = get_theme()

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)

        # Fila superior: icono + título
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        # Icono
        icon_label = QLabel(self.icon)
        icon_label.setStyleSheet(f"font-size: 20px;")
        header_layout.addWidget(icon_label)

        # Título
        title_label = QLabel(self.title)
        title_label.setStyleSheet("""
            font-size: 12px;
            color: #6c757d;
            font-weight: 500;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Valor (grande)
        value_label = QLabel(self.value)
        value_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {self.color if self.color else theme.text};
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)

        self.setLayout(layout)

        # Estilo de la tarjeta
        self.setStyleSheet(f"""
            KPICard {{
                background-color: {theme.card_background};
                border: 1px solid {theme.border};
                border-radius: 8px;
            }}
        """)
        self.setFixedHeight(100)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def update_value(self, value: str):
        """Actualiza el valor mostrado"""
        # Buscar el label del valor
        for child in self.children():
            if isinstance(child, QLabel) and child.styleSheet().find("font-size: 28px") != -1:
                child.setText(value)
                break


class FilterBar(QWidget):
    """
    Barra de filtros para la tabla de envíos.
    Emite señales cuando cambian los filtros.
    """

    # Señales
    filter_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Configura la interfaz de la barra de filtros"""
        theme = get_theme()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Filtro por estado
        layout.addWidget(QLabel("Estado:"))
        self.status_filter = QPushButton("Todos")
        self.status_filter.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        self.status_filter.clicked.connect(lambda: self._show_status_menu())
        layout.addWidget(self.status_filter)

        layout.addStretch()

        # Botón de limpiar filtros
        clear_btn = QPushButton("✕ Limpiar filtros")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        clear_btn.clicked.connect(self._clear_filters)
        layout.addWidget(clear_btn)

        # Indicador de filtros activos
        self.filter_indicator = QLabel("")
        self.filter_indicator.setStyleSheet(f"""
            color: {theme.success};
            font-size: 11px;
        """)
        layout.addWidget(self.filter_indicator)

        self.setLayout(layout)

    def _show_status_menu(self):
        """Muestra un menú para seleccionar estado"""
        from PyQt6.QtWidgets import QMenu

        menu = QMenu(self)

        for status in ["Todos", "Pendiente", "En ruta", "Entregado", "Retrasado"]:
            action = menu.addAction(status)
            action.triggered.connect(lambda checked, s=status: self._set_status_filter(s))

        menu.exec(self.status_filter.mapToGlobal(self.status_filter.rect().bottomLeft()))

    def _set_status_filter(self, status: str):
        """Aplica el filtro por estado"""
        self.status_filter.setText(status)
        self.filter_changed.emit({"status": status if status != "Todos" else ""})

        if status != "Todos":
            self.filter_indicator.setText(f"🔍 Filtro: {status}")
        else:
            self.filter_indicator.setText("")

    def _clear_filters(self):
        """Limpia todos los filtros"""
        self.status_filter.setText("Todos")
        self.filter_indicator.setText("")
        self.filter_changed.emit({"status": ""})