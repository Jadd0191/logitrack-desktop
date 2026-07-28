# 04 - Componentes Visuales Avanzados - Fase 5

## Sistema de Temas

### Modos Disponibles
- **Claro** (Light) - Por defecto
- **Oscuro** (Dark) - Para entornos con poca luz

### Toggle de Tema
- Atajo: `Ctrl+T`
- Menú: `Ver → Alternar Tema`

## Componentes Personalizados

### 1. StatusBadge
Badge visual para mostrar el estado de un envío.

| Estado | Color | Icono |
|--------|-------|-------|
| Entregado | ✅ Verde | ● |
| En ruta | 🟡 Amarillo | ● |
| Pendiente | 🔵 Celeste | ● |
| Retrasado | 🔴 Rojo | ● |

### 2. KPICard
Tarjeta para mostrar métricas clave.

| KPI | Descripción |
|-----|-------------|
| Total Envíos | Total de envíos registrados |
| Pendientes | Envíos en estado pendiente |
| Entregados | Envíos entregados |
| Retrasados | Envíos con retraso |

### 3. FilterBar
Barra de filtros para la tabla.

- **Filtro por estado**: Menú desplegable
- **Limpiar filtros**: Botón para resetear

## Estilos

### Centralización en `theme.py`

```python
class ThemeColors:
    background = "#ffffff"
    text = "#212529"
    success = "#28a745"
    warning = "#ffc107"
    danger = "#dc3545"
    info = "#17a2b8"