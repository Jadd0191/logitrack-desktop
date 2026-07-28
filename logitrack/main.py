#!/usr/bin/env python3
"""
LogiTrack Desktop - Aplicación principal
Fase 1: Esqueleto mínimo de ventana
"""

import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QVBoxLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction


class LogiTrackWindow(QMainWindow):
    """Ventana principal de LogiTrack Desktop"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LogiTrack Desktop")
        self.setMinimumSize(1024, 768)
        self._setup_menu()
        self._setup_central_widget()
        self._setup_status_bar()

    def _setup_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&Archivo")
        exit_action = QAction("&Salir", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("&Ayuda")
        about_action = QAction("&Acerca de", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_central_widget(self):
        central_widget = QWidget()
        layout = QVBoxLayout()

        welcome_label = QLabel("🚚 LogiTrack Desktop v0.1")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            padding: 50px;
        """)

        subtitle_label = QLabel("Estación de Control Logístico de Escritorio")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
        """)

        phase_label = QLabel("📍 Fase 1: Fundamentos y elección de framework")
        phase_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        phase_label.setStyleSheet("""
            font-size: 12px;
            color: #3498db;
            margin-top: 20px;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 5px;
        """)

        layout.addWidget(welcome_label)
        layout.addWidget(subtitle_label)
        layout.addWidget(phase_label)
        layout.addStretch()

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def _setup_status_bar(self):
        self.statusBar().showMessage("✅ Listo | PyQt6 | Modo: Desarrollo")

    def _show_about(self):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "Acerca de LogiTrack Desktop",
            """
            <h2>LogiTrack Desktop</h2>
            <p><b>Versión:</b> 0.1.0 (Fase 1)</p>
            <p><b>Framework:</b> PyQt6</p>
            <p><b>Descripción:</b> Estación de Control Logístico de Escritorio</p>
            <p><b>Diplomado:</b> Especialista en Desarrollo de Software con Python SSR</p>
            <p><b>Módulo:</b> 1 - Programación visual y frameworks GUI</p>
            <hr>
            <p style="color: #7f8c8d; font-size: 10px;">
                🚀 Proyecto Integrador - LogiTrack
            </p>
            """,
        )

    def closeEvent(self, event):
        event.accept()