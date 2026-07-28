# 06 - Integración de Datos: BBDD y API - Fase 7

## Esquema de Base de Datos

### Tabla: shipments
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | PK, autoincrement |
| destinatario | TEXT | Nombre del destinatario |
| direccion | TEXT | Dirección de entrega |
| tipo | TEXT | Tipo de envío |
| estado | TEXT | Estado actual |
| fecha | TEXT | Fecha de registro |
| observaciones | TEXT | Notas adicionales |
| tracking_id | TEXT | ID de seguimiento |
| distancia_km | REAL | Distancia estimada |
| tiempo_estimado | TEXT | Tiempo estimado |
| clima | TEXT | Clima en la zona |
| zona | TEXT | Zona de entrega |
| api_data | TEXT | Datos crudos de API (JSON) |

### Tabla: sync_logs
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | PK, autoincrement |
| shipment_id | INTEGER | FK a shipments |
| action | TEXT | Acción realizada |
| timestamp | TEXT | Fecha y hora |
| status | TEXT | Estado de la operación |
| details | TEXT | Detalles adicionales |

## API Externa

### Endpoint Simulado
```python
def get_route_info(address: str) -> Dict[str, Any]:
    return {
        "distancia_km": 12.5,
        "tiempo_estimado": "25 min",
        "zona": "Urbana",
        "clima": "Despejado",
        "tracking_id": "LT-20240101-1234",
    }