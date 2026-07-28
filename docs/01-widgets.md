# 01 - Widgets Básicos - Fase 2

## Ventana Principal

La ventana de LogiTrack Desktop ahora incluye:

### Panel Izquierdo (70%)
- **Tabla de envíos** con 6 columnas:
  - ID
  - Destinatario
  - Dirección
  - Tipo
  - Estado (coloreado)
  - Fecha

### Panel Derecho (30%)
- **Formulario de alta** con:
  - Campo: Destinatario (texto)
  - Campo: Dirección (texto)
  - Combo: Tipo (Paquete, Documento, Carga, Mercancía)
  - Combo: Estado (Pendiente, En ruta, Entregado, Retrasado)
  - Botón: Guardar
  - Botón: Limpiar
  - Campo: Búsqueda (filtro en vivo)

### Barra de Estado
- Mensajes de feedback al usuario

## Atajos de Teclado
| Acción | Atajo |
|--------|-------|
| Nuevo envío | Ctrl+N |
| Guardar | Ctrl+S |
| Limpiar formulario | Esc |

## Validación
- El campo "Destinatario" es obligatorio
- El campo "Dirección" es obligatorio
- Feedback visual con QMessageBox