# 03 - Eventos, Señales y Asincronía - Fase 4

## Estrategia de Concurrencia

### QThread + Workers

Para evitar congelar la UI, utilizamos `QThread` con workers dedicados:
UI Thread (Principal)
↓
QThread (Worker)
↓
Tarea en segundo plano
↓
Señal → UI Thread (Actualización segura)


### Flujo de Trabajo

1. **Usuario** hace clic en un botón
2. **UI** crea un Worker y lo inicia en un QThread
3. **Worker** ejecuta la tarea en segundo plano
4. **Worker** emite señales de progreso/estado
5. **UI** recibe las señales y actualiza la interfaz
6. **Worker** termina y emite `finished`

## Componentes

### Worker
- Hereda de `QThread`
- Tiene métodos `run()` y `cancel()`
- Emite señales: `data`, `progress`, `status`, `finished`, `error`

### ShipmentWorker
- Especializado para operaciones de envíos
- Soporta: `load`, `save`, `search`, `sync`

### Señales y Slots

| Señal | Propósito | Conectado a |
|-------|-----------|-------------|
| `data` | Envía resultados | `_on_shipments_loaded`, `_on_shipment_saved` |
| `progress` | Actualiza progreso | `_on_task_progress` |
| `status` | Mensajes de estado | `_on_task_status` |
| `error` | Errores | `_on_task_error` |
| `finished` | Tarea completada | `_on_task_finished` |

## Diagrama de Hilos
┌─────────────────────────────────────────────────────────┐
│ UI THREAD (Principal) │
│ ┌─────────────────────────────────────────────────┐ │
│ │ LogiTrackWindow │ │
│ │ - Botón "Cargar Datos" → _load_shipments_async│ │
│ │ - Botón "Guardar" → _save_shipment_async │ │
│ │ - Botón "Cancelar" → _cancel_current_task │ │
│ └─────────────────────────────────────────────────┘ │
│ ↑ │
│ Señales (data, progress) │
│ │ │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Worker (QThread) │ │
│ │ - run() → ejecuta tarea │ │
│ │ - cancel() → detiene tarea │ │
│ │ - Emite señales de progreso │ │
│ └─────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘


## Prueba de Asincronía

### Cómo verificar que la UI no se congela:

1. **Haz clic en "Cargar Datos"**
2. **Intenta mover la ventana** - Debe moverse suavemente
3. **Intenta escribir en el buscador** - Debe responder
4. **Intenta hacer clic en "Limpiar"** - Debe funcionar

### Con tarea síncrona (MALO):
```python
# ❌ Esto congela la UI
time.sleep(5)
self.table.setRowCount(0)

# ✅ Esto NO congela la UI
worker = ShipmentWorker("load")
worker.signals.data.connect(self._on_shipments_loaded)
worker.start()