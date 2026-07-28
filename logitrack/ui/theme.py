#!/usr/bin/env python3
"""
LogiTrack Desktop - Sistema de Temas
Fase 5: Componentes visuales avanzados y personalización de estilos
"""

from enum import Enum
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt


class ThemeMode(Enum):
    """Modos de tema disponibles"""
    LIGHT = "light"
    DARK = "dark"


class ThemeColors:
    """Colores del tema actual"""

    def __init__(self, mode: ThemeMode = ThemeMode.LIGHT):
        self.mode = mode
        self._set_colors()

    def _set_colors(self):
        """Define los colores según el modo"""
        if self.mode == ThemeMode.LIGHT:
            # Colores para modo claro
            self.background = "#ffffff"
            self.background_secondary = "#f8f9fa"
            self.text = "#212529"
            self.text_secondary = "#6c757d"
            self.border = "#dee2e6"
            self.card_background = "#ffffff"
            self.card_shadow = "rgba(0,0,0,0.1)"
            self.input_background = "#ffffff"
            self.input_border = "#ced4da"
            
            # Colores de estado
            self.success = "#28a745"
            self.success_light = "#d4edda"
            self.warning = "#ffc107"
            self.warning_light = "#fff3cd"
            self.danger = "#dc3545"
            self.danger_light = "#f8d7da"
            self.info = "#17a2b8"
            self.info_light = "#d1ecf1"
            self.primary = "#007bff"
            self.primary_light = "#cce5ff"
            
        else:
            # Colores para modo oscuro
            self.background = "#1a1a2e"
            self.background_secondary = "#16213e"
            self.text = "#e4e6eb"
            self.text_secondary = "#a0a4b0"
            self.border = "#2d2d44"
            self.card_background = "#252545"
            self.card_shadow = "rgba(0,0,0,0.3)"
            self.input_background = "#1a1a2e"
            self.input_border = "#2d2d44"
            
            # Colores de estado (ajustados para oscuro)
            self.success = "#2ecc71"
            self.success_light = "#1a3a2a"
            self.warning = "#f1c40f"
            self.warning_light = "#3a3520"
            self.danger = "#e74c3c"
            self.danger_light = "#3a1a1a"
            self.info = "#3498db"
            self.info_light = "#1a2a3a"
            self.primary = "#4a9eff"
            self.primary_light = "#1a2a4a"

    def get_palette(self) -> QPalette:
        """Obtiene la paleta de colores para Qt"""
        palette = QPalette()
        
        # Colores base
        palette.setColor(QPalette.ColorRole.Window, QColor(self.background))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(self.text))
        palette.setColor(QPalette.ColorRole.Base, QColor(self.input_background))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(self.background_secondary))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(self.background))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(self.text))
        palette.setColor(QPalette.ColorRole.Text, QColor(self.text))
        palette.setColor(QPalette.ColorRole.Button, QColor(self.background_secondary))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(self.text))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(self.text))
        
        # Colores para enlaces
        palette.setColor(QPalette.ColorRole.Link, QColor(self.primary))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(self.primary))
        
        # Colores para estados
        palette.setColor(QPalette.ColorRole.Highlight, QColor(self.primary))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        
        return palette

    def get_stylesheet(self) -> str:
        """Obtiene el stylesheet para la aplicación"""
        return f"""
            /* Estilos generales */
            QMainWindow {{
                background-color: {self.background};
            }}
            
            QWidget {{
                background-color: {self.background};
                color: {self.text};
                font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            }}
            
            /* Grupos */
            QGroupBox {{
                background-color: {self.card_background};
                border: 1px solid {self.border};
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 10px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                color: {self.text};
                font-size: 13px;
            }}
            
            /* Líneas de entrada */
            QLineEdit {{
                background-color: {self.input_background};
                border: 1px solid {self.input_border};
                border-radius: 4px;
                padding: 8px 10px;
                color: {self.text};
                selection-background-color: {self.primary};
            }}
            QLineEdit:focus {{
                border-color: {self.primary};
            }}
            QLineEdit::placeholder {{
                color: {self.text_secondary};
            }}
            
            /* ComboBox */
            QComboBox {{
                background-color: {self.input_background};
                border: 1px solid {self.input_border};
                border-radius: 4px;
                padding: 8px 10px;
                color: {self.text};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {self.text_secondary};
                margin-right: 8px;
            }}
            QComboBox:hover {{
                border-color: {self.primary};
            }}
            QComboBox QAbstractItemView {{
                background-color: {self.input_background};
                border: 1px solid {self.border};
                color: {self.text};
                selection-background-color: {self.primary};
                selection-color: white;
            }}
            
            /* Botones */
            QPushButton {{
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                opacity: 0.8;
            }}
            QPushButton:disabled {{
                background-color: {self.border};
                color: {self.text_secondary};
            }}
            
            /* Tablas */
            QTableWidget {{
                background-color: {self.background};
                alternate-background-color: {self.background_secondary};
                gridline-color: {self.border};
                border: 1px solid {self.border};
                border-radius: 4px;
            }}
            QTableWidget::item {{
                padding: 6px;
                color: {self.text};
            }}
            QTableWidget::item:selected {{
                background-color: {self.primary};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {self.background_secondary};
                color: {self.text};
                padding: 8px;
                border: 1px solid {self.border};
                font-weight: bold;
            }}
            QHeaderView::section:hover {{
                background-color: {self.border};
            }}
            
            /* Labels */
            QLabel {{
                color: {self.text};
            }}
            
            /* Scrollbars */
            QScrollBar:vertical {{
                background-color: {self.background_secondary};
                width: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {self.border};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {self.text_secondary};
            }}
            QScrollBar:horizontal {{
                background-color: {self.background_secondary};
                height: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {self.border};
                border-radius: 6px;
                min-width: 20px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {self.text_secondary};
            }}
            
            /* Progress Bar */
            QProgressBar {{
                background-color: {self.background_secondary};
                border-radius: 4px;
                height: 20px;
                text-align: center;
                color: {self.text};
            }}
            QProgressBar::chunk {{
                background-color: {self.primary};
                border-radius: 4px;
            }}
            
            /* Status Bar */
            QStatusBar {{
                background-color: {self.background_secondary};
                color: {self.text_secondary};
                padding: 4px 8px;
            }}
            
            /* Separadores */
            QFrame[frameShape="4"] {{
                color: {self.border};
            }}
        """


# Instancia global del tema
current_theme = ThemeColors(ThemeMode.LIGHT)


def apply_theme(app, mode: ThemeMode):
    """Aplica un tema a la aplicación"""
    global current_theme
    current_theme = ThemeColors(mode)
    
    # Aplicar paleta
    app.setPalette(current_theme.get_palette())
    
    # Aplicar stylesheet
    app.setStyleSheet(current_theme.get_stylesheet())


def get_theme() -> ThemeColors:
    """Obtiene los colores del tema actual"""
    return current_theme


def toggle_theme(app):
    """Alterna entre modo claro y oscuro"""
    if current_theme.mode == ThemeMode.LIGHT:
        apply_theme(app, ThemeMode.DARK)
        return ThemeMode.DARK
    else:
        apply_theme(app, ThemeMode.LIGHT)
        return ThemeMode.LIGHT