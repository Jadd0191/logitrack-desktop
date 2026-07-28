#!/usr/bin/env python3
"""
LogiTrack Desktop - Modelo de Envío
Fase 6: Arquitectura MVC/MVVM
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import json


@dataclass
class Shipment:
    """
    Modelo de datos para un envío.
    Contiene toda la información de un envío y métodos de validación.
    """
    id: int
    destinatario: str
    direccion: str
    tipo: str
    estado: str
    fecha: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    observaciones: Optional[str] = None
    tracking_id: Optional[str] = None

    def __post_init__(self):
        """Validaciones después de la inicialización"""
        self._validate()

    def _validate(self):
        """Valida los campos del envío"""
        if not self.destinatario or not self.destinatario.strip():
            raise ValueError("El destinatario es obligatorio")
        if not self.direccion or not self.direccion.strip():
            raise ValueError("La dirección es obligatoria")
        if self.tipo not in ["Paquete", "Documento", "Carga", "Mercancía"]:
            raise ValueError(f"Tipo de envío inválido: {self.tipo}")
        if self.estado not in ["Pendiente", "En ruta", "Entregado", "Retrasado"]:
            raise ValueError(f"Estado inválido: {self.estado}")

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario"""
        return {
            "id": self.id,
            "destinatario": self.destinatario,
            "direccion": self.direccion,
            "tipo": self.tipo,
            "estado": self.estado,
            "fecha": self.fecha,
            "observaciones": self.observaciones,
            "tracking_id": self.tracking_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Shipment":
        """Crea un Shipment desde un diccionario"""
        return cls(
            id=data.get("id", 0),
            destinatario=data.get("destinatario", ""),
            direccion=data.get("direccion", ""),
            tipo=data.get("tipo", "Paquete"),
            estado=data.get("estado", "Pendiente"),
            fecha=data.get("fecha", datetime.now().strftime("%Y-%m-%d %H:%M")),
            observaciones=data.get("observaciones"),
            tracking_id=data.get("tracking_id"),
        )

    def to_json(self) -> str:
        """Serializa el modelo a JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "Shipment":
        """Deserializa desde JSON"""
        data = json.loads(json_str)
        return cls.from_dict(data)


class ShipmentStatus:
    """Constantes para los estados de envío"""
    PENDIENTE = "Pendiente"
    EN_RUTA = "En ruta"
    ENTREGADO = "Entregado"
    RETRASADO = "Retrasado"

    @classmethod
    def all(cls) -> List[str]:
        """Lista todos los estados disponibles"""
        return [cls.PENDIENTE, cls.EN_RUTA, cls.ENTREGADO, cls.RETRASADO]

    @classmethod
    def get_color(cls, status: str) -> str:
        """Obtiene el color asociado a un estado"""
        colors = {
            cls.PENDIENTE: "#17a2b8",
            cls.EN_RUTA: "#ffc107",
            cls.ENTREGADO: "#28a745",
            cls.RETRASADO: "#dc3545",
        }
        return colors.get(status, "#6c757d")


class ShipmentType:
    """Constantes para los tipos de envío"""
    PAQUETE = "Paquete"
    DOCUMENTO = "Documento"
    CARGA = "Carga"
    MERCANCIA = "Mercancía"

    @classmethod
    def all(cls) -> List[str]:
        """Lista todos los tipos disponibles"""
        return [cls.PAQUETE, cls.DOCUMENTO, cls.CARGA, cls.MERCANCIA]