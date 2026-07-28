# 05 - Arquitectura MVC/MVVM - Fase 6

## Estructura de Capas
logitrack/
├── models/ # Modelos de datos (CERO UI)
│ ├── shipment.py # Shipment, ShipmentStatus, ShipmentType
│ └── init.py
│
├── views/ # Vistas (CERO lógica de negocio)
│ └── main_window.py # LogiTrackWindow
│
├── controllers/ # Controladores (Orquestan)
│ └── shipment_controller.py
│
├── services/ # Servicios (Lógica de negocio)
│ └── shipment_service.py
│
├── ui/ # UI (Temas y componentes)
│ ├── theme.py
│ └── components.py
│
└── app.py # Bootstrap + Inyección de dependencias

## Diagrama de Dependencias

┌─────────────────────────────────────────────────────────────┐
│ app.py                                                      │
│ (Bootstrap + DI Container)                                  │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ views/main_window.py                                        │
│ (LogiTrackWindow)                                           │
│ SOLO UI - SIN LÓGICA DE NEGOCIO                             │
└─────────────────────────────────────────────────────────────┘
│
▼ (señales)
┌─────────────────────────────────────────────────────────────┐
│ controllers/shipment_controller.py                          │
│ (ShipmentController)                                        │
│ Traduce eventos UI → Servicios                              │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ services/shipment_service.py                                │
│ (ShipmentService)                                           │
│ Lógica de negocio + SQLite                                  │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ models/shipment.py                                          │
│ (Shipment)                                                  │
│ Modelos de datos + validación                               │
└─────────────────────────────────────────────────────────────┘


## Reglas Arquitectónicas

### ✅ Correcto
```python
# Vista llama al Controlador
self.controller.save_shipment(data)

# Controlador llama al Servicio
self._service.create(data)

# Servicio usa Modelos
shipment = Shipment(...)

