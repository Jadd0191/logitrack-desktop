#!/usr/bin/env python3
"""
LogiTrack Desktop - Ventana Principal (Vista)
Fase 7: Integración de datos: BBDD y API

REGLA: Esta vista NO contiene lógica de negocio.
Toda la lógica está en el Controlador y Servicios.
"""

import sys
from typing import Dict, Any, Optional, List
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QMessageBox,
    QHeaderView,
    QSplitter,
    QFrame,
    QSizePolicy,
    QProgressBar,
    QApplication,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence, QColor

# ✅ CORRECTO: Importar solo enums/constantes desde models
from ..models import ShipmentStatus, ShipmentType
from ..controllers import ShipmentController
from ..ui.theme import ThemeMode, apply_theme, toggle_theme, get_theme
from ..ui.components import StatusBadge, KPICard, FilterBar


class LogiTrackWindow(QMainWindow):
    """
    Vista principal de LogiTrack Desktop.
    SOLO contiene widgets y layouts. Sin lógica de negocio.
    """
    
    # Señal para cambiar el tema
    theme_changed = pyqtSignal()
    
    def __init__(self, controller: ShipmentController):
        super().__init__()
        
        self.controller = controller
        self.current_filter = {}
        
        # Configuración básica
        self.setWindowTitle("LogiTrack Desktop")
        self.setMinimumSize(1000, 650)
        self.resize(1200, 750)
        
        # Configurar UI
        self._setup_menu()
        self._setup_central_widget()
        self._setup_status_bar()
        self._setup_shortcuts()
        
        # Conectar señales del controlador
        self._connect_controller_signals()
        
        # Cargar datos
        self.controller.load_shipments()

    def _setup_menu(self):
        """Configura la barra de menú"""
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("&Archivo")
        exit_action = QAction("&Salir", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menú Ver
        view_menu = menubar.addMenu("&Ver")
        theme_action = QAction("🌓 Alternar Tema", self)
        theme_action.setShortcut("Ctrl+T")
        theme_action.triggered.connect(self._toggle_theme)
        view_menu.addAction(theme_action)
        
        # Menú Envíos
        shipments_menu = menubar.addMenu("&Envíos")
        new_action = QAction("&Nuevo Envío", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.clear_form)
        shipments_menu.addAction(new_action)
        
        # Menú Ayuda
        help_menu = menubar.addMenu("&Ayuda")
        about_action = QAction("&Acerca de", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_central_widget(self):
        """Configura el widget central - SOLO UI"""
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # ===== KPI CARDS =====
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(10)
        
        self.kpi_total = KPICard("Total Envíos", "0", "📦")
        self.kpi_pendientes = KPICard("Pendientes", "0", "⏳", "#17a2b8")
        self.kpi_entregados = KPICard("Entregados", "0", "✅", "#28a745")
        self.kpi_retrasados = KPICard("Retrasados", "0", "⚠️", "#dc3545")
        
        kpi_layout.addWidget(self.kpi_total)
        kpi_layout.addWidget(self.kpi_pendientes)
        kpi_layout.addWidget(self.kpi_entregados)
        kpi_layout.addWidget(self.kpi_retrasados)
        
        main_layout.addLayout(kpi_layout)
        
        # ===== SPLITTER =====
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(5)
        splitter.setChildrenCollapsible(False)
        
        # --- Panel izquierdo: Tabla ---
        left_widget = QWidget()
        left_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(8)
        left_layout.setContentsMargins(5, 5, 5, 5)
        
        # Título y filtros
        title_layout = QHBoxLayout()
        table_title = QLabel("📋 Lista de Envíos")
        table_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        
        self.filter_bar = FilterBar()
        self.filter_bar.filter_changed.connect(self._apply_filters)
        
        title_layout.addWidget(table_title)
        title_layout.addStretch()
        title_layout.addWidget(self.filter_bar)
        left_layout.addLayout(title_layout)
        
        # ✅ TABLA CON COLUMNAS DE API
        self.table = QTableWidget()
        self.table.setColumnCount(10)  # ID, Destinatario, Dirección, Tipo, Estado, Fecha, Distancia, Tiempo, Clima, Badge
        self.table.setHorizontalHeaderLabels([
            "ID", 
            "Destinatario", 
            "Dirección", 
            "Tipo", 
            "Estado", 
            "Fecha",
            "Distancia",
            "Tiempo",
            "Clima",
            ""  # StatusBadge
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.hideColumn(9)  # Ocultar columna del badge
        left_layout.addWidget(self.table)
        
        # --- Panel derecho: Formulario ---
        right_widget = QWidget()
        right_widget.setMaximumWidth(380)
        right_widget.setMinimumWidth(280)
        right_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(10)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        # Grupo: Nuevo Envío
        form_group = QGroupBox("📝 Nuevo Envío")
        form_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                padding-top: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0px 5px 0px 5px;
            }
        """)
        
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setHorizontalSpacing(8)
        form_layout.setContentsMargins(15, 20, 15, 15)
        
        # Campos del formulario
        form_layout.addWidget(QLabel("Destinatario:"), 0, 0)
        self.destinatario_input = QLineEdit()
        self.destinatario_input.setPlaceholderText("Nombre completo")
        self.destinatario_input.setMinimumHeight(30)
        form_layout.addWidget(self.destinatario_input, 0, 1)
        
        form_layout.addWidget(QLabel("Dirección:"), 1, 0)
        self.direccion_input = QLineEdit()
        self.direccion_input.setPlaceholderText("Calle y número")
        self.direccion_input.setMinimumHeight(30)
        form_layout.addWidget(self.direccion_input, 1, 1)
        
        form_layout.addWidget(QLabel("Tipo:"), 2, 0)
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(ShipmentType.all())
        self.tipo_combo.setMinimumHeight(30)
        form_layout.addWidget(self.tipo_combo, 2, 1)
        
        form_layout.addWidget(QLabel("Estado:"), 3, 0)
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(ShipmentStatus.all())
        self.estado_combo.setMinimumHeight(30)
        form_layout.addWidget(self.estado_combo, 3, 1)
        
        # Botones
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.guardar_btn = QPushButton("💾 Guardar")
        self.guardar_btn.setMinimumHeight(35)
        self.guardar_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.guardar_btn.clicked.connect(self._on_save_clicked)
        
        self.limpiar_btn = QPushButton("🧹 Limpiar")
        self.limpiar_btn.setMinimumHeight(35)
        self.limpiar_btn.clicked.connect(self.clear_form)
        
        button_layout.addWidget(self.guardar_btn)
        button_layout.addWidget(self.limpiar_btn)
        form_layout.addLayout(button_layout, 4, 0, 1, 2)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        form_layout.addWidget(separator, 5, 0, 1, 2)
        
        # Búsqueda
        form_layout.addWidget(QLabel("🔍 Buscar:"), 6, 0)
        self.buscar_input = QLineEdit()
        self.buscar_input.setPlaceholderText("Buscar envíos...")
        self.buscar_input.setMinimumHeight(30)
        self.buscar_input.textChanged.connect(self._on_search_changed)
        form_layout.addWidget(self.buscar_input, 6, 1)
        
        form_group.setLayout(form_layout)
        right_layout.addWidget(form_group)
        
        # Contador
        self.counter_label = QLabel("📊 Total: 0 envíos")
        self.counter_label.setStyleSheet("""
            font-size: 12px;
            padding: 8px;
            border-radius: 4px;
        """)
        right_layout.addWidget(self.counter_label)
        
        right_layout.addStretch()
        
        # --- Agregar widgets al splitter ---
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([700, 300])
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def _setup_status_bar(self):
        """Configura la barra de estado"""
        self.statusBar().showMessage("✅ Listo | Fase 7: Integración de datos")

    def _setup_shortcuts(self):
        """Configura atajos de teclado"""
        new_shortcut = QAction("Nuevo", self)
        new_shortcut.setShortcut(QKeySequence.StandardKey.New)
        new_shortcut.triggered.connect(self.clear_form)
        self.addAction(new_shortcut)

        theme_shortcut = QAction("Tema", self)
        theme_shortcut.setShortcut("Ctrl+T")
        theme_shortcut.triggered.connect(self._toggle_theme)
        self.addAction(theme_shortcut)

    def _connect_controller_signals(self):
        """Conecta las señales del controlador"""
        self.controller.shipments_loaded.connect(self._on_shipments_loaded)
        self.controller.shipment_saved.connect(self._on_shipment_saved)
        self.controller.stats_updated.connect(self._on_stats_updated)
        self.controller.error_occurred.connect(self._on_error)

    # ============================================================
    # MANEJADORES DE UI (Solo emiten eventos)
    # ============================================================

    def _on_save_clicked(self):
        """Maneja el clic en Guardar"""
        data = {
            "destinatario": self.destinatario_input.text().strip(),
            "direccion": self.direccion_input.text().strip(),
            "tipo": self.tipo_combo.currentText(),
            "estado": self.estado_combo.currentText(),
        }
        self.controller.save_shipment(data)

    def _on_search_changed(self, text):
        """Maneja el cambio en la búsqueda"""
        self._filter_table(text)

    def _toggle_theme(self):
        """Alterna el tema"""
        toggle_theme(QApplication.instance())
        self.theme_changed.emit()
        self.statusBar().showMessage("🌓 Tema cambiado", 3000)

    def _apply_filters(self, filters):
        """Aplica filtros"""
        self.current_filter = filters
        self._filter_table(self.buscar_input.text())

    def clear_form(self):
        """Limpia el formulario"""
        self.destinatario_input.clear()
        self.direccion_input.clear()
        self.tipo_combo.setCurrentIndex(0)
        self.estado_combo.setCurrentIndex(0)
        self.destinatario_input.setFocus()
        self.statusBar().showMessage("🧹 Formulario limpiado", 2000)

    # ============================================================
    # RECEPTORES DE SEÑALES (Actualizan la UI)
    # ============================================================

    def _on_shipments_loaded(self, shipments):
        """Actualiza la tabla con los envíos cargados"""
        self.table.setRowCount(0)
        for shipment in shipments:
            self._add_shipment_to_table(shipment)
        self._update_counter()

    def _on_shipment_saved(self, shipment):
        """Añade un envío a la tabla"""
        self._add_shipment_to_table(shipment)
        self._update_counter()
        self.clear_form()
        self.statusBar().showMessage(f"✅ Envío #{shipment.id} guardado", 3000)

    def _on_stats_updated(self, stats):
        """Actualiza las tarjetas KPI"""
        self.kpi_total.update_value(str(stats.get("total", 0)))
        self.kpi_pendientes.update_value(str(stats.get("pendientes", 0)))
        self.kpi_entregados.update_value(str(stats.get("entregados", 0)))
        self.kpi_retrasados.update_value(str(stats.get("retrasados", 0)))

    def _on_error(self, error_msg):
        """Muestra un error"""
        QMessageBox.warning(self, "Error", f"❌ {error_msg}")

    # ============================================================
    # MÉTODOS AUXILIARES DE UI
    # ============================================================

    def _add_shipment_to_table(self, shipment):
        """
        Añade un envío a la tabla con datos de API.
        """
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Columnas básicas
        self.table.setItem(row, 0, QTableWidgetItem(str(shipment.id)))
        self.table.setItem(row, 1, QTableWidgetItem(shipment.destinatario))
        self.table.setItem(row, 2, QTableWidgetItem(shipment.direccion))
        self.table.setItem(row, 3, QTableWidgetItem(shipment.tipo))
        self.table.setItem(row, 4, QTableWidgetItem(shipment.estado))
        self.table.setItem(row, 5, QTableWidgetItem(shipment.fecha))
        
        # ✅ DATOS DE API (Columnas 6, 7, 8)
        distancia = f"{shipment.distancia_km} km" if shipment.distancia_km else "N/A"
        self.table.setItem(row, 6, QTableWidgetItem(distancia))
        
        tiempo = shipment.tiempo_estimado if shipment.tiempo_estimado else "N/A"
        self.table.setItem(row, 7, QTableWidgetItem(tiempo))
        
        clima = shipment.clima if shipment.clima else "N/A"
        self.table.setItem(row, 8, QTableWidgetItem(clima))
        
        # StatusBadge (columna 9)
        badge = StatusBadge(shipment.estado)
        self.table.setCellWidget(row, 9, badge)
        
        self._color_status_cell(row)

    def _color_status_cell(self, row):
        """Colorea la celda de estado"""
        estado_item = self.table.item(row, 4)
        if estado_item:
            color = ShipmentStatus.get_color(estado_item.text())
            hex_color = color.lstrip("#")
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            estado_item.setBackground(QColor(r, g, b))
            if estado_item.text() in ["Entregado", "Retrasado"]:
                estado_item.setForeground(Qt.GlobalColor.white)
            else:
                estado_item.setForeground(Qt.GlobalColor.black)

    def _filter_table(self, text):
        """Filtra la tabla incluyendo columnas de API"""
        text = text.lower()
        status_filter = self.current_filter.get("status", "")
        
        for row in range(self.table.rowCount()):
            visible = True
            
            if text:
                text_visible = False
                # Buscar en todas las columnas excepto la última (badge)
                for col in range(self.table.columnCount() - 1):
                    item = self.table.item(row, col)
                    if item and text in item.text().lower():
                        text_visible = True
                        break
                visible = visible and text_visible
            
            if status_filter and visible:
                estado_item = self.table.item(row, 4)
                if estado_item:
                    visible = estado_item.text() == status_filter
            
            self.table.setRowHidden(row, not visible)
        
        self._update_counter()

    def _update_counter(self):
        """Actualiza el contador"""
        total = self.table.rowCount()
        visible = sum(1 for row in range(self.table.rowCount()) if not self.table.isRowHidden(row))
        self.counter_label.setText(f"📊 Total: {total} envíos | Visibles: {visible}")

    def _show_about(self):
        """Diálogo Acerca de"""
        QMessageBox.about(
            self,
            "Acerca de LogiTrack Desktop",
            """
            <h2>🚚 LogiTrack Desktop</h2>
            <p><b>Versión:</b> 1.0.0</p>
            <p><b>Arquitectura:</b> MVC</p>
            <p><b>Framework:</b> PyQt6</p>
            <p><b>Características:</b></p>
            <ul>
                <li>🏗️ Arquitectura MVC</li>
                <li>📦 Modelos con validación</li>
                <li>🔧 Servicios de negocio</li>
                <li>🎮 Controladores</li>
                <li>🖥️ Vistas sin lógica</li>
                <li>🌐 Integración con API</li>
                <li>💾 Persistencia SQLite</li>
                <li>🌓 Tema claro/oscuro</li>
            </ul>
            <hr>
            <p style="color: #7f8c8d; font-size: 10px;">
                🚀 Proyecto Integrador - LogiTrack
            </p>
            """,
        )

    def closeEvent(self, event):
        """Maneja el cierre"""
        reply = QMessageBox.question(
            self,
            "Salir",
            "¿Estás seguro de que deseas salir?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()