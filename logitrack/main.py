#!/usr/bin/env python3
"""
LogiTrack Desktop - Aplicación principal
Fase 3: Gestión de geometría y layouts responsivos
"""

import sys
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
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QKeySequence


class LogiTrackWindow(QMainWindow):
    """Ventana principal de LogiTrack Desktop - Fase 3"""

    def __init__(self):
        super().__init__()

        # Configuración básica
        self.setWindowTitle("LogiTrack Desktop")
        self.setMinimumSize(1000, 650)
        self.resize(1200, 750)

        # Datos en memoria
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

        help_menu = menubar.addMenu("&Ayuda")
        about_action = QAction("&Acerca de", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_central_widget(self):
        """Configura el widget central con layouts responsivos"""
        central_widget = QWidget()
        
        # Layout principal - Vertical
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # ===== SPLITTER: Tabla (izquierda) + Formulario (derecha) =====
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(5)
        splitter.setChildrenCollapsible(False)

        # --- Panel izquierdo: Tabla ---
        left_widget = QWidget()
        left_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(8)
        left_layout.setContentsMargins(5, 5, 5, 5)

        # Título de la tabla
        table_title = QLabel("📋 Lista de Envíos")
        table_title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 5px 0px;
        """)
        left_layout.addWidget(table_title)

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
        
        # Layout interno del grupo - Grid para mejor alineación
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(10)
        form_layout.setHorizontalSpacing(8)
        form_layout.setContentsMargins(15, 20, 15, 15)

        # Fila 0: Destinatario
        form_layout.addWidget(QLabel("Destinatario:"), 0, 0)
        self.destinatario_input = QLineEdit()
        self.destinatario_input.setPlaceholderText("Nombre completo")
        self.destinatario_input.setMinimumHeight(30)
        form_layout.addWidget(self.destinatario_input, 0, 1)

        # Fila 1: Dirección
        form_layout.addWidget(QLabel("Dirección:"), 1, 0)
        self.direccion_input = QLineEdit()
        self.direccion_input.setPlaceholderText("Calle y número")
        self.direccion_input.setMinimumHeight(30)
        form_layout.addWidget(self.direccion_input, 1, 1)

        # Fila 2: Tipo
        form_layout.addWidget(QLabel("Tipo:"), 2, 0)
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Paquete", "Documento", "Carga", "Mercancía"])
        self.tipo_combo.setMinimumHeight(30)
        form_layout.addWidget(self.tipo_combo, 2, 1)

        # Fila 3: Estado
        form_layout.addWidget(QLabel("Estado:"), 3, 0)
        self.estado_combo = QComboBox()
        self.estado_combo.addItems(["Pendiente", "En ruta", "Entregado", "Retrasado"])
        self.estado_combo.setMinimumHeight(30)
        form_layout.addWidget(self.estado_combo, 3, 1)

        # Fila 4: Botones (ocupan 2 columnas)
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
        self.guardar_btn.clicked.connect(self._save_shipment)

        self.limpiar_btn = QPushButton("🧹 Limpiar")
        self.limpiar_btn.setMinimumHeight(35)
        self.limpiar_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.limpiar_btn.clicked.connect(self._clear_form)

        button_layout.addWidget(self.guardar_btn)
        button_layout.addWidget(self.limpiar_btn)
        form_layout.addLayout(button_layout, 4, 0, 1, 2)

        # Fila 5: Línea separadora
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        form_layout.addWidget(separator, 5, 0, 1, 2)

        # Fila 6: Búsqueda
        form_layout.addWidget(QLabel("🔍 Buscar:"), 6, 0)
        self.buscar_input = QLineEdit()
        self.buscar_input.setPlaceholderText("Buscar envíos...")
        self.buscar_input.setMinimumHeight(30)
        self.buscar_input.textChanged.connect(self._filter_table)
        form_layout.addWidget(self.buscar_input, 6, 1)

        form_group.setLayout(form_layout)
        right_layout.addWidget(form_group)

        # Contador de envíos
        self.counter_label = QLabel("📊 Total: 0 envíos")
        self.counter_label.setStyleSheet("""
            font-size: 12px;
            color: #6c757d;
            padding: 8px;
            background-color: #f8f9fa;
            border-radius: 4px;
        """)
        right_layout.addWidget(self.counter_label)

        right_layout.addStretch()

        # --- Agregar widgets al splitter ---
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([700, 300])  # Proporción 70/30

        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def _setup_status_bar(self):
        """Configura la barra de estado"""
        self.statusBar().showMessage("✅ Listo | Fase 3: Layouts responsivos")

    def _setup_shortcuts(self):
        """Configura atajos de teclado"""
        new_shortcut = QAction("Nuevo", self)
        new_shortcut.setShortcut(QKeySequence.StandardKey.New)
        new_shortcut.triggered.connect(self._clear_form)
        self.addAction(new_shortcut)

        save_shortcut = QAction("Guardar", self)
        save_shortcut.setShortcut(QKeySequence.StandardKey.Save)
        save_shortcut.triggered.connect(self._save_shipment)
        self.addAction(save_shortcut)

        esc_shortcut = QAction("Limpiar", self)
        esc_shortcut.setShortcut(QKeySequence.StandardKey.Cancel)
        esc_shortcut.triggered.connect(self._clear_form)
        self.addAction(esc_shortcut)

    def _load_sample_data(self):
        """Carga datos de ejemplo"""
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

        # Colorear estado
        self._color_status_cell(row)

    def _color_status_cell(self, row):
        """Colorea la celda de estado según su valor"""
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
            
            # Texto blanco para fondos oscuros
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

    def _save_shipment(self):
        """Guarda un nuevo envío"""
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

        self._add_shipment_to_table(destinatario, direccion, tipo, estado)
        self._update_counter()
        self._clear_form()
        self.statusBar().showMessage(f"✅ Envío #{self.next_id - 1} guardado", 3000)

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
        self.counter_label.setText(f"📊 Total: {total} envíos | Visibles: {visible}")

    def _show_about(self):
        """Diálogo Acerca de"""
        QMessageBox.about(
            self,
            "Acerca de LogiTrack Desktop",
            """
            <h2>🚚 LogiTrack Desktop</h2>
            <p><b>Versión:</b> 0.3.0 (Fase 3)</p>
            <p><b>Framework:</b> PyQt6</p>
            <p><b>Características:</b></p>
            <ul>
                <li>📐 Layouts responsivos</li>
                <li>📋 Tabla con colores por estado</li>
                <li>📝 Formulario con grid layout</li>
                <li>🔍 Búsqueda en tiempo real</li>
            </ul>
            <hr>
            <p style="color: #7f8c8d; font-size: 10px;">
                🚀 Proyecto Integrador - Fase 3
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