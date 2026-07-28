# 02 - Gestión de Geometría y Layouts - Fase 3

## Estrategia de Layouts

### Layouts Utilizados

1. **QVBoxLayout** - Layout vertical principal
2. **QHBoxLayout** - Layout horizontal para botones
3. **QGridLayout** - Layout en grilla para el formulario
4. **QSplitter** - Separador redimensionable entre tabla y formulario

## Estructura de Layouts
QMainWindow
└── QWidget (central)
└── QVBoxLayout (main_layout)
└── QSplitter (horizontal)
├── QWidget (left_panel)
│ └── QVBoxLayout
│ ├── QLabel (título)
│ └── QTableWidget
└── QWidget (right_panel)
└── QVBoxLayout
├── QGroupBox (formulario)
│ └── QGridLayout
│ ├── Destinatario
│ ├── Dirección
│ ├── Tipo
│ ├── Estado
│ ├── Botones (HBoxLayout)
│ └── Búsqueda
└── QLabel (contador)


## Características Responsivas

### Splitter
- El usuario puede arrastrar el separador para cambiar la proporción
- Proporción inicial: 70/30 (Tabla/Formulario)

### Tamaños Mínimos
- Ventana: 1000x650
- Formulario: 280px de ancho mínimo, 380px máximo

### Política de Tamaño
- Tabla: Expanding (se expande libremente)
- Formulario: Fixed (mantiene su ancho)

## Capturas de Pantalla

### Tamaño Pequeño (1000x650)
[Captura]

### Tamaño Medio (1200x750)
[Captura]

### Tamaño Maximizado
[Captura]

## Mejoras de la Fase 3

1. **QSplitter** para redimensionamiento interactivo
2. **QGridLayout** para mejor alineación del formulario
3. **Botones con estilos** visuales
4. **Color por estado** en la tabla
5. **Contador de envíos** en tiempo real