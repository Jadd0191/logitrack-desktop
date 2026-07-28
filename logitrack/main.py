#!/usr/bin/env python3
"""
LogiTrack Desktop - Aplicación principal
Fase 2: Ventana principal con widgets básicos
"""

import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QMessageBox,
    QStatusBar,
    QHeaderView,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence


class LogiTrackWindow(QMainWindow):
    """Ventana principal de LogiTrack Desktop"""

    def __init__(self):
        super().__init__()

        # Configuración básica
        self.setWindowTitle("LogiTrack Desktop")
        self.setMinimumSize(1200, 700)

        # Datos en memoria (temporal)
        self.shipments = []
        self.next_id = 1

        # Configurar UI
        self._setup_menu()
        self._setup_central_widget()
        self._setup_status_bar()
        self._setup_shortcuts()

        # Cargar datos de ejemplo
        self._load_sample_data()

    def _setup_menu(self):
        """Configura la barra de menú"""
        menubar = self.menuBar()

        # Menú Archivo
        file_menu = menubar.addMenu("&Archivo")
        exit_action = QAction("&Salir", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menú Envíos
        shipments_menu = menubar.addMenu("&Envíos")
        new_action = QAction("&Nuevo Envío", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._clear_form)
        shipments_menu.addAction(new_action)

        # Menú Ayuda
        help_menu = menubar.addMenu("&Ayuda")
        about_action = QAction("&Acerca de", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_central_widget(self):
        """Configura el widget central con tabla y formulario"""
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)

        # ===== PANEL IZQUIERDO: Tabla de envíos =====
        left_panel = QWidget()
        left_layout = QVBoxLayout()

        # Título de la tabla
        table_title = QLabel("📋 Lista de Envíos")
        table_title.setStyleSheet("font-size: 16px; font-weight: bold;")

        # Tabla de envíos
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Destinatario", "Dirección", "Tipo", "Estado", "Fecha"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)

        left_layout.addWidget(table_title)
        left_layout.addWidget(self.table)
        left_panel.setLayout(left_layout)

        # ===== PANEL DERECHO: Formulario de alta =====
        right_panel = QWidget()
        right_panel.setMaximumWidth(350)
        right_layout = QVBoxLayout()

        # Grupo del formulario
        form_group = QGroupBox("📝 Nuevo Envío")
        form_layout = QVBoxLayout()

        # Campo: Destinatario
        form_layout.addWidget(QLabel("Destinatario:"))
        self.destinatario_input = QLineEdit()
        self.destinatario_input.setPlaceholderText("Nombre del destinatario")
        form_layout.addWidget(self.destinatario_input)

        # Campo: Dirección
        form_layout.addWidget(QLabel("Dirección:"))
        self.direccion_input = QLineEdit()
        self.direccion_input.setPlaceholderText("Calle y número")
        form_layout.addWidget(self.direccion_input)

        # Campo: Tipo
        form_layout.addWidget(QLabel("Tipo de envío:"))
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Paquete", "Documento", "Carga", "Mercancía"])
        form_layout.addWidget(self.tipo_combo)

        # Campo: Estado
        form_layout.addWidget(QLabel("Estado:"))
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(["Pendiente", "En ruta", "Entregado", "Retrasado"])
        form_layout.addWidget(self.estado_combo)

        # Botones
        button_layout = QHBoxLayout()

        self.guardar_btn = QPushButton("💾 Guardar")
        self.guardar_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold;")
        self.guardar_btn.clicked.connect(self._save_shipment)

        self.limpiar_btn = QPushButton("🧹 Limpiar")
        self.limpiar_btn.clicked.connect(self._clear_form)

        button_layout.addWidget(self.guardar_btn)
        button_layout.addWidget(self.limpiar_btn)

        form_layout.addLayout(button_layout)

        # Campo de búsqueda
        form_layout.addWidget(QLabel("🔍 Buscar:"))
        self.buscar_input = QLineEdit()
        self.buscar_input.setPlaceholderText("Buscar envíos...")
        self.buscar_input.textChanged.connect(self._filter_table)
        form_layout.addWidget(self.buscar_input)

        form_group.setLayout(form_layout)
        right_layout.addWidget(form_group)

        # Contador de envíos
        self.counter_label = QLabel("Total de envíos: 0")
        self.counter_label.setStyleSheet("font-size: 12px; color: #6c757d; padding: 5px;")
        right_layout.addWidget(self.counter_label)

        right_layout.addStretch()
        right_panel.setLayout(right_layout)

        # ===== ARMAR LAYOUT PRINCIPAL =====
        main_layout.addWidget(left_panel, 7)   # 70% del espacio
        main_layout.addWidget(right_panel, 3)   # 30% del espacio

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def _setup_status_bar(self):
        """Configura la barra de estado"""
        self.statusBar().showMessage("✅ Listo | Fase 2: Widgets básicos")

    def _setup_shortcuts(self):
        """Configura atajos de teclado"""
        # Ctrl+N: Nuevo envío (limpiar formulario)
        new_shortcut = QAction("Nuevo", self)
        new_shortcut.setShortcut(QKeySequence.StandardKey.New)
        new_shortcut.triggered.connect(self._clear_form)
        self.addAction(new_shortcut)

        # Ctrl+S: Guardar
        save_shortcut = QAction("Guardar", self)
        save_shortcut.setShortcut(QKeySequence.StandardKey.Save)
        save_shortcut.triggered.connect(self._save_shipment)
        self.addAction(save_shortcut)

        # Esc: Limpiar
        esc_shortcut = QAction("Limpiar", self)
        esc_shortcut.setShortcut(QKeySequence.StandardKey.Cancel)
        esc_shortcut.triggered.connect(self._clear_form)
        self.addAction(esc_shortcut)

    def _load_sample_data(self):
        """Carga datos de ejemplo para la tabla"""
        sample_data = [
            ("María González", "Av. Principal 123", "Paquete", "Entregado"),
            ("Carlos Rodríguez", "Calle 45 #23", "Documento", "En ruta"),
            ("Ana Martínez", "Blvd. Norte 789", "Mercancía", "Pendiente"),
        ]
        for destinatario, direccion, tipo, estado in sample_data:
            self._add_shipment_to_table(destinatario, direccion, tipo, estado)

        self._update_counter()

    def _add_shipment_to_table(self, destinatario, direccion, tipo, estado):
        """Añade un envío a la tabla y a la lista en memoria"""
        shipment_id = self.next_id
        self.next_id += 1
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Guardar en memoria
        self.shipments.append({
            "id": shipment_id,
            "destinatario": destinatario,
            "direccion": direccion,
            "tipo": tipo,
            "estado": estado,
            "fecha": fecha
        })

        # Añadir a la tabla
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(str(shipment_id)))
        self.table.setItem(row, 1, QTableWidgetItem(destinatario))
        self.table.setItem(row, 2, QTableWidgetItem(direccion))
        self.table.setItem(row, 3, QTableWidgetItem(tipo))
        self.table.setItem(row, 4, QTableWidgetItem(estado))
        self.table.setItem(row, 5, QTableWidgetItem(fecha))

    def _save_shipment(self):
        """Guarda un nuevo envío desde el formulario"""
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

        # Añadir envío
        self._add_shipment_to_table(destinatario, direccion, tipo, estado)
        self._update_counter()
        self._clear_form()

        # Feedback
        self.statusBar().showMessage(f"✅ Envío #{self.next_id - 1} guardado correctamente", 3000)

    def _clear_form(self):
        """Limpia el formulario"""
        self.destinatario_input.clear()
        self.direccion_input.clear()
        self.tipo_combo.setCurrentIndex(0)
        self.estado_combo.setCurrentIndex(0)
        self.destinatario_input.setFocus()
        self.statusBar().showMessage("🧹 Formulario limpiado", 2000)

    def _filter_table(self, text):
        """Filtra la tabla según el texto de búsqueda"""
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
        """Actualiza el contador de envíos"""
        total = self.table.rowCount()
        visible = sum(1 for row in range(self.table.rowCount()) if not self.table.isRowHidden(row))
        self.counter_label.setText(f"Total de envíos: {total} | Visibles: {visible}")

    def _show_about(self):
        """Muestra el diálogo Acerca de"""
        QMessageBox.about(
            self,
            "Acerca de LogiTrack Desktop",
            """
            <h2>🚚 LogiTrack Desktop</h2>
            <p><b>Versión:</b> 0.2.0 (Fase 2)</p>
            <p><b>Framework:</b> PyQt6</p>
            <p><b>Descripción:</b> Estación de Control Logístico de Escritorio</p>
            <p><b>Características:</b></p>
            <ul>
                <li>📝 Registro de envíos</li>
                <li>📋 Tabla interactiva</li>
                <li>🔍 Búsqueda en tiempo real</li>
                <li>⌨️ Atajos de teclado</li>
            </ul>
            <hr>
            <p style="color: #7f8c8d; font-size: 10px;">
                🚀 Proyecto Integrador - Fase 2
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

    window = LogiTrackWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()