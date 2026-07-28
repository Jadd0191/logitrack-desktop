# 00 - Fundamentos y Elección de Framework

## Matriz Comparativa de Frameworks GUI para Python

| Criterio | Tkinter + ttkbootstrap | PyQt6 | Kivy | Flet |
|----------|----------------------|-------|------|------|
| **Curva de aprendizaje** | Baja | Media-Alta | Media | Media |
| **Licencia** | BSD (libre) | GPL/LGPL (comercial) | MIT | Apache 2.0 |
| **Look nativo** | Aceptable (con ttkbootstrap) | Excelente (nativo en cada SO) | Personalizable (no nativo) | Web-like (Material Design) |
| **Empaquetado** | Fácil (PyInstaller) | Medio (recursos Qt) | Complejo | Complejo |
| **Comunidad** | Grande | Muy grande | Mediana | Creciente |
| **Documentación** | Buena | Excelente | Buena | Buena |
| **Rendimiento** | Bueno | Excelente | Bueno | Aceptable |
| **Widgets avanzados** | Limitados (requiere ttk) | Abundantes (nativos Qt) | Limitados | Limitados |
| **Modo oscuro nativo** | Con ttkbootstrap | Sí (nativo) | Manual | Sí (por defecto) |
| **Offline-first** | Sí | Sí | Sí | Parcial (requiere web) |

---

## Decisión Justificada

**Framework elegido: PyQt6**

### Justificación (178 palabras)

Tras analizar el caso de uso de LogiTrack Desktop — una aplicación de escritorio para despachadores en sucursales de logística con internet inestable —, la elección de PyQt6 responde a criterios objetivos que priorizan la experiencia del usuario final y la sostenibilidad del proyecto.

En primer lugar, el **look nativo** de PyQt6 es superior. Los despachadores trabajan en computadoras de mostrador con sistemas operativos variados (Windows 10/11, algunas con Linux). PyQt6 emula perfectamente el aspecto nativo de cada sistema, reduciendo la curva de adopción porque la herramienta se siente familiar desde el primer momento.

En segundo lugar, **el ecosistema de widgets** de Qt es el más completo. Necesitamos una tabla avanzada con ordenamiento y filtrado (QTableView con QSortFilterProxyModel), una barra de estado con indicadores visuales, y posibilidad de añadir atajos de teclado sin esfuerzo. Qt ofrece todo esto de serie, mientras que Tkinter requeriría múltiples extensiones.

En tercer lugar, la **madurez en concurrencia** es crítica. QThread y el sistema de señales/slots integrado de Qt proporcionan una forma segura y probada de ejecutar tareas en segundo plano sin congelar la UI, algo fundamental para el caso LogiTrack donde las consultas a API y BBDD son constantes.

Finalmente, aunque la licencia GPL requiere compartir el código fuente, este proyecto es open-source y educativo, por lo que no supone una limitación.


Para respaldar mi decisión, desarrollé un prototipo funcional con  Tkinter + ttkbootstrap (ver prototypes/tkinter_prototype.py). Al ejecutarlo, pude comprobar que aunque ttkbootstrap mejora la apariencia de Tkinter, sigue sin ofrecer widgets tan avanzados como los de Qt. 
La tabla que necesitamos para LogiTrack (ordenable, filtrable, jerárquica) requeriría mucho más trabajo en Tkinter. Esta evidencia práctica confirma que PyQt6 es la mejor opción para nuestro caso.
---