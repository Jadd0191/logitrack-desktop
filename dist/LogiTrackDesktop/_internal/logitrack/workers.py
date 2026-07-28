#!/usr/bin/env python3
"""
LogiTrack Desktop - Workers para tareas en segundo plano
Fase 4: Manejo de eventos, señales y asincronía
"""

import time
import random
from PyQt6.QtCore import QThread, pyqtSignal, QObject


class WorkerSignals(QObject):
    """
    Define las señales que puede emitir un worker.
    """
    # Señal para enviar datos de vuelta a la UI
    data = pyqtSignal(object)
    # Señal para enviar mensajes de progreso
    progress = pyqtSignal(int)
    # Señal para mensajes de estado
    status = pyqtSignal(str)
    # Señal para indicar que el trabajo está completo
    finished = pyqtSignal()
    # Señal para enviar errores
    error = pyqtSignal(str)


class Worker(QThread):
    """
    Worker genérico para ejecutar tareas en segundo plano.
    Hereda de QThread para poder ejecutarse en un hilo separado.
    """

    def __init__(self, task_id, task_func, args=None, kwargs=None):
        super().__init__()
        self.task_id = task_id
        self.task_func = task_func
        self.args = args or []
        self.kwargs = kwargs or {}
        self._is_cancelled = False
        self.signals = WorkerSignals()

    def run(self):
        """
        Este método se ejecuta en el hilo separado.
        """
        try:
            # Emitir estado inicial
            self.signals.status.emit(f"Iniciando tarea {self.task_id}...")

            # Ejecutar la tarea con los argumentos
            result = self.task_func(*self.args, **self.kwargs)

            # Verificar si fue cancelada
            if self._is_cancelled:
                self.signals.status.emit(f"Tarea {self.task_id} cancelada")
                self.signals.finished.emit()
                return

            # Emitir el resultado
            self.signals.data.emit(result)
            self.signals.status.emit(f"Tarea {self.task_id} completada")
            self.signals.finished.emit()

        except Exception as e:
            # Emitir error si algo sale mal
            self.signals.error.emit(str(e))
            self.signals.finished.emit()

    def cancel(self):
        """
        Cancela la tarea en curso.
        """
        self._is_cancelled = True


class ShipmentWorker(Worker):
    """
    Worker especializado para operaciones de envíos.
    """

    def __init__(self, operation, data=None):
        """
        Args:
            operation: 'load', 'save', 'search', 'sync'
            data: Datos necesarios para la operación
        """
        super().__init__(
            task_id=f"shipment_{operation}",
            task_func=self._execute_operation,
            args=[operation, data]
        )
        self.operation = operation
        self.data = data

    def _execute_operation(self, operation, data):
        """
        Ejecuta la operación solicitada.
        """
        if operation == "load":
            return self._load_shipments(data)
        elif operation == "save":
            return self._save_shipment(data)
        elif operation == "search":
            return self._search_shipments(data)
        elif operation == "sync":
            return self._sync_with_api(data)
        else:
            raise ValueError(f"Operación desconocida: {operation}")

    def _load_shipments(self, data=None):
        """Simula carga de envíos desde la base de datos"""
        self.signals.status.emit("📊 Cargando envíos...")
        time.sleep(2)  # Simular trabajo

        # Simular algunos datos de ejemplo
        shipments = [
            {"id": 1, "destinatario": "María González", "estado": "Entregado"},
            {"id": 2, "destinatario": "Carlos Rodríguez", "estado": "En ruta"},
            {"id": 3, "destinatario": "Ana Martínez", "estado": "Pendiente"},
        ]

        # Emitir progreso
        for i in range(3):
            if self._is_cancelled:
                return None
            self.signals.progress.emit((i + 1) * 25)
            time.sleep(0.5)

        return shipments

    def _save_shipment(self, data):
        """Simula guardar un envío en la base de datos"""
        self.signals.status.emit("💾 Guardando envío...")
        time.sleep(1.5)  # Simular trabajo

        if self._is_cancelled:
            return None

        return {"status": "success", "data": data}

    def _search_shipments(self, query):
        """Simula búsqueda de envíos"""
        self.signals.status.emit(f"🔍 Buscando: '{query}'...")
        time.sleep(2)  # Simular trabajo

        if self._is_cancelled:
            return None

        # Simular resultados de búsqueda
        results = [
            {"id": 5, "destinatario": "Pedro Sánchez", "direccion": "Calle 123"},
            {"id": 8, "destinatario": "Laura Gómez", "direccion": "Av. Principal"},
        ]
        return results

    def _sync_with_api(self, data):
        """Simula sincronización con API externa"""
        self.signals.status.emit("🔄 Sincronizando con API...")
        total_steps = 5

        for i in range(total_steps):
            if self._is_cancelled:
                return None

            self.signals.progress.emit((i + 1) * (100 // total_steps))
            self.signals.status.emit(f"🔄 Sincronizando paso {i + 1}/{total_steps}...")
            time.sleep(0.8)  # Simular trabajo

        return {"status": "sync_complete", "synced": 10}