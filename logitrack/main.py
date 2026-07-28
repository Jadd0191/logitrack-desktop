#!/usr/bin/env python3
"""
LogiTrack Desktop - Aplicación principal
Fase 4: Manejo de eventos, señales y asincronía
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
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence

from .workers import ShipmentWorker


class LogiTrackWindow(QMainWindow):
    """Ventana principal de LogiTrack Desktop - Fase 4"""

    def __init__(self):
        super().__init__()

        # Configuración básica
        self.setWindowTitle("LogiTrack Desktop")
        self.setMinimumSize(1000, 650)
        self.resize(1200, 750)

        # Datos en memoria
        self.shipments = []
        self.next_id = 1
        self.workers = []  # Lista de workers activos
        self.current_worker = None

        # Configurar UI
        self._setup_menu()
        self._setup_central_widget()
        self._setup_status_bar()
        self._setup_shortcuts()

        # Cargar datos de ejemplo de forma asíncrona
        self._load_initial_data()

    def _setup_menu(self):
        """Configura la barra de menú"""
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&Archivo")
        exit_action = QAction("&Salir", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        shipments_menu = menubar.addMenu("&Envíos")
        new_action = QAction("&Nuevo Envío", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._clear_form)
        shipments_menu.addAction(new_action)

        # Acción: Sincronizar (tarea larga)
        sync_action = QAction("&Sincronizar con API", self)
        sync_action.setShortcut("Ctrl+Shift+S")
        sync_action.triggered.connect(self._sync_with_api)
        shipments_menu.addAction(sync_action)

        help_menu = menubar.addMenu("&Ayuda")
        about_action = QAction("&Acerca de", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_central_widget(self):
        """Configura el widget central con layouts responsivos"""
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

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

        # Botón de carga asíncrona
        self.load_btn = QPushButton("🔄 Cargar Datos")
        self.load_btn.clicked.connect(self._load_shipments_async)
        self.load_btn.setMaximumWidth(120)

        title_layout.addWidget(table_title)
        title_layout.addStretch()
        title_layout.addWidget(self.load_btn)

        left_layout.addLayout(title_layout)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Destinatario", "Dirección", "Tipo", "Estado", "Fecha"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
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
            QGroupBox { font-weight: bold; font-size: 13px; padding-top: 15px; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0px 5px 0px 5px; }
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
            QPushButton { background-color: #28a745; color: white; font-weight: bold; border-radius: 4px; padding: 5px 15px; }
            QPushButton:hover { background-color: #218838; }
            QPushButton:disabled { background-color: #6c757d; }
        """)
        self.guardar_btn.clicked.connect(self._save_shipment_async)

        self.limpiar_btn = QPushButton("🧹 Limpiar")
        self.limpiar_btn.setMinimumHeight(35)
        self.limpiar_btn.setStyleSheet("""
            QPushButton { background-color: #6c757d; color: white; font-weight: bold; border-radius: 4px; padding: 5px 15px; }
            QPushButton:hover { background-color: #5a6268; }
        """)
        self.limpiar_btn.clicked.connect(self._clear_form)

        # Botón de cancelar
        self.cancelar_btn = QPushButton("⏹ Cancelar")
        self.cancelar_btn.setMinimumHeight(35)
        self.cancelar_btn.setStyleSheet("""
            QPushButton { background-color: #dc3545; color: white; font-weight: bold; border-radius: 4px; padding: 5px 15px; }
            QPushButton:hover { background-color: #c82333; }
            QPushButton:disabled { background-color: #6c757d; }
        """)
        self.cancelar_btn.setEnabled(False)
        self.cancelar_btn.clicked.connect(self._cancel_current_task)

        button_layout.addWidget(self.guardar_btn)
        button_layout.addWidget(self.limpiar_btn)
        button_layout.addWidget(self.cancelar_btn)
        form_layout.addLayout(button_layout, 4, 0, 1, 2)

        # Línea separadora
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
            font-size: 12px; color: #6c757d; padding: 8px;
            background-color: #f8f9fa; border-radius: 4px;
        """)
        right_layout.addWidget(self.counter_label)

        # Estado de la tarea
        self.task_status_label = QLabel("✅ Sin tareas en curso")
        self.task_status_label.setStyleSheet("font-size: 11px; color: #28a745; padding: 5px;")
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
        self.statusBar().showMessage("✅ Listo | Fase 4: Eventos y asincronía")

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

    # ============================================================
    # MÉTODOS ASÍNCRONOS
    # ============================================================

    def _load_initial_data(self):
        """Carga datos iniciales de forma asíncrona"""
        self._load_shipments_async()

    def _load_shipments_async(self):
        """Carga envíos en segundo plano"""
        # Limpiar tabla
        self.table.setRowCount(0)
        self.shipments.clear()

        # Crear y configurar worker
        worker = ShipmentWorker("load")
        self._setup_worker(worker)
        worker.signals.data.connect(self._on_shipments_loaded)
        worker.start()

    def _save_shipment_async(self):
        """Guarda un envío en segundo plano"""
        # Validar campos
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

        # Preparar datos
        data = {
            "destinatario": destinatario,
            "direccion": direccion,
            "tipo": tipo,
            "estado": estado
        }

        # Crear worker
        worker = ShipmentWorker("save", data)
        self._setup_worker(worker)
        worker.signals.data.connect(self._on_shipment_saved)
        worker.start()

    def _sync_with_api(self):
        """Sincroniza con API en segundo plano"""
        # Crear worker
        worker = ShipmentWorker("sync", {"timestamp": datetime.now().isoformat()})
        self._setup_worker(worker)
        worker.signals.data.connect(self._on_sync_complete)
        worker.start()

    def _setup_worker(self, worker):
        """Configura un worker con sus señales"""
        # Guardar referencia
        self.current_worker = worker
        self.workers.append(worker)

        # Conectar señales
        worker.signals.status.connect(self._on_task_status)
        worker.signals.progress.connect(self._on_task_progress)
        worker.signals.error.connect(self._on_task_error)
        worker.signals.finished.connect(self._on_task_finished)

        # Actualizar UI
        self._set_loading_state(True)

    # ============================================================
    # MÉTODOS DE RESPUESTA A SEÑALES
    # ============================================================

    def _on_shipments_loaded(self, shipments):
        """Recibe los envíos cargados"""
        if shipments:
            for shipment in shipments:
                self._add_shipment_to_table(
                    shipment.get("destinatario", ""),
                    shipment.get("direccion", ""),
                    shipment.get("tipo", "Paquete"),
                    shipment.get("estado", "Pendiente")
                )
            self._update_counter()
            self.statusBar().showMessage(f"✅ Cargados {len(shipments)} envíos", 3000)

    def _on_shipment_saved(self, result):
        """Recibe confirmación de guardado"""
        if result and result.get("status") == "success":
            data = result.get("data", {})
            self._add_shipment_to_table(
                data.get("destinatario", ""),
                data.get("direccion", ""),
                data.get("tipo", "Paquete"),
                data.get("estado", "Pendiente")
            )
            self._update_counter()
            self._clear_form()
            self.statusBar().showMessage("✅ Envío guardado correctamente", 3000)

    def _on_sync_complete(self, result):
        """Recibe resultado de sincronización"""
        if result and result.get("status") == "sync_complete":
            QMessageBox.information(
                self,
                "Sincronización Completa",
                f"✅ Se sincronizaron {result.get('synced', 0)} envíos correctamente."
            )
            self.statusBar().showMessage("✅ Sincronización completada", 3000)

    def _on_task_status(self, message):
        """Actualiza el estado de la tarea"""
        self.task_status_label.setText(f"⏳ {message}")
        self.statusBar().showMessage(f"⏳ {message}", 3000)

    def _on_task_progress(self, value):
        """Actualiza la barra de progreso"""
        self.progress_bar.setValue(value)
        self.progress_bar.show()

    def _on_task_error(self, error_msg):
        """Maneja errores de tareas"""
        QMessageBox.warning(self, "Error en tarea", f"❌ {error_msg}")
        self.task_status_label.setText(f"❌ Error: {error_msg}")
        self.task_status_label.setStyleSheet("font-size: 11px; color: #dc3545; padding: 5px;")

    def _on_task_finished(self):
        """Limpia el estado de la tarea"""
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        self._set_loading_state(False)
        self.task_status_label.setStyleSheet("font-size: 11px; color: #28a745; padding: 5px;")

    def _cancel_current_task(self):
        """Cancela la tarea actual"""
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.cancel()
            self.current_worker.wait()  # Esperar a que termine
            self.task_status_label.setText("⏹ Tarea cancelada")
            self.task_status_label.setStyleSheet("font-size: 11px; color: #ffc107; padding: 5px;")
            self._set_loading_state(False)
            self.statusBar().showMessage("⏹ Tarea cancelada", 3000)

    def _set_loading_state(self, loading):
        """Habilita/deshabilita la UI durante carga"""
        self.guardar_btn.setEnabled(not loading)
        self.load_btn.setEnabled(not loading)
        self.cancelar_btn.setEnabled(loading)

        if loading:
            self.task_status_label.setText("⏳ Procesando...")
            self.task_status_label.setStyleSheet("font-size: 11px; color: #17a2b8; padding: 5px;")
        else:
            self.task_status_label.setText("✅ Sin tareas en curso")
            self.task_status_label.setStyleSheet("font-size: 11px; color: #28a745; padding: 5px;")
            self.current_worker = None

    # ============================================================
    # MÉTODOS AUXILIARES (sincrónicos)
    # ============================================================

    def _load_sample_data(self):
        """Carga datos de ejemplo (sincrónico, para pruebas)"""
        sample_data = [
            ("María González", "Av. Principal 123", "Paquete", "Entregado"),
            ("Carlos Rodríguez", "Calle 45 #23", "Documento", "En ruta"),
            ("Ana Martínez", "Blvd. Norte 789", "Mercancía", "Pendiente"),
            ("Luis Pérez", "Calle Sur 456", "Carga", "Retrasado"),
        ]
        for destinatario, direccion, tipo, estado in sample_data:
            self._add_shipment_to_table(destinatario, direccion, tipo, estado)
        self._update_counter()

    def _add_shipment_to_table(self, destinatario, direccion, tipo, estado):
        """Añade un envío a la tabla"""
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
        self.table.setItem(row, 4, QTableWidgetItem(estado))
        self.table.setItem(row, 5, QTableWidgetItem(fecha))

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
        from PyQt6.QtGui import QColor
        hex_color = hex_color.lstrip("#")
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return QColor(r, g, b)

    def _clear_form(self):
        """Limpia el formulario"""
        self.destinatario_input.clear()
        self.direccion_input.clear()
        self.tipo_combo.setCurrentIndex(0)
        self.estado_combo.setCurrentIndex(0)
        self.destinatario_input.setFocus()
        self.statusBar().showMessage("🧹 Formulario limpiado", 2000)

    def _filter_table(self, text):
        """Filtra la tabla"""
        text = text.lower()
        for row in range(self.table.rowCount()):
            visible = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text in item.text().lower():
                    visible = True
                    break
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
            <p><b>Versión:</b> 0.4.0 (Fase 4)</p>
            <p><b>Framework:</b> PyQt6</p>
            <p><b>Características:</b></p>
            <ul>
                <li>⚡ Tareas asíncronas (QThread)</li>
                <li>📊 Barra de progreso</li>
                <li>⏹ Cancelación de tareas</li>
                <li>📐 Layouts responsivos</li>
            </ul>
            <hr>
            <p style="color: #7f8c8d; font-size: 10px;">
                🚀 Proyecto Integrador - Fase 4
            </p>
            """,
        )

    def closeEvent(self, event):
        """Maneja el cierre de la ventana"""
        # Cancelar tareas pendientes
        if self.current_worker and self.current_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Tarea en curso",
                "Hay una tarea en curso. ¿Deseas cancelarla y salir?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._cancel_current_task()
                event.accept()
            else:
                event.ignore()
            return

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

    window = LogiTrackWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()