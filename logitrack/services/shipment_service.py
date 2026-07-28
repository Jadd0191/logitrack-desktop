#!/usr/bin/env python3
"""
LogiTrack Desktop - Servicio de Envíos
Fase 6: Arquitectura MVC/MVVM
"""

import sqlite3
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from ..models import Shipment, ShipmentStatus, ShipmentType


class ShipmentService:
    """
    Servicio para operaciones con envíos.
    Encapsula toda la lógica de negocio y acceso a datos.
    """

    def __init__(self, db_path: str = None):
        """Inicializa el servicio con la ruta de la base de datos"""
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "logitrack.db"
            db_path.parent.mkdir(exist_ok=True)
        
        self.db_path = str(db_path)
        self._init_database()
        self._shipments: List[Shipment] = []
        self._next_id = 1

    def _init_database(self):
        """Inicializa la base de datos SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shipments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                destinatario TEXT NOT NULL,
                direccion TEXT NOT NULL,
                tipo TEXT NOT NULL,
                estado TEXT NOT NULL,
                fecha TEXT NOT NULL,
                observaciones TEXT,
                tracking_id TEXT
            )
        """)
        
        conn.commit()
        conn.close()

    def get_all(self) -> List[Shipment]:
        """Obtiene todos los envíos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, destinatario, direccion, tipo, estado, fecha, observaciones, tracking_id
            FROM shipments
            ORDER BY id DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            Shipment(
                id=row[0],
                destinatario=row[1],
                direccion=row[2],
                tipo=row[3],
                estado=row[4],
                fecha=row[5],
                observaciones=row[6],
                tracking_id=row[7],
            )
            for row in rows
        ]

    def get_by_id(self, shipment_id: int) -> Optional[Shipment]:
        """Obtiene un envío por su ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, destinatario, direccion, tipo, estado, fecha, observaciones, tracking_id
            FROM shipments
            WHERE id = ?
        """, (shipment_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Shipment(
                id=row[0],
                destinatario=row[1],
                direccion=row[2],
                tipo=row[3],
                estado=row[4],
                fecha=row[5],
                observaciones=row[6],
                tracking_id=row[7],
            )
        return None

    def create(self, shipment_data: Dict[str, Any]) -> Shipment:
        """Crea un nuevo envío"""
        # Validar datos
        if not shipment_data.get("destinatario"):
            raise ValueError("El destinatario es obligatorio")
        if not shipment_data.get("direccion"):
            raise ValueError("La dirección es obligatoria")
        
        # Crear el envío (sin ID todavía)
        shipment = Shipment(
            id=0,  # Temporal, se asignará en la BD
            destinatario=shipment_data["destinatario"],
            direccion=shipment_data["direccion"],
            tipo=shipment_data.get("tipo", "Paquete"),
            estado=shipment_data.get("estado", "Pendiente"),
            fecha=datetime.now().strftime("%Y-%m-%d %H:%M"),
            observaciones=shipment_data.get("observaciones"),
            tracking_id=shipment_data.get("tracking_id"),
        )
        
        # Guardar en BD
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO shipments (destinatario, direccion, tipo, estado, fecha, observaciones, tracking_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            shipment.destinatario,
            shipment.direccion,
            shipment.tipo,
            shipment.estado,
            shipment.fecha,
            shipment.observaciones,
            shipment.tracking_id,
        ))
        
        shipment.id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return shipment

    def update(self, shipment_id: int, data: Dict[str, Any]) -> Optional[Shipment]:
        """Actualiza un envío existente"""
        # Verificar que existe
        existing = self.get_by_id(shipment_id)
        if not existing:
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Construir query de actualización
        fields = []
        values = []
        
        for key, value in data.items():
            if key in ["destinatario", "direccion", "tipo", "estado", "observaciones", "tracking_id"]:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            conn.close()
            return existing
        
        values.append(shipment_id)
        query = f"UPDATE shipments SET {', '.join(fields)} WHERE id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        
        return self.get_by_id(shipment_id)

    def delete(self, shipment_id: int) -> bool:
        """Elimina un envío"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM shipments WHERE id = ?", (shipment_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted

    def get_stats(self) -> Dict[str, int]:
        """Obtiene estadísticas de envíos"""
        shipments = self.get_all()
        
        stats = {
            "total": len(shipments),
            "pendientes": 0,
            "en_ruta": 0,
            "entregados": 0,
            "retrasados": 0,
        }
        
        for shipment in shipments:
            if shipment.estado == ShipmentStatus.PENDIENTE:
                stats["pendientes"] += 1
            elif shipment.estado == ShipmentStatus.EN_RUTA:
                stats["en_ruta"] += 1
            elif shipment.estado == ShipmentStatus.ENTREGADO:
                stats["entregados"] += 1
            elif shipment.estado == ShipmentStatus.RETRASADO:
                stats["retrasados"] += 1
        
        return stats

    def search(self, query: str) -> List[Shipment]:
        """Busca envíos por texto"""
        all_shipments = self.get_all()
        query_lower = query.lower()
        
        results = []
        for shipment in all_shipments:
            if (query_lower in shipment.destinatario.lower() or
                query_lower in shipment.direccion.lower() or
                query_lower in shipment.tipo.lower() or
                query_lower in shipment.estado.lower()):
                results.append(shipment)
        
        return results

    def filter_by_status(self, status: str) -> List[Shipment]:
        """Filtra envíos por estado"""
        if not status:
            return self.get_all()
        
        all_shipments = self.get_all()
        return [s for s in all_shipments if s.estado == status]