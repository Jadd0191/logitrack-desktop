#!/usr/bin/env python3
"""
LogiTrack Desktop - Servicio de Envíos
Fase 7: Integración de datos: BBDD y API
"""

import sqlite3
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from ..models import Shipment, ShipmentStatus, ShipmentType
from .api_client import RouteApiClient


class ShipmentService:
    """
    Servicio para operaciones con envíos.
    Encapsula toda la lógica de negocio y acceso a datos.
    """

    def __init__(self, db_path: str = None, api_client: RouteApiClient = None):
        """Inicializa el servicio con la ruta de la base de datos"""
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "logitrack.db"
            db_path.parent.mkdir(exist_ok=True)

        self.db_path = str(db_path)
        self.api_client = api_client or RouteApiClient()
        self._init_database()

    def _init_database(self):
        """Inicializa la base de datos SQLite con migraciones"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tabla principal de envíos (con campos nuevos para API)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shipments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                destinatario TEXT NOT NULL,
                direccion TEXT NOT NULL,
                tipo TEXT NOT NULL,
                estado TEXT NOT NULL,
                fecha TEXT NOT NULL,
                observaciones TEXT,
                tracking_id TEXT,
                distancia_km REAL,
                tiempo_estimado TEXT,
                clima TEXT,
                zona TEXT,
                api_data TEXT
            )
        """)

        # Tabla de logs de sincronización
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shipment_id INTEGER,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT,
                FOREIGN KEY (shipment_id) REFERENCES shipments (id)
            )
        """)

        # Verificar si hay columnas nuevas y agregarlas si no existen
        cursor.execute("PRAGMA table_info(shipments)")
        columns = [row[1] for row in cursor.fetchall()]

        new_columns = {
            "distancia_km": "REAL",
            "tiempo_estimado": "TEXT",
            "clima": "TEXT",
            "zona": "TEXT",
            "api_data": "TEXT",
        }

        for col_name, col_type in new_columns.items():
            if col_name not in columns:
                cursor.execute(f"ALTER TABLE shipments ADD COLUMN {col_name} {col_type}")

        conn.commit()
        conn.close()

    # ============================================================
    # MÉTODOS CRUD BÁSICOS
    # ============================================================

    def get_all(self) -> List[Shipment]:
        """Obtiene todos los envíos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, destinatario, direccion, tipo, estado, fecha,
                   observaciones, tracking_id, distancia_km, tiempo_estimado,
                   clima, zona, api_data
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
                distancia_km=row[8],
                tiempo_estimado=row[9],
                clima=row[10],
                zona=row[11],
                api_data=json.loads(row[12]) if row[12] else {},
            )
            for row in rows
        ]

    def get_by_id(self, shipment_id: int) -> Optional[Shipment]:
        """Obtiene un envío por su ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, destinatario, direccion, tipo, estado, fecha,
                   observaciones, tracking_id, distancia_km, tiempo_estimado,
                   clima, zona, api_data
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
                distancia_km=row[8],
                tiempo_estimado=row[9],
                clima=row[10],
                zona=row[11],
                api_data=json.loads(row[12]) if row[12] else {},
            )
        return None

    def create(self, shipment_data: Dict[str, Any]) -> Shipment:
        """Crea un nuevo envío con enriquecimiento de API"""
        # Validar datos básicos
        if not shipment_data.get("destinatario"):
            raise ValueError("El destinatario es obligatorio")
        if not shipment_data.get("direccion"):
            raise ValueError("La dirección es obligatoria")

        # Enriquecer con API
        address = shipment_data.get("direccion", "")
        enriched_data = self.api_client.enrich_shipment(
            address,
            shipment_data
        )

        # Crear el envío
        shipment = Shipment(
            id=0,
            destinatario=enriched_data["destinatario"],
            direccion=enriched_data["direccion"],
            tipo=enriched_data.get("tipo", "Paquete"),
            estado=enriched_data.get("estado", "Pendiente"),
            fecha=datetime.now().strftime("%Y-%m-%d %H:%M"),
            observaciones=enriched_data.get("observaciones"),
            tracking_id=enriched_data.get("tracking_id"),
            distancia_km=enriched_data.get("distancia_km"),
            tiempo_estimado=enriched_data.get("tiempo_estimado"),
            clima=enriched_data.get("clima"),
            zona=enriched_data.get("zona"),
            api_data=enriched_data.get("api_data", {}),
        )

        # Guardar en BD
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO shipments (
                destinatario, direccion, tipo, estado, fecha,
                observaciones, tracking_id, distancia_km, tiempo_estimado,
                clima, zona, api_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            shipment.destinatario,
            shipment.direccion,
            shipment.tipo,
            shipment.estado,
            shipment.fecha,
            shipment.observaciones,
            shipment.tracking_id,
            shipment.distancia_km,
            shipment.tiempo_estimado,
            shipment.clima,
            shipment.zona,
            json.dumps(shipment.api_data),
        ))

        shipment.id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Registrar en log
        self._log_sync(shipment.id, "create", "success")

        return shipment

    def update(self, shipment_id: int, data: Dict[str, Any]) -> Optional[Shipment]:
        """Actualiza un envío existente"""
        existing = self.get_by_id(shipment_id)
        if not existing:
            return None

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Construir query de actualización
        fields = []
        values = []

        for key, value in data.items():
            if key in ["destinatario", "direccion", "tipo", "estado", "observaciones"]:
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

        self._log_sync(shipment_id, "update", "success")
        return self.get_by_id(shipment_id)

    def delete(self, shipment_id: int) -> bool:
        """Elimina un envío"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM shipments WHERE id = ?", (shipment_id,))
        deleted = cursor.rowcount > 0

        if deleted:
            self._log_sync(shipment_id, "delete", "success")

        conn.commit()
        conn.close()

        return deleted

    # ============================================================
    # MÉTODOS DE BÚSQUEDA Y FILTROS
    # ============================================================

    def search(self, query: str) -> List[Shipment]:
        """Busca envíos por texto"""
        all_shipments = self.get_all()
        query_lower = query.lower()

        results = []
        for shipment in all_shipments:
            if (query_lower in shipment.destinatario.lower() or
                query_lower in shipment.direccion.lower() or
                query_lower in shipment.tipo.lower() or
                query_lower in shipment.estado.lower() or
                (shipment.tracking_id and query_lower in shipment.tracking_id.lower())):
                results.append(shipment)

        return results

    def filter_by_status(self, status: str) -> List[Shipment]:
        """Filtra envíos por estado"""
        if not status:
            return self.get_all()

        all_shipments = self.get_all()
        return [s for s in all_shipments if s.estado == status]

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

    # ============================================================
    # SINCROZACIÓN Y LOGS
    # ============================================================

    def _log_sync(self, shipment_id: int, action: str, status: str, details: str = None):
        """Registra una operación de sincronización"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sync_logs (shipment_id, action, timestamp, status, details)
            VALUES (?, ?, ?, ?, ?)
        """, (
            shipment_id,
            action,
            datetime.now().isoformat(),
            status,
            details,
        ))

        conn.commit()
        conn.close()

    def get_sync_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtiene los logs de sincronización"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, shipment_id, action, timestamp, status, details
            FROM sync_logs
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "shipment_id": row[1],
                "action": row[2],
                "timestamp": row[3],
                "status": row[4],
                "details": row[5],
            }
            for row in rows
        ]

    def sync_with_api(self) -> Dict[str, Any]:
        """
        Simula sincronización con API central.
        En producción, enviaría datos a un servidor.
        """
        shipments = self.get_all()
        synced_count = len(shipments)

        for shipment in shipments:
            self._log_sync(
                shipment.id,
                "sync",
                "success",
                f"Synced shipment #{shipment.id}"
            )

        return {
            "status": "sync_complete",
            "synced": synced_count,
            "timestamp": datetime.now().isoformat(),
        }

    def set_online_status(self, is_online: bool):
        """Establece el estado de conexión de la API"""
        self.api_client.set_online_status(is_online)

    def is_api_online(self) -> bool:
        """Verifica si la API está online"""
        return self.api_client.is_online()