#!/usr/bin/env python3
"""
Prototipo alternativo con Tkinter + ttkbootstrap
Para demostrar que se evaluaron múltiples opciones

Este prototipo muestra la misma ventana básica de LogiTrack Desktop
pero implementada con Tkinter y ttkbootstrap en lugar de PyQt6.

Propósito: Evidencia práctica para justificar la elección del framework.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# Intentar importar las fuentes de ttkbootstrap, si falla usar las de tkinter
try:
    from tkinter import font
except ImportError:
    font = None


class LogiTrackTkWindow(tb.Window):
    """
    Prototipo de LogiTrack Desktop implementado con Tkinter + ttkbootstrap.
    
    Este prototipo reproduce la misma funcionalidad básica que la versión
    con PyQt6, permitiendo una comparación directa entre frameworks.
    """
    
    def __init__(self):
        # Inicializar con tema "darkly" (modo oscuro) o "cosmo" (modo claro)
        super().__init__(themename="darkly")
        
        # Configuración de la ventana
        self.title("LogiTrack Desktop (Tkinter)")
        self.geometry("1024x768")
        self.minsize(800, 600)
        
        # Variables de estado
        self.current_theme = "darkly"
        
        # Configurar la interfaz
        self._setup_menu()
        self._setup_central_widget()
        self._setup_status_bar()
        
        # Centrar la ventana en la pantalla
        self._center_window()
    
    def _center_window(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _setup_menu(self):
        """Configura la barra de menú"""
        # Crear barra de menú
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Salir", command=self.quit, accelerator="Ctrl+Q")
        
        # Menú Ver
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ver", menu=view_menu)
        
        # Submenú de temas
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Tema", menu=theme_menu)
        theme_menu.add_command(label="Modo Oscuro", command=lambda: self._change_theme("darkly"))
        theme_menu.add_command(label="Modo Claro", command=lambda: self._change_theme("cosmo"))
        theme_menu.add_separator()
        theme_menu.add_command(label="Tema Amarillo", command=lambda: self._change_theme("solar"))
        theme_menu.add_command(label="Tema Azul", command=lambda: self._change_theme("darkly"))
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Acerca de", command=self._show_about)
    
    def _change_theme(self, theme_name):
        """Cambia el tema de la aplicación"""
        self.style.theme_use(theme_name)
        self.current_theme = theme_name
        self._update_status_bar(f"✅ Tema: {theme_name}")
    
    def _setup_central_widget(self):
        """Configura el widget central (similar a la versión PyQt6)"""
        # Contenedor principal con padding
        main_frame = tb.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configurar grid del frame principal
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # ===== SECCIÓN DE BIENVENIDA =====
        welcome_frame = tb.Frame(main_frame)
        welcome_frame.grid(row=0, column=0, sticky="nsew")
        welcome_frame.grid_rowconfigure(0, weight=1)
        welcome_frame.grid_rowconfigure(1, weight=0)
        welcome_frame.grid_rowconfigure(2, weight=0)
        welcome_frame.grid_rowconfigure(3, weight=0)
        welcome_frame.grid_rowconfigure(4, weight=1)
        welcome_frame.grid_columnconfigure(0, weight=1)
        
        # Título principal
        title_label = tb.Label(
            welcome_frame,
            text="🚚 LogiTrack Desktop",
            font=("Helvetica", 28, "bold"),
            bootstyle="primary",
        )
        title_label.grid(row=0, column=0, pady=(50, 10))
        
        # Subtítulo
        subtitle_label = tb.Label(
            welcome_frame,
            text="Estación de Control Logístico de Escritorio",
            font=("Helvetica", 14),
            bootstyle="secondary",
        )
        subtitle_label.grid(row=1, column=0, pady=(0, 30))
        
        # Información del prototipo
        proto_info = tb.Label(
            welcome_frame,
            text="🔬 Prototipo con Tkinter + ttkbootstrap",
            font=("Helvetica", 11),
            bootstyle="info",
        )
        proto_info.grid(row=2, column=0, pady=(0, 10))
        
        # ===== SECCIÓN DE DEMOSTRACIÓN =====
        demo_frame = tb.Frame(welcome_frame)
        demo_frame.grid(row=3, column=0, pady=20)
        
        # Botones de demostración
        btn_style = tb.Button(
            demo_frame,
            text="🎨 Cambiar Estilo",
            command=self._demo_style_change,
            bootstyle="success",
            width=20,
        )
        btn_style.pack(side=tk.LEFT, padx=5)
        
        btn_counter = tb.Button(
            demo_frame,
            text="🔢 Contador",
            command=self._demo_counter,
            bootstyle="info",
            width=20,
        )
        btn_counter.pack(side=tk.LEFT, padx=5)
        
        btn_theme = tb.Button(
            demo_frame,
            text="🌓 Alternar Tema",
            command=self._toggle_theme,
            bootstyle="warning",
            width=20,
        )
        btn_theme.pack(side=tk.LEFT, padx=5)
        
        # ===== SECCIÓN DE COMPARATIVA =====
        compare_frame = tb.Frame(welcome_frame)
        compare_frame.grid(row=4, column=0, pady=(30, 0))
        compare_frame.grid_columnconfigure(0, weight=1)
        compare_frame.grid_columnconfigure(1, weight=1)
        
        # Tarjeta PyQt6
        pyqt_card = tb.Frame(
            compare_frame,
            bootstyle="primary",
            padding=15,
        )
        pyqt_card.grid(row=0, column=0, padx=10, sticky="nsew")
        
        tb.Label(
            pyqt_card,
            text="✅ PyQt6",
            font=("Helvetica", 14, "bold"),
            bootstyle="primary",
        ).pack(pady=(0, 5))
        
        tb.Label(
            pyqt_card,
            text="• Look nativo\n• Widgets avanzados\n• QThread para async\n• Excelente documentación",
            justify=tk.LEFT,
            bootstyle="secondary",
        ).pack()
        
        # Tarjeta Tkinter
        tk_card = tb.Frame(
            compare_frame,
            bootstyle="secondary",
            padding=15,
        )
        tk_card.grid(row=0, column=1, padx=10, sticky="nsew")
        
        tb.Label(
            tk_card,
            text="🔄 Tkinter (este prototipo)",
            font=("Helvetica", 14, "bold"),
            bootstyle="secondary",
        ).pack(pady=(0, 5))
        
        tb.Label(
            tk_card,
            text="• Curva de aprendizaje baja\n• Incluido en Python\n• ttkbootstrap para estilos\n• Más limitado en widgets",
            justify=tk.LEFT,
            bootstyle="secondary",
        ).pack()
        
        # Variable para el contador
        self.counter = 0
    
    def _demo_style_change(self):
        """Demuestra cambio de estilo en botones"""
        # Cambiar el estilo de un botón de demostración
        # (No implementado completamente en este prototipo)
        self._update_status_bar("🎨 Estilo cambiado (demo)")
        messagebox.showinfo(
            "Demo de Estilo",
            "En Tkinter, los estilos se cambian con style.configure()\n"
            "Ejemplo: style.configure('TButton', background='red')"
        )
    
    def _demo_counter(self):
        """Incrementa un contador y lo muestra"""
        self.counter += 1
        self._update_status_bar(f"🔢 Contador: {self.counter}")
        
        # Mostrar notificación tipo toast
        self._show_toast(f"Contador: {self.counter}")
    
    def _toggle_theme(self):
        """Alterna entre tema oscuro y claro"""
        if self.current_theme == "darkly":
            self._change_theme("cosmo")
        else:
            self._change_theme("darkly")
    
    def _show_toast(self, message):
        """Muestra una notificación tipo toast (popup temporal)"""
        # Crear ventana emergente
        toast = tk.Toplevel(self)
        toast.title("Notificación")
        toast.geometry("300x60")
        toast.overrideredirect(True)  # Quitar bordes de ventana
        
        # Posicionar en la esquina inferior derecha
        x = self.winfo_x() + self.winfo_width() - 320
        y = self.winfo_y() + self.winfo_height() - 100
        toast.geometry(f"+{x}+{y}")
        
        # Contenido
        tb.Label(
            toast,
            text=f"ℹ️ {message}",
            bootstyle="info",
            font=("Helvetica", 11),
        ).pack(pady=10, padx=10)
        
        # Auto-cerrar después de 2 segundos
        toast.after(2000, toast.destroy)
    
    def _setup_status_bar(self):
        """Configura la barra de estado"""
        self.status_frame = tb.Frame(self)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tb.Label(
            self.status_frame,
            text="✅ Listo | Tkinter + ttkbootstrap | Modo: Desarrollo",
            bootstyle="secondary",
            anchor="w",
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Indicador de versión
        version_label = tb.Label(
            self.status_frame,
            text="v0.1.0",
            bootstyle="secondary",
            anchor="e",
        )
        version_label.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def _update_status_bar(self, message):
        """Actualiza el mensaje de la barra de estado"""
        self.status_label.config(text=message)
    
    def _show_about(self):
        """Muestra el diálogo Acerca de"""
        messagebox.showinfo(
            "Acerca de LogiTrack Desktop (Tkinter)",
            "🚚 LogiTrack Desktop - Prototipo Tkinter\n\n"
            "Versión: 0.1.0 (Fase 1 - Prototipo)\n"
            "Framework: Tkinter + ttkbootstrap\n\n"
            "Este es un prototipo de demostración para\n"
            "comparar con la versión PyQt6.\n\n"
            "Propósito: Evidencia para justificar\n"
            "la elección del framework principal.\n\n"
            "📚 Diplomado: Especialista en Desarrollo\n"
            "de Software con Python SSR\n"
            "📖 Módulo 1: Programación visual y frameworks GUI"
        )
    
    def on_closing(self):
        """Maneja el evento de cierre"""
        if messagebox.askokcancel("Salir", "¿Deseas salir de LogiTrack Desktop?"):
            self.destroy()
    
    def quit(self):
        """Cierra la aplicación"""
        self.on_closing()


def main():
    """
    Punto de entrada principal del prototipo Tkinter.
    """
    # Crear la aplicación
    app = LogiTrackTkWindow()
    
    # Configurar evento de cierre
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Atajos de teclado básicos
    app.bind("<Control-q>", lambda e: app.on_closing())
    app.bind("<Control-Q>", lambda e: app.on_closing())
    
    # Iniciar el bucle principal
    app.mainloop()


if __name__ == "__main__":
    main()