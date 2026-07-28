#!/usr/bin/env python3
"""
LogiTrack Desktop - Aplicación principal
Fase 5: Componentes visuales avanzados y personalización de estilos
"""

import sys
import random
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication,
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
    QCheckBox,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QKeySequence, QColor

from .workers import ShipmentWorker
from .ui.theme import ThemeMode, apply_theme, toggle_theme, get_theme
from .ui.components import StatusBadge, KPICard, FilterBar


class LogiTrackWindow(QMainWindow):
    """Ventana principal de LogiTrack Desktop - Fase 5"""

    def __init__(self):
        super().__init__()

        # Configuración básica
        self.setWindowTitle("LogiTrack Desktop")
        self.setMinimumSize(1000, 650)
        self.resize(1200, 750)

        # Datos en memoria
        self.shipments = []
        self.next_id = 1
        self.workers = []
        self.current_worker = None
        self.current_filter = {}

        # Configurar UI
        self._setup_menu()
        self._setup_central_widget()
        self._setup_status_bar()
        self._setup_shortcuts()

        # Cargar datos
        self._load_initial_data()

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
        new_action.triggered.connect(self._clear_form)
        shipments_menu.addAction(new_action)

        sync_action = QAction("&Sincronizar con API", self)
        sync_action.setShortcut("Ctrl+Shift+S")
        sync_action.triggered.connect(self._sync_with_api)
        shipments_menu.addAction(sync_action)

        help_menu = menubar.addMenu("&Ayuda")
        about_action = QAction("&Acerca de", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_central_widget(self):
        """Configura el widget central con componentes avanzados"""
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # ===== KPI CARDS (fila superior) =====
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

        # Título y barra de acciones
        title_layout = QHBoxLayout()
        table_title = QLabel("📋 Lista de Envíos")
        table_title.setStyleSheet("font-size: 16px; font-weight: bold;")

        # Barra de filtros
        self.filter_bar = FilterBar()
        self.filter_bar.filter_changed.connect(self._apply_filters)

        title_layout.addWidget(table_title)
        title_layout.addStretch()
        title_layout.addWidget(self.filter_bar)

        left_layout.addLayout(title_layout)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Destinatario", "Dirección", "Tipo", "Estado", "Fecha", ""
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        # Ocultar la última columna (índice 6) - usada para el badge
        self.table.hideColumn(6)
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
        self.tipo_combo.addItems(["Paquete", "Documento", "Carga", "Mercancía"])
        self.tipo_combo.setMinimumHeight(30)
        form_layout.addWidget(self.tipo_combo, 2, 1)

        form_layout.addWidget(QLabel("Estado:"), 3, 0)
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(["Pendiente", "En ruta", "Entregado", "Retrasado"])
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
            QPushButton:hover { background-color: #218838; }
            QPushButton:disabled { background-color: #6c757d; }
        """)
        self.guardar_btn.clicked.connect(self._save_shipment_async)

        self.limpiar_btn = QPushButton("🧹 Limpiar")
        self.limpiar_btn.setMinimumHeight(35)
        self.limpiar_btn.clicked.connect(self._clear_form)

        self.cancelar_btn = QPushButton("⏹ Cancelar")
        self.cancelar_btn.setMinimumHeight(35)
        self.cancelar_btn.setEnabled(False)
        self.cancelar_btn.clicked.connect(self._cancel_current_task)

        button_layout.addWidget(self.guardar_btn)
        button_layout.addWidget(self.limpiar_btn)
        button_layout.addWidget(self.cancelar_btn)
        form_layout.addLayout(button_layout, 4, 0, 1, 2)

        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        form_layout.addWidget(separator, 5, 0, 1, 2)

        # Barra de progreso
        form_layout.addWidget(QLabel("Progreso:"), 6, 0)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        form_layout.addWidget(self.progress_bar, 6, 1)

        # Búsqueda
        form_layout.addWidget(QLabel("🔍 Buscar:"), 7, 0)
        self.buscar_input = QLineEdit()
        self.buscar_input.setPlaceholderText("Buscar envíos...")
        self.buscar_input.setMinimumHeight(30)
        self.buscar_input.textChanged.connect(self._filter_table)
        form_layout.addWidget(self.buscar_input, 7, 1)

        form_group.setLayout(form_layout)
        right_layout.addWidget(form_group)

        # Contador de envíos
        self.counter_label = QLabel("📊 Total: 0 envíos")
        self.counter_label.setStyleSheet("""
            font-size: 12px;
            padding: 8px;
            border-radius: 4px;
        """)
        right_layout.addWidget(self.counter_label)

        # Estado de la tarea
        self.task_status_label = QLabel("✅ Sin tareas en curso")
        self.task_status_label.setStyleSheet("font-size: 11px; padding: 5px;")
        right_layout.addWidget(self.task_status_label)

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
        self.statusBar().showMessage("✅ Listo | Fase 5: Componentes avanzados y estilos")

    def _setup_shortcuts(self):
        """Configura atajos de teclado"""
        new_shortcut = QAction("Nuevo", self)
        new_shortcut.setShortcut(QKeySequence.StandardKey.New)
        new_shortcut.triggered.connect(self._clear_form)
        self.addAction(new_shortcut)

        save_shortcut = QAction("Guardar", self)
        save_shortcut.setShortcut(QKeySequence.StandardKey.Save)
        save_shortcut.triggered.connect(self._save_shipment_async)
        self.addAction(save_shortcut)

        esc_shortcut = QAction("Limpiar", self)
        esc_shortcut.setShortcut(QKeySequence.StandardKey.Cancel)
        esc_shortcut.triggered.connect(self._clear_form)
        self.addAction(esc_shortcut)

        theme_shortcut = QAction("Tema", self)
        theme_shortcut.setShortcut("Ctrl+T")
        theme_shortcut.triggered.connect(self._toggle_theme)
        self.addAction(theme_shortcut)

    # ============================================================
    # MÉTODOS DE TEMA
    # ============================================================

    def _toggle_theme(self):
        """Alterna entre modo claro y oscuro"""
        new_mode = toggle_theme(QApplication.instance())
        self.statusBar().showMessage(f"🌓 Tema cambiado a: {new_mode.value}", 3000)
        self._update_styles()

    def _update_styles(self):
        """Actualiza los estilos de los componentes"""
        theme = get_theme()
        self.counter_label.setStyleSheet(f"""
            font-size: 12px;
            padding: 8px;
            border-radius: 4px;
            background-color: {theme.background_secondary};
            color: {theme.text_secondary};
        """)
        self.task_status_label.setStyleSheet(f"""
            font-size: 11px;
            padding: 5px;
            color: {theme.success};
        """)

    # ============================================================
    # MÉTODOS DE DATOS Y TABLA
    # ============================================================

    def _load_initial_data(self):
        """Carga datos iniciales de forma asíncrona"""
        self._load_shipments_async()

    def _load_shipments_async(self):
        """Carga envíos en segundo plano"""
        self.table.setRowCount(0)
        self.shipments.clear()

        # Crear datos de ejemplo más completos
        sample_data = [
            ("María González", "Av. Principal 123", "Paquete", "Entregado"),
            ("Carlos Rodríguez", "Calle 45 #23", "Documento", "En ruta"),
            ("Ana Martínez", "Blvd. Norte 789", "Mercancía", "Pendiente"),
            ("Luis Pérez", "Calle Sur 456", "Carga", "Retrasado"),
            ("Sofía Ramírez", "Av. Central 321", "Paquete", "Entregado"),
            ("Diego Torres", "Calle Oriente 159", "Documento", "En ruta"),
            ("Laura Gómez", "Av. Poniente 753", "Mercancía", "Pendiente"),
            ("Javier Morales", "Calle Norte 951", "Carga", "Entregado"),
        ]

        for destinatario, direccion, tipo, estado in sample_data:
            self._add_shipment_to_table(destinatario, direccion, tipo, estado)

        self._update_counter()
        self._update_kpis()
        self.statusBar().showMessage(f"✅ Cargados {len(sample_data)} envíos", 3000)

    def _add_shipment_to_table(self, destinatario, direccion, tipo, estado):
        """Añade un envío a la tabla con StatusBadge"""
        shipment_id = self.next_id
        self.next_id += 1
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

        self.shipments.append({
            "id": shipment_id,
            "destinatario": destinatario,
            "direccion": direccion,
            "tipo": tipo,
            "estado": estado,
            "fecha": fecha
        })

        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(str(shipment_id)))
        self.table.setItem(row, 1, QTableWidgetItem(destinatario))
        self.table.setItem(row, 2, QTableWidgetItem(direccion))
        self.table.setItem(row, 3, QTableWidgetItem(tipo))
        # Columna 4: Estado (texto)
        self.table.setItem(row, 4, QTableWidgetItem(estado))
        self.table.setItem(row, 5, QTableWidgetItem(fecha))

        # Columna 6: StatusBadge (widget personalizado)
        badge = StatusBadge(estado)
        self.table.setCellWidget(row, 6, badge)

        # Colorear la celda de estado (texto) para compatibilidad
        self._color_status_cell(row)

    def _color_status_cell(self, row):
        """Colorea la celda de estado"""
        estado_item = self.table.item(row, 4)
        if estado_item:
            estado = estado_item.text()
            colors = {
                "Entregado": "#28a745",
                "En ruta": "#ffc107",
                "Pendiente": "#17a2b8",
                "Retrasado": "#dc3545"
            }
            color = colors.get(estado, "#6c757d")
            estado_item.setBackground(self._get_color(color))
            if estado in ["Entregado", "Retrasado"]:
                estado_item.setForeground(Qt.GlobalColor.white)
            else:
                estado_item.setForeground(Qt.GlobalColor.black)

    def _get_color(self, hex_color):
        """Convierte hex a QColor"""
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return QColor(r, g, b)

    def _update_kpis(self):
        """Actualiza las tarjetas KPI"""
        total = self.table.rowCount()
        pendientes = 0
        entregados = 0
        retrasados = 0

        for row in range(self.table.rowCount()):
            estado_item = self.table.item(row, 4)
            if estado_item:
                estado = estado_item.text()
                if estado == "Pendiente":
                    pendientes += 1
                elif estado == "Entregado":
                    entregados += 1
                elif estado == "Retrasado":
                    retrasados += 1

        self.kpi_total.update_value(str(total))
        self.kpi_pendientes.update_value(str(pendientes))
        self.kpi_entregados.update_value(str(entregados))
        self.kpi_retrasados.update_value(str(retrasados))

    # ============================================================
    # MÉTODOS DE FILTROS
    # ============================================================

    def _apply_filters(self, filters):
        """Aplica los filtros a la tabla"""
        self.current_filter = filters
        self._filter_table(self.buscar_input.text())

    def _filter_table(self, text):
        """Filtra la tabla según texto y filtros activos"""
        text = text.lower()
        status_filter = self.current_filter.get("status", "")

        for row in range(self.table.rowCount()):
            visible = True

            # Filtro por texto
            if text:
                text_visible = False
                for col in range(self.table.columnCount() - 1):  # Excluir columna del badge
                    item = self.table.item(row, col)
                    if item and text in item.text().lower():
                        text_visible = True
                        break
                visible = visible and text_visible

            # Filtro por estado
            if status_filter and visible:
                estado_item = self.table.item(row, 4)
                if estado_item:
                    visible = estado_item.text() == status_filter

            self.table.setRowHidden(row, not visible)

        self._update_counter()

    # ============================================================
    # MÉTODOS DE GUARDADO Y ACCIONES
    # ============================================================

    def _save_shipment_async(self):
        """Guarda un envío en segundo plano"""
        destinatario = self.destinatario_input.text().strip()
        direccion = self.direccion_input.text().strip()

        if not destinatario:
            QMessageBox.warning(self, "Campo requerido", "El campo 'Destinatario' es obligatorio.")
            self.destinatario_input.setFocus()
            return

        if not direccion:
            QMessageBox.warning(self, "Campo requerido", "El campo 'Dirección' es obligatorio.")
            self.direccion_input.setFocus()
            return

        tipo = self.tipo_combo.currentText()
        estado = self.estado_combo.currentText()

        # Añadir directamente (sin worker para simplicidad)
        self._add_shipment_to_table(destinatario, direccion, tipo, estado)
        self._update_counter()
        self._update_kpis()
        self._clear_form()
        self.statusBar().showMessage(f"✅ Envío #{self.next_id - 1} guardado", 3000)

    def _sync_with_api(self):
        """Simula sincronización con API"""
        self.statusBar().showMessage("🔄 Sincronizando...", 3000)
        import time
        time.sleep(1)
        self.statusBar().showMessage("✅ Sincronización completada", 3000)
        QMessageBox.information(self, "Sincronización", "✅ Se sincronizaron todos los envíos correctamente.")

    def _clear_form(self):
        """Limpia el formulario"""
        self.destinatario_input.clear()
        self.direccion_input.clear()
        self.tipo_combo.setCurrentIndex(0)
        self.estado_combo.setCurrentIndex(0)
        self.destinatario_input.setFocus()
        self.statusBar().showMessage("🧹 Formulario limpiado", 2000)

    def _cancel_current_task(self):
        """Cancela la tarea actual"""
        # Simplemente resetear el estado
        self.progress_bar.hide()
        self.cancelar_btn.setEnabled(False)
        self.guardar_btn.setEnabled(True)
        self.statusBar().showMessage("⏹ Tarea cancelada", 3000)

    def _update_counter(self):
        """Actualiza el contador de envíos"""
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
            <p><b>Versión:</b> 0.5.0 (Fase 5)</p>
            <p><b>Framework:</b> PyQt6</p>
            <p><b>Características:</b></p>
            <ul>
                <li>🌓 Tema claro/oscuro</li>
                <li>🎨 Componentes visuales avanzados</li>
                <li>📊 Tarjetas KPI</li>
                <li>🏷️ StatusBadge con colores</li>
                <li>🔍 Filtros avanzados</li>
            </ul>
            <hr>
            <p style="color: #7f8c8d; font-size: 10px;">
                🚀 Proyecto Integrador - Fase 5
            </p>
            """,
        )

    def closeEvent(self, event):
        """Maneja el cierre de la ventana"""
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


def main():
    """Punto de entrada principal"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Aplicar tema claro por defecto
    apply_theme(app, ThemeMode.LIGHT)

    window = LogiTrackWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()