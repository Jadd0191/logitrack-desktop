#!/usr/bin/env python3
"""
LogiTrack Desktop - Controlador de Envíos
Fase 7: Integración de datos: BBDD y API
"""

from typing import List, Dict, Any, Optional
from PyQt6.QtCore import QObject, pyqtSignal  # ✅ Importación correcta

from ..models import Shipment, ShipmentStatus
from ..services import ShipmentService


class ShipmentController(QObject):
    """
    Controlador para operaciones de envíos.
    Orquesta la comunicación entre la vista y el servicio.
    """
    
    # Señales para comunicación con la vista
    shipments_loaded = pyqtSignal(list)
    shipment_saved = pyqtSignal(object)
    shipment_updated = pyqtSignal(object)
    shipment_deleted = pyqtSignal(int)
    stats_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    sync_complete = pyqtSignal(dict)
    api_status_changed = pyqtSignal(bool)
    
    def __init__(self, service: ShipmentService):
        super().__init__()
        self._service = service
        self._current_shipments: List[Shipment] = []

    def load_shipments(self) -> List[Shipment]:
        """Carga todos los envíos"""
        try:
            self._current_shipments = self._service.get_all()
            self.shipments_loaded.emit(self._current_shipments)
            self._update_stats()
            return self._current_shipments
        except Exception as e:
            self.error_occurred.emit(f"Error al cargar envíos: {str(e)}")
            return []

    def save_shipment(self, data: Dict[str, Any]) -> Optional[Shipment]:
        """Guarda un nuevo envío"""
        try:
            # Validar datos
            if not data.get("destinatario"):
                self.error_occurred.emit("El destinatario es obligatorio")
                return None
            if not data.get("direccion"):
                self.error_occurred.emit("La dirección es obligatoria")
                return None
            
            # Guardar
            shipment = self._service.create(data)
            self._current_shipments.insert(0, shipment)
            self.shipment_saved.emit(shipment)
            self._update_stats()
            return shipment
        except Exception as e:
            self.error_occurred.emit(f"Error al guardar envío: {str(e)}")
            return None

    def update_shipment(self, shipment_id: int, data: Dict[str, Any]) -> Optional[Shipment]:
        """Actualiza un envío existente"""
        try:
            shipment = self._service.update(shipment_id, data)
            if shipment:
                # Actualizar en la lista local
                for i, s in enumerate(self._current_shipments):
                    if s.id == shipment_id:
                        self._current_shipments[i] = shipment
                        break
                self.shipment_updated.emit(shipment)
                self._update_stats()
            return shipment
        except Exception as e:
            self.error_occurred.emit(f"Error al actualizar envío: {str(e)}")
            return None

    def delete_shipment(self, shipment_id: int) -> bool:
        """Elimina un envío"""
        try:
            success = self._service.delete(shipment_id)
            if success:
                self._current_shipments = [s for s in self._current_shipments if s.id != shipment_id]
                self.shipment_deleted.emit(shipment_id)
                self._update_stats()
            return success
        except Exception as e:
            self.error_occurred.emit(f"Error al eliminar envío: {str(e)}")
            return False

    def search_shipments(self, query: str) -> List[Shipment]:
        """Busca envíos por texto"""
        try:
            if not query:
                return self._current_shipments
            results = self._service.search(query)
            return results
        except Exception as e:
            self.error_occurred.emit(f"Error al buscar envíos: {str(e)}")
            return []

    def filter_by_status(self, status: str) -> List[Shipment]:
        """Filtra envíos por estado"""
        try:
            if not status:
                return self._current_shipments
            results = self._service.filter_by_status(status)
            return results
        except Exception as e:
            self.error_occurred.emit(f"Error al filtrar envíos: {str(e)}")
            return []

    def get_shipment(self, shipment_id: int) -> Optional[Shipment]:
        """Obtiene un envío por su ID"""
        try:
            return self._service.get_by_id(shipment_id)
        except Exception as e:
            self.error_occurred.emit(f"Error al obtener envío: {str(e)}")
            return None

    def get_stats(self) -> Dict[str, int]:
        """Obtiene estadísticas"""
        try:
            return self._service.get_stats()
        except Exception as e:
            self.error_occurred.emit(f"Error al obtener estadísticas: {str(e)}")
            return {}

    def sync_with_api(self) -> Dict[str, Any]:
        """Sincroniza con la API central"""
        try:
            result = self._service.sync_with_api()
            self.sync_complete.emit(result)
            return result
        except Exception as e:
            self.error_occurred.emit(f"Error al sincronizar: {str(e)}")
            return {"status": "error", "message": str(e)}

    def get_sync_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtiene logs de sincronización"""
        try:
            return self._service.get_sync_logs(limit)
        except Exception as e:
            self.error_occurred.emit(f"Error al obtener logs: {str(e)}")
            return []

    def set_online_status(self, is_online: bool):
        """Cambia el estado de conexión"""
        self._service.set_online_status(is_online)
        self.api_status_changed.emit(is_online)

    def is_api_online(self) -> bool:
        """Verifica estado de la API"""
        return self._service.is_api_online()

    def _update_stats(self):
        """Actualiza y emite las estadísticas"""
        stats = self.get_stats()
        self.stats_updated.emit(stats)