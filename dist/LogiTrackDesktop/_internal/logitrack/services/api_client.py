#!/usr/bin/env python3
"""
LogiTrack Desktop - Cliente API
Fase 7: Integración de datos: BBDD y API
"""

import json
import time
import random
from typing import Dict, Any, Optional, List
from datetime import datetime
import sqlite3
from pathlib import Path


class RouteApiClient:
    """
    Cliente para consumir API de enrutamiento.
    Simula una API real para desarrollo con caché en SQLite.
    """

    def __init__(self, cache_db_path: str = None):
        if cache_db_path is None:
            cache_db_path = Path(__file__).parent.parent / "data" / "api_cache.db"
            cache_db_path.parent.mkdir(exist_ok=True)

        self.cache_db_path = str(cache_db_path)
        self._init_cache_db()
        self._is_online = True

    def _init_cache_db(self):
        """Inicializa la base de datos de caché"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS route_cache (
                address TEXT PRIMARY KEY,
                data TEXT,
                timestamp TEXT,
                expires_at TEXT
            )
        """)

        conn.commit()
        conn.close()

    def set_online_status(self, is_online: bool):
        """Establece el estado de conexión"""
        self._is_online = is_online

    def is_online(self) -> bool:
        """Verifica si hay conexión"""
        return self._is_online

    def get_route_info(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de ruta para una dirección.
        Primero busca en caché, si no, llama a la API simulada.
        """
        # Buscar en caché
        cached = self._get_from_cache(address)
        if cached:
            return cached

        # Si no está en caché y estamos offline, devolver None
        if not self._is_online:
            return None

        # Llamar a la API simulada
        try:
            result = self._call_mock_api(address)
            # Guardar en caché
            self._save_to_cache(address, result)
            return result
        except Exception as e:
            # Si falla la API, devolver None
            return None

    def _get_from_cache(self, address: str) -> Optional[Dict[str, Any]]:
        """Obtiene datos de la caché"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT data, expires_at FROM route_cache WHERE address = ?",
            (address.lower().strip(),)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            data = json.loads(row[0])
            expires_at = row[1]

            # Verificar si el caché expiró (24 horas)
            if expires_at and datetime.now().isoformat() < expires_at:
                return data

        return None

    def _save_to_cache(self, address: str, data: Dict[str, Any]):
        """Guarda datos en caché"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()

        # Expira en 24 horas
        from datetime import timedelta
        expires_at = (datetime.now() + timedelta(hours=24)).isoformat()

        cursor.execute("""
            INSERT OR REPLACE INTO route_cache (address, data, timestamp, expires_at)
            VALUES (?, ?, ?, ?)
        """, (
            address.lower().strip(),
            json.dumps(data),
            datetime.now().isoformat(),
            expires_at
        ))

        conn.commit()
        conn.close()

    def _call_mock_api(self, address: str) -> Dict[str, Any]:
        """
        Simula una llamada a API real.
        En producción, aquí iría una llamada a httpx/requests.
        """
        # Simular latencia de red
        time.sleep(0.5 + random.random() * 0.5)

        # Datos simulados según la dirección
        address_hash = hash(address) % 10

        # Simular diferentes zonas
        zonas = ["Urbana", "Rural", "Industrial", "Comercial", "Residencial"]
        climas = ["Despejado", "Nublado", "Lluvia ligera", "Soleado", "Viento"]

        # Calcular distancia simulada (entre 1 y 50 km)
        distancia = round(1 + (address_hash * 2.5 + random.random() * 5), 1)

        # Tiempo estimado (minutos)
        tiempo = round(distancia * 1.5 + 5 + random.random() * 10)

        # Generar tracking ID simulado
        tracking_id = f"LT-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

        # Zona según hash
        zona = zonas[address_hash % len(zonas)]
        clima = climas[(address_hash + 3) % len(climas)]

        return {
            "distancia_km": distancia,
            "tiempo_estimado": f"{tiempo} min",
            "zona": zona,
            "clima": clima,
            "tracking_id": tracking_id,
            "coordenadas": {
                "lat": -33.4 + random.random() * 0.1,
                "lng": -70.6 + random.random() * 0.1,
            },
            "timestamp": datetime.now().isoformat(),
            "source": "mock_api",
        }

    def enrich_shipment(self, address: str, current_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriquece los datos de un envío con información de la API.
        """
        route_info = self.get_route_info(address)

        if route_info:
            # Solo añadir campos que no estén ya definidos
            result = current_data.copy()
            result["distancia_km"] = route_info.get("distancia_km")
            result["tiempo_estimado"] = route_info.get("tiempo_estimado")
            result["zona"] = route_info.get("zona")
            result["clima"] = route_info.get("clima")
            result["tracking_id"] = route_info.get("tracking_id")
            result["api_data"] = route_info
            return result

        return current_data