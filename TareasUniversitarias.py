import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser
import tkinter.ttk as ttk
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import json, os
import math
import threading
import time

try:
    from pystray import Icon, Menu, MenuItem
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False

try:
    from plyer.notification import notify  # type: ignore
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

try:
    from PIL import Image, ImageTk, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ==========================
# CONFIG
# ==========================
ARCHIVO = "tareas.json"
PERFIL_ARCHIVO = "perfil.json"
USUARIO = "Usuario"

COLORES_ESTADO = {
    "Pendiente": "#d6ecff",
    "Proximo":   "#c2f0ff",
    "Urgente":   "#ffb3b3",
    "Vencido":   "#ff8c8c",
    "Entregado": "#caffbf",
}

ESTADOS = ["Pendiente", "Proximo", "Urgente", "Vencido", "Entregado"]

MATERIAS = [
    "Operativa",
    "Big Data",
    "Analisis numerico",
    "Comunicación de datos",
    "Emprendimiento e innovación",
    "Ciencia, tecnología e innovación",
    "Seguridad en hardware",
]

EMOJIS_MATERIAS = {
    "Operativa": "🧮",
    "Big Data": "📊",
    "Analisis numerico": "📈",
    "Comunicación de datos": "📡",
    "Emprendimiento e innovación": "💡",
    "Ciencia, tecnología e innovación": "🔬",
    "Seguridad en hardware": "🔐",
}

NOTIFICACIONES_HOY_FILE = "notificaciones_hoy.json"

# Configurar CustomTkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# ==========================
# FUNCIONES AUXILIARES
# ==========================

def obtener_notificaciones_hoy() -> set:
    """Obtiene el conjunto de IDs de tareas notificadas hoy."""
    hoy = datetime.now().date()
    if not os.path.exists(NOTIFICACIONES_HOY_FILE):
        return set()
    try:
        with open(NOTIFICACIONES_HOY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("fecha") != str(hoy):
            return set()
        return set(data.get("tarea_ids", []))
    except (json.JSONDecodeError, OSError):
        return set()


def guardar_notificaciones_hoy(tarea_ids: set):
    """Guarda las IDs de tareas notificadas hoy."""
    hoy = datetime.now().date()
    data = {
        "fecha": str(hoy),
        "tarea_ids": list(tarea_ids)
    }
    try:
        with open(NOTIFICACIONES_HOY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except OSError:
        pass


def enviar_notificacion(titulo: str, mensaje: str):
    """Envía una notificación inteligente con plyer."""
    if PLYER_AVAILABLE:
        try:
            notify(
                title=titulo,
                message=mensaje,
                timeout=15,
                app_name="Gestor de Tareas"
            )
        except Exception:
            pass


def monitoreo_tareas_background(archivo_tareas: str = ARCHIVO):
    """Hilo de monitoreo que verifica tareas próximas a vencer cada 30 minutos."""
    def ejecutar_monitoreo():
        while True:
            try:
                ahora = datetime.now()
                notificaciones_hoy = obtener_notificaciones_hoy()

                tareas = []
                if os.path.exists(archivo_tareas):
                    try:
                        with open(archivo_tareas, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        if isinstance(data, dict):
                            tareas = data.get("tareas", [])
                        elif isinstance(data, list):
                            tareas = data
                    except (json.JSONDecodeError, OSError):
                        tareas = []

                for t in tareas:
                    try:
                        tarea_id = f"{t.get('nombre', '')}_{t.get('materia', '')}_{t.get('fecha', '')}"
                        if tarea_id in notificaciones_hoy:
                            continue

                        if isinstance(t.get("fecha"), str):
                            fecha = datetime.strptime(t["fecha"], "%Y-%m-%d %H:%M")
                        else:
                            fecha = t.get("fecha")

                        if not fecha or t.get("entregado"):
                            continue

                        diff = fecha - ahora
                        if timedelta(0) < diff <= timedelta(hours=24):
                            materia = t.get("materia", "Sin materia")
                            emoji = EMOJIS_MATERIAS.get(materia, "📝")
                            horas_restantes = int(diff.total_seconds() / 3600)
                            minutos_restantes = int((diff.total_seconds() % 3600) / 60)

                            titulo = f"{emoji} {materia}"
                            tiempo_str = f"{horas_restantes}h {minutos_restantes}m" if horas_restantes > 0 else f"{minutos_restantes}m"
                            mensaje = f"'{t.get('nombre', 'Tarea sin nombre')}' vence en {tiempo_str}"

                            enviar_notificacion(titulo, mensaje)
                            notificaciones_hoy.add(tarea_id)
                            guardar_notificaciones_hoy(notificaciones_hoy)
                    except Exception:
                        continue

                time.sleep(1800)
            except Exception:
                time.sleep(1800)

    hilo = threading.Thread(target=ejecutar_monitoreo, daemon=True)
    hilo.start()


def cargar_perfil():
    """Carga el perfil del usuario desde perfil.json"""
    if not os.path.exists(PERFIL_ARCHIVO):
        return None
    try:
        with open(PERFIL_ARCHIVO, "r", encoding="utf-8") as f:
            perfil = json.load(f)
        if not isinstance(perfil, dict) or not perfil.get("materias"):
            return None
        return perfil
    except (json.JSONDecodeError, OSError):
        return None


def guardar_perfil(perfil):
    """Guarda el perfil del usuario"""
    with open(PERFIL_ARCHIVO, "w", encoding="utf-8") as f:
        json.dump(perfil, f, indent=4, ensure_ascii=False)


def iniciar_onboarding():
    """Inicia el asistente de configuración inicial"""
    root = ctk.CTk()
    setup = ProfileSetup(root)
    root.mainloop()
    result = setup.result
    # Destruir completamente la ventana antes de retornar
    try:
        root.destroy()
    except (tk.TclError, AttributeError):
        pass
    return result


# ==========================
# CLASE CONFIGURACIÓN INICIAL
# ==========================
class ProfileSetup:
    """Asistente interactivo para configurar el perfil inicial"""
    
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("Configurar Perfil")
        self.root.geometry("800x900")
        self.result = None
        self.materia_rows = []

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Centrar la ventana en la pantalla
        self.root.update_idletasks()
        ancho_pantalla = self.root.winfo_screenwidth()
        alto_pantalla = self.root.winfo_screenheight()
        x = (ancho_pantalla - 800) // 2
        y = (alto_pantalla - 900) // 2
        self.root.geometry(f"800x900+{max(0, x)}+{max(0, y)}")

        # Encabezado
        header_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 12))
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_frame,
            text="Configura tu Cuenta",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text="Completa tu perfil y agrega tus materias con colores personalizados.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="gray60"
        ).pack(anchor="w", pady=(4, 0))

        # Canvas scrolleable
        canvas_frame = ctk.CTkFrame(self.root)
        canvas_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        self.canvas = ctk.CTkCanvas(canvas_frame, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = ctk.CTkScrollbar(canvas_frame, command=self.canvas.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")
        self.canvas_window = self.canvas.create_window(0, 0, window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self._crear_contenido()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _crear_contenido(self):
        """Crea el formulario de configuración"""
        # Contenedor centrado para la tarjeta
        center_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        center_frame.pack(fill="both", expand=True, padx=20, pady=20)
        center_frame.grid_columnconfigure(0, weight=1)
        
        card = ctk.CTkFrame(center_frame, corner_radius=15)
        card.grid(row=0, column=0, sticky="new", padx=10, pady=10)
        card.grid_columnconfigure(0, weight=1)

        # Sección 1: Datos personales
        ctk.CTkLabel(
            card,
            text="1. Datos Personales",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 12))

        frame_form = ctk.CTkFrame(card, fg_color="transparent")
        frame_form.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        frame_form.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame_form,
            text="Nombre del Estudiante",
            font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.entry_nombre = ctk.CTkEntry(
            frame_form,
            placeholder_text="Tu nombre completo",
            corner_radius=8,
            height=40
        )
        self.entry_nombre.grid(row=1, column=0, sticky="ew", pady=(0, 14))

        ctk.CTkLabel(
            frame_form,
            text="Perfil / Carrera",
            font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=2, column=0, sticky="w", pady=(0, 6))

        self.entry_carrera = ctk.CTkEntry(
            frame_form,
            placeholder_text="Ej: Ingeniería de Sistemas",
            corner_radius=8,
            height=40
        )
        self.entry_carrera.grid(row=3, column=0, sticky="ew")

        # Sección 2: Materias
        ctk.CTkLabel(
            card,
            text="2. Materias y Colores",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        ).grid(row=2, column=0, sticky="w", padx=20, pady=(20, 4))

        ctk.CTkLabel(
            card,
            text="Define tus materias y elige el color que las represente.",
            font=ctk.CTkFont(size=10),
            text_color="gray60"
        ).grid(row=3, column=0, sticky="w", padx=20, pady=(0, 12))

        self.frame_materias = ctk.CTkFrame(card, fg_color="transparent")
        self.frame_materias.grid(row=4, column=0, sticky="ew", padx=20)
        self.frame_materias.grid_columnconfigure(0, weight=1)

        btn_add = ctk.CTkButton(
            card,
            text="+ Agregar Materia",
            command=self.agregar_materia_fila,
            corner_radius=8,
            height=32
        )
        btn_add.grid(row=5, column=0, sticky="w", padx=20, pady=(16, 20))

        button_frame = ctk.CTkFrame(card, fg_color="transparent")
        button_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=(0, 20))
        button_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            button_frame,
            text="Guardar y Comenzar",
            command=self.guardar,
            corner_radius=8,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, sticky="ew")

        self.agregar_materia_fila()

    def agregar_materia_fila(self, nombre="", color="#6EC1FF"):
        """Añade una fila de entrada para una materia"""
        row_num = len(self.materia_rows)
        row_frame = ctk.CTkFrame(self.frame_materias, fg_color="transparent")
        row_frame.grid(row=row_num, column=0, sticky="ew", pady=8)
        row_frame.grid_columnconfigure(0, weight=1)

        entry = ctk.CTkEntry(
            row_frame,
            placeholder_text="Nombre de la materia",
            corner_radius=8,
            height=32
        )
        entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        if nombre:
            entry.insert(0, nombre)

        action_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        action_frame.grid(row=0, column=1, sticky="ew")

        color_var = ctk.StringVar(value=color)
        color_label = ctk.CTkLabel(
            action_frame,
            text="■",
            font=ctk.CTkFont(size=18),
            text_color=color
        )
        color_label.pack(side="left", padx=4)

        def cambiar_color():
            _, nuevo_color = colorchooser.askcolor(initialcolor=color_var.get())
            if nuevo_color:
                color_var.set(nuevo_color)
                color_label.configure(text_color=nuevo_color)

        color_btn = ctk.CTkButton(
            action_frame,
            text="Cambiar Color",
            command=cambiar_color,
            width=100,
            height=28,
            corner_radius=6,
            font=ctk.CTkFont(size=10)
        )
        color_btn.pack(side="left", padx=4)

        def eliminar():
            row_frame.destroy()
            self.materia_rows.remove(row_data)
            for idx, rd in enumerate(self.materia_rows):
                rd["frame"].grid(row=idx, column=0, sticky="ew", pady=8)

        btn_delete = ctk.CTkButton(
            action_frame,
            text="✕",
            command=eliminar,
            width=32,
            height=28,
            corner_radius=6,
            fg_color="red",
            font=ctk.CTkFont(size=12)
        )
        btn_delete.pack(side="left", padx=2)

        row_data = {
            "frame": row_frame,
            "entry": entry,
            "color_var": color_var,
        }
        self.materia_rows.append(row_data)

    def guardar(self):
        """Guarda la configuración inicial"""
        nombre = self.entry_nombre.get().strip()
        carrera = self.entry_carrera.get().strip()
        materias = []

        for item in self.materia_rows:
            materia = item["entry"].get().strip()
            color = item["color_var"].get()
            if materia:
                materias.append({"nombre": materia, "color": color})

        if not nombre:
            messagebox.showwarning("Atención", "Escribe tu nombre.", parent=self.root)
            return
        if not carrera:
            messagebox.showwarning("Atención", "Escribe tu carrera.", parent=self.root)
            return
        if not materias:
            messagebox.showwarning("Atención", "Agrega al menos una materia.", parent=self.root)
            return

        perfil = {"nombre": nombre, "carrera": carrera, "materias": materias}
        guardar_perfil(perfil)
        self.result = perfil
        self.root.destroy()

    def on_close(self):
        self.result = None
        self.root.destroy()


# ==========================
# CLASE PRINCIPAL
# ==========================
class App:
    """Aplicación principal del Gestor de Tareas"""
    
    def __init__(self, root: ctk.CTk, profile: dict):
        self.root = root
        self.root.title("Gestor de Tareas Universitarias")
        self.root.geometry("1400x850")
        self.root.minsize(900, 600)

        self.filtro_materia = ctk.StringVar(value="Todas")
        self.tareas: list[dict] = []
        self.hora_var = ctk.StringVar(value="12:00")
        self.profile = profile
        self.usuario = profile.get("nombre", USUARIO)
        self.carrera = profile.get("carrera", "")
        self.materias = [m["nombre"] for m in profile.get("materias", [])] or MATERIAS
        self.colores_materias = {m["nombre"]: m["color"] for m in profile.get("materias", [])}
        self.profile_photo_path = profile.get("foto")
        self.tray_icon = None
        self.profile_image = None
        self.closing = False

        self.root.protocol("WM_DELETE_WINDOW", self._al_cerrar_ventana)
        self._cargar_tareas()
        self._construir_ui()
        self.actualizar_tablero()

        monitoreo_tareas_background(ARCHIVO)
        self.root.after(200, self._crear_icono_bandeja)

    # ==================== PERSISTENCIA ====================
    
    def _cargar_tareas(self):
        """Carga las tareas desde tareas.json"""
        if not os.path.exists(ARCHIVO):
            self._crear_archivo_tareas()
            return
        try:
            with open(ARCHIVO, "r", encoding="utf-8") as f:
                data = json.load(f)

            tareas = []
            if isinstance(data, dict):
                tareas = data.get("tareas", [])
            elif isinstance(data, list):
                tareas = data

            for t in tareas:
                t["fecha"] = datetime.strptime(t["fecha"], "%Y-%m-%d %H:%M")
                self.tareas.append(t)
        except (json.JSONDecodeError, KeyError, ValueError, OSError):
            self.tareas = []
            self._crear_archivo_tareas()

    def _crear_archivo_tareas(self):
        """Crea un archivo tareas.json vacío"""
        with open(ARCHIVO, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)

    def _guardar_tareas(self):
        """Guarda las tareas en tareas.json"""
        with open(ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(
                [{**t, "fecha": t["fecha"].strftime("%Y-%m-%d %H:%M")} for t in self.tareas],
                f, indent=4,
                ensure_ascii=False
            )

    # ==================== LÓGICA DE ESTADO ====================
    
    @staticmethod
    def get_estado(t: dict) -> str:
        """Determina el estado de una tarea basado en la fecha"""
        ahora = datetime.now()
        diff = t["fecha"] - ahora

        if t["entregado"]:
            return "Entregado"
        if diff <= timedelta(0):
            return "Vencido"
        if t.get("manual") == "Urgente":
            return "Urgente"
        if diff <= timedelta(days=4):
            return "Urgente"
        if t["fecha"].isocalendar()[1] == ahora.isocalendar()[1]:
            return "Proximo"
        return "Pendiente"

    # ==================== ACCIONES ====================
    
    def agregar_tarea(self):
        """Agrega una nueva tarea"""
        nombre = self.entry_nombre.get().strip()
        materia = self.combo_materia.get()

        if not nombre:
            messagebox.showwarning("Atención", "Escribe el nombre de la tarea.")
            return
        if not materia:
            messagebox.showwarning("Atención", "Selecciona una materia.")
            return

        try:
            fecha_hora = datetime.strptime(
                f"{self.cal.get_date().strftime('%d/%m/%Y')} {self.hora_var.get()}",
                "%d/%m/%Y %H:%M"
            )
        except ValueError:
            messagebox.showerror("Error", "Formato de hora inválido (usa HH:MM).")
            return

        self.tareas.append({
            "nombre": nombre,
            "materia": materia,
            "fecha": fecha_hora,
            "entregado": False,
            "manual": None,
        })

        self._guardar_tareas()
        self.actualizar_tablero()
        self.entry_nombre.delete(0, ctk.END)

    def cambiar_estado(self, t: dict, entregado: bool):
        """Marca una tarea como entregada o pendiente"""
        t["entregado"] = entregado
        t["manual"] = None
        self._guardar_tareas()
        self.actualizar_tablero()

    def marcar_urgente(self, t: dict):
        """Marca manualmente una tarea como urgente"""
        t["manual"] = "Urgente"
        self._guardar_tareas()
        self.actualizar_tablero()

    def eliminar_tarea(self, t: dict):
        """Elimina una tarea después de confirmación"""
        if not messagebox.askyesno("Confirmar", f"¿Eliminar '{t['nombre']}'?"):
            return
        try:
            self.tareas.remove(t)
        except ValueError:
            pass
        self._guardar_tareas()
        self.actualizar_tablero()

    def editar_tarea(self, t: dict):
        """Abre diálogo para editar una tarea"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Editar Tarea")
        dialog.geometry("450x320")
        dialog.grab_set()

        dialog.grid_columnconfigure(0, weight=1)

        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame,
            text="Nombre de la Tarea",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        entry_nombre = ctk.CTkEntry(frame, corner_radius=8, height=40)
        entry_nombre.insert(0, t["nombre"])
        entry_nombre.grid(row=1, column=0, sticky="ew", pady=(0, 16))

        ctk.CTkLabel(
            frame,
            text="Materia",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=2, column=0, sticky="w", pady=(0, 6))

        combo_materia = ctk.CTkComboBox(
            frame,
            values=self.materias,
            corner_radius=8,
            height=40
        )
        combo_materia.set(t["materia"])
        combo_materia.grid(row=3, column=0, sticky="ew", pady=(0, 16))

        ctk.CTkLabel(
            frame,
            text="Hora (HH:MM)",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=4, column=0, sticky="w", pady=(0, 6))

        hora_entry = ctk.CTkEntry(
            frame,
            placeholder_text="12:00",
            corner_radius=8,
            height=40
        )
        hora_entry.insert(0, t["fecha"].strftime("%H:%M"))
        hora_entry.grid(row=5, column=0, sticky="ew", pady=(0, 20))

        def guardar():
            nuevo_nombre = entry_nombre.get().strip()
            nueva_materia = combo_materia.get()
            if not nuevo_nombre or not nueva_materia:
                messagebox.showwarning("Atención", "Completa todos los campos.", parent=dialog)
                return
            try:
                nueva_hora = datetime.strptime(hora_entry.get(), "%H:%M")
            except ValueError:
                messagebox.showerror("Error", "Formato de hora inválido (HH:MM).", parent=dialog)
                return
            
            t["nombre"] = nuevo_nombre
            t["materia"] = nueva_materia
            t["fecha"] = t["fecha"].replace(hour=nueva_hora.hour, minute=nueva_hora.minute)
            self._guardar_tareas()
            self.actualizar_tablero()
            dialog.destroy()

        btn_guardar = ctk.CTkButton(
            frame,
            text="Guardar Cambios",
            command=guardar,
            corner_radius=8,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        btn_guardar.grid(row=6, column=0, sticky="ew")

    # ==================== UI ====================
    
    def _construir_ui(self):
        """Construye la interfaz completa de la aplicación"""
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self._construir_encabezado()
        self._construir_panel_inputs()
        self._construir_tablero()

    def _construir_encabezado(self):
        """Construye el encabezado con saludo y reloj"""
        header_frame = ctk.CTkFrame(self.root, corner_radius=15)
        header_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        header_frame.grid_columnconfigure(1, weight=1)

        # Lado izquierdo: Avatar y datos
        left_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="ns", padx=40, pady=20)
        left_frame.grid_columnconfigure(0, weight=0)

        avatar_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        avatar_frame.grid(row=0, column=0, sticky="nw", padx=(0, 20))

        self.avatar_canvas = ctk.CTkCanvas(
            avatar_frame,
            width=90, height=90,
            highlightthickness=0
        )
        self.avatar_canvas.pack()
        self._dibujar_avatar_inicial()

        if self.profile_photo_path and os.path.exists(self.profile_photo_path):
            self._mostrar_avatar_por_ruta(self.profile_photo_path)

        info_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="nw")

        ctk.CTkLabel(
            info_frame,
            text=f"👋 Hola, {self.usuario}",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        ).pack(anchor="w")

        ctk.CTkLabel(
            info_frame,
            text=f"📚 {self.carrera}",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="gray70"
        ).pack(anchor="w", pady=(4, 0))

        # Lado derecho: Reloj analógico
        clock_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        clock_frame.grid(row=0, column=1, sticky="ne", padx=40, pady=20)

        self.canvas_reloj = ctk.CTkCanvas(
            clock_frame,
            width=140, height=140,
            highlightthickness=0
        )
        self.canvas_reloj.pack()
        self.canvas_reloj.after(100, self.dibujar_reloj)

    def _dibujar_avatar_inicial(self):
        """Dibuja el avatar inicial con la letra del nombre"""
        self.avatar_canvas.delete("all")
        initial = self.usuario[0].upper() if self.usuario else "U"
        self.avatar_canvas.create_text(
            45, 45,
            text=initial,
            font=ctk.CTkFont(family="Segoe UI", size=36, weight="bold"),
            fill="white"
        )

    def _mostrar_avatar_por_ruta(self, ruta: str):
        """Carga y muestra la foto de perfil desde una ruta"""
        if not PIL_AVAILABLE:
            return

        try:
            imagen = Image.open(ruta).convert("RGBA")
            ancho, alto = imagen.size
            lado = min(ancho, alto)
            izquierda = (ancho - lado) // 2
            superior = (alto - lado) // 2
            imagen = imagen.crop((izquierda, superior, izquierda + lado, superior + lado))
            imagen = imagen.resize((80, 80), Image.LANCZOS)

            mask = Image.new("L", (80, 80), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 80, 80), fill=255)
            imagen.putalpha(mask)

            self.profile_image = ImageTk.PhotoImage(imagen)
            self.avatar_canvas.delete("all")
            self.avatar_canvas.create_image(45, 45, image=self.profile_image)
        except Exception:
            pass

    def dibujar_reloj(self):
        """Dibuja el reloj analógico actualizado"""
        # Detener si la ventana se está cerrando
        if self.closing:
            return
        
        # Verificar que el widget existe antes de intentar operaciones
        try:
            if not self.canvas_reloj.winfo_exists():
                return
            self.canvas_reloj.delete("all")
        except (tk.TclError, AttributeError):
            return

        ancho = self.canvas_reloj.winfo_width()
        alto = self.canvas_reloj.winfo_height()

        if ancho < 10:
            if not self.closing:
                self.canvas_reloj.after(100, self.dibujar_reloj)
            return

        cx, cy = ancho // 2, alto // 2
        radio = min(ancho, alto) // 2 - 8

        # Fondo del reloj
        self.canvas_reloj.create_oval(
            cx - radio, cy - radio, cx + radio, cy + radio,
            fill="#1F1F1F", outline="#3F3F3F", width=2
        )

        # Marcas de horas
        for i in range(12):
            angulo = math.radians(i * 30 - 90)
            x1 = cx + (radio - 12) * math.cos(angulo)
            y1 = cy + (radio - 12) * math.sin(angulo)
            x2 = cx + (radio - 4) * math.cos(angulo)
            y2 = cy + (radio - 4) * math.sin(angulo)
            self.canvas_reloj.create_line(x1, y1, x2, y2, fill="#FFFFFF", width=2)

        ahora = datetime.now()
        horas = ahora.hour % 12
        minutos = ahora.minute
        segundos = ahora.second

        angulo_h = math.radians(horas * 30 + minutos * 0.5 - 90)
        angulo_m = math.radians(minutos * 6 + segundos * 0.1 - 90)
        angulo_s = math.radians(segundos * 6 - 90)

        # Manecilla de horas
        x_h = cx + (radio * 0.5) * math.cos(angulo_h)
        y_h = cy + (radio * 0.5) * math.sin(angulo_h)
        self.canvas_reloj.create_line(cx, cy, x_h, y_h, fill="#FFFFFF", width=6, capstyle="round")

        # Manecilla de minutos
        x_m = cx + (radio * 0.7) * math.cos(angulo_m)
        y_m = cy + (radio * 0.7) * math.sin(angulo_m)
        self.canvas_reloj.create_line(cx, cy, x_m, y_m, fill="#4DAEFF", width=4, capstyle="round")

        # Manecilla de segundos
        x_s = cx + (radio * 0.75) * math.cos(angulo_s)
        y_s = cy + (radio * 0.75) * math.sin(angulo_s)
        self.canvas_reloj.create_line(cx, cy, x_s, y_s, fill="#FF6B6B", width=1)

        # Centro
        self.canvas_reloj.create_oval(
            cx - 6, cy - 6, cx + 6, cy + 6,
            fill="#FFFFFF", outline="#4DAEFF", width=2
        )

        self.canvas_reloj.after(1000, self.dibujar_reloj)

    def _construir_panel_inputs(self):
        """Construye el panel de entrada para nuevas tareas"""
        input_frame = ctk.CTkFrame(self.root, corner_radius=15)
        input_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))
        # Configurar columnas: entrada principal más ancha, resto proporcional
        input_frame.grid_columnconfigure(0, weight=3)  # Nombre (más ancho)
        input_frame.grid_columnconfigure(1, weight=2)  # Materia
        input_frame.grid_columnconfigure(2, weight=2)  # Fecha
        input_frame.grid_columnconfigure(3, weight=1)  # Hora
        input_frame.grid_columnconfigure(4, weight=1)  # Agregar
        input_frame.grid_columnconfigure(5, weight=1)  # Filtro

        # Columna 0: Nombre de tarea
        left = ctk.CTkFrame(input_frame, fg_color="transparent")
        left.grid(row=0, column=0, sticky="ew", padx=(20, 8), pady=16)
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            left,
            text="Nueva Tarea",
            font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.entry_nombre = ctk.CTkEntry(
            left,
            placeholder_text="Nombre de la tarea",
            corner_radius=8,
            height=40
        )
        self.entry_nombre.grid(row=1, column=0, sticky="ew")
        self.entry_nombre.bind("<Return>", lambda _: self.agregar_tarea())

        # Columna 1: Materia
        materia_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        materia_frame.grid(row=0, column=1, sticky="ew", padx=8, pady=16)
        materia_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            materia_frame,
            text="Materia",
            font=ctk.CTkFont(size=10, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.combo_materia = ctk.CTkComboBox(
            materia_frame,
            values=self.materias,
            corner_radius=8,
            height=40
        )
        self.combo_materia.grid(row=1, column=0, sticky="ew")

        # Columna 2: Fecha
        fecha_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        fecha_frame.grid(row=0, column=2, sticky="ew", padx=8, pady=16)
        fecha_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            fecha_frame,
            text="Fecha",
            font=ctk.CTkFont(size=10, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.cal = DateEntry(fecha_frame, width=14, font=("Segoe UI", 10), height=4)
        self.cal.set_date(datetime.now())
        self.cal.grid(row=1, column=0, sticky="ew")

        # Columna 3: Hora
        hora_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        hora_frame.grid(row=0, column=3, sticky="ew", padx=8, pady=16)
        hora_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hora_frame,
            text="Hora",
            font=ctk.CTkFont(size=10, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.btn_hora = ctk.CTkButton(
            hora_frame,
            text=f"⏰ {self.hora_var.get()}",
            command=self.abrir_selector_hora,
            corner_radius=8,
            height=40,
            font=ctk.CTkFont(size=11)
        )
        self.btn_hora.grid(row=1, column=0, sticky="ew")

        # Columna 4: Botón Agregar
        btn_add = ctk.CTkButton(
            input_frame,
            text="➕ Agregar",
            command=self.agregar_tarea,
            corner_radius=8,
            height=40,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        btn_add.grid(row=0, column=4, sticky="ew", padx=8, pady=16)

        # Columna 5: Filtro
        filter_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        filter_frame.grid(row=0, column=5, sticky="ew", padx=(8, 20), pady=16)
        filter_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            filter_frame,
            text="Filtro",
            font=ctk.CTkFont(size=10, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.combo_filtro = ctk.CTkComboBox(
            filter_frame,
            values=["Todas"] + self.materias,
            corner_radius=8,
            height=40,
            variable=self.filtro_materia
        )
        self.combo_filtro.grid(row=1, column=0, sticky="ew")
        self.combo_filtro.bind("<<ComboboxSelected>>", lambda e: self.actualizar_tablero())

    def _construir_tablero(self):
        """Construye el tablero de columnas de tareas con ancho uniforme"""
        board_container = ctk.CTkFrame(self.root)
        board_container.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 16))
        board_container.grid_rowconfigure(0, weight=1)
        
        # Aplicar uniform a todas las columnas para anchos iguales
        for col_idx in range(len(ESTADOS)):
            board_container.grid_columnconfigure(col_idx, weight=1, uniform="columnas_tareas")

        self.columnas: dict[str, ctk.CTkScrollableFrame] = {}

        for estado in ESTADOS:
            col_frame = ctk.CTkFrame(board_container, corner_radius=15)
            col_idx = ESTADOS.index(estado)
            col_frame.grid(row=0, column=col_idx, sticky="nsew", padx=8)
            col_frame.grid_rowconfigure(1, weight=1)
            col_frame.grid_columnconfigure(0, weight=1)

            header = ctk.CTkFrame(col_frame, fg_color="transparent", corner_radius=15)
            header.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
            header.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                header,
                text=estado,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORES_ESTADO[estado]
            ).pack()

            self.columnas[estado] = ctk.CTkScrollableFrame(
                col_frame,
                corner_radius=0,
                fg_color="transparent"
            )
            self.columnas[estado].grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
            self.columnas[estado]._parent_canvas.configure(highlightthickness=0)

    def actualizar_tablero(self):
        """Actualiza el contenido del tablero mostrando las tareas filtradas"""
        for inner in self.columnas.values():
            for w in inner.winfo_children():
                w.destroy()

        for t in self.tareas:
            if self.filtro_materia.get() != "Todas" and t["materia"] != self.filtro_materia.get():
                continue

            estado = self.get_estado(t)
            inner = self.columnas[estado]

            # Crear card estilo Notion con barra lateral gruesa
            card = ctk.CTkFrame(inner, corner_radius=10, fg_color="#2B2B2B" if ctk.get_appearance_mode() == "Dark" else "#FFFFFF")
            card.pack(fill="x", pady=6, padx=2)
            card.grid_columnconfigure(1, weight=1)

            color_materia = self.colores_materias.get(t["materia"], "#CCCCCC")

            # Barra lateral (4-5px de grosor)
            barra = ctk.CTkFrame(
                card,
                width=5,
                corner_radius=10,
                fg_color=color_materia
            )
            barra.grid(row=0, column=0, sticky="ns", padx=(0, 0), pady=0)

            # Contenido
            contenido = ctk.CTkFrame(card, fg_color="transparent")
            contenido.grid(row=0, column=1, sticky="nsew", padx=12, pady=10)
            contenido.grid_columnconfigure(0, weight=1)

            # Nombre de la tarea
            nombre_label = ctk.CTkLabel(
                contenido,
                text=t["nombre"],
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="white" if ctk.get_appearance_mode() == "Dark" else "black",
                wraplength=200,
                justify="left",
                anchor="w"
            )
            nombre_label.grid(row=0, column=0, sticky="ew", pady=(0, 4))

            # Info
            info_text = f"{t['materia']} • {t['fecha'].strftime('%d/%m %H:%M')}"
            info_label = ctk.CTkLabel(
                contenido,
                text=info_text,
                font=ctk.CTkFont(size=9),
                text_color="gray70",
                anchor="w"
            )
            info_label.grid(row=1, column=0, sticky="ew", pady=(0, 8))

            # Frame de botones
            botones_frame = ctk.CTkFrame(contenido, fg_color="transparent")
            botones_frame.grid(row=2, column=0, sticky="ew")
            botones_frame.grid_columnconfigure(0, weight=1)

            # Botones de acción
            if estado != "Entregado":
                btn_entregar = ctk.CTkButton(
                    botones_frame,
                    text="✔ Entregar",
                    command=lambda tarea=t: self.cambiar_estado(tarea, True),
                    corner_radius=6,
                    height=28,
                    font=ctk.CTkFont(size=9),
                    width=60
                )
                btn_entregar.pack(side="left", padx=2)

                if estado != "Urgente":
                    btn_urgente = ctk.CTkButton(
                        botones_frame,
                        text="🔥 Urgente",
                        command=lambda tarea=t: self.marcar_urgente(tarea),
                        corner_radius=6,
                        height=28,
                        font=ctk.CTkFont(size=9),
                        width=65
                    )
                    btn_urgente.pack(side="left", padx=2)
            else:
                btn_volver = ctk.CTkButton(
                    botones_frame,
                    text="↩ Pendiente",
                    command=lambda tarea=t: self.cambiar_estado(tarea, False),
                    corner_radius=6,
                    height=28,
                    font=ctk.CTkFont(size=9),
                    width=75
                )
                btn_volver.pack(side="left", padx=2)

            # Botones de editar y eliminar
            btn_editar = ctk.CTkButton(
                botones_frame,
                text="✏",
                command=lambda tarea=t: self.editar_tarea(tarea),
                corner_radius=6,
                height=28,
                font=ctk.CTkFont(size=10),
                width=32
            )
            btn_editar.pack(side="right", padx=2)

            btn_eliminar = ctk.CTkButton(
                botones_frame,
                text="🗑",
                command=lambda tarea=t: self.eliminar_tarea(tarea),
                corner_radius=6,
                height=28,
                font=ctk.CTkFont(size=10),
                width=32,
                fg_color="red"
            )
            btn_eliminar.pack(side="right", padx=2)

    def abrir_selector_hora(self):
        """Abre diálogo para seleccionar la hora"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Seleccionar Hora")
        dialog.geometry("300x300")
        dialog.grab_set()

        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.grid_columnconfigure(0, weight=1)

        ahora_h, ahora_m = self.hora_var.get().split(":")

        ctk.CTkLabel(
            frame,
            text="Hora (0-23)",
            font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=0, column=0, sticky="w", pady=(0, 8))

        spin_h = ctk.CTkEntry(frame, corner_radius=8, height=40)
        spin_h.insert(0, ahora_h)
        spin_h.grid(row=1, column=0, sticky="ew", pady=(0, 16))

        ctk.CTkLabel(
            frame,
            text="Minutos (0-59)",
            font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=2, column=0, sticky="w", pady=(0, 8))

        spin_m = ctk.CTkEntry(frame, corner_radius=8, height=40)
        spin_m.insert(0, ahora_m)
        spin_m.grid(row=3, column=0, sticky="ew", pady=(0, 20))

        def ok():
            try:
                h = int(spin_h.get())
                m = int(spin_m.get())
                if not (0 <= h <= 23 and 0 <= m <= 59):
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Hora inválida.", parent=dialog)
                return
            self.hora_var.set(f"{h:02d}:{m:02d}")
            self.btn_hora.configure(text=f"⏰ {self.hora_var.get()}")
            dialog.destroy()

        ctk.CTkButton(
            frame,
            text="Aceptar",
            command=ok,
            corner_radius=8,
            height=40,
            font=ctk.CTkFont(size=11, weight="bold")
        ).grid(row=4, column=0, sticky="ew")

    # ==================== SYSTEM TRAY ====================
    
    def _al_cerrar_ventana(self):
        """Cancela tareas programadas y cierra la aplicación de forma segura"""
        self.closing = True
        # Cancelar todas las tareas programadas con after
        self._cancelar_tareas_after()
        # Detener la bandeja del sistema si está activa
        try:
            if self.tray_icon:
                self.tray_icon.stop()
        except Exception:
            pass
        # Ejecutar salida completa
        self._salir_aplicacion()
    
    def _cancelar_tareas_after(self):
        """Cancela todas las tareas pendientes programadas con after"""
        try:
            # Obtener todas las tareas después pendientes
            for id_tarea in self.root.after_info():
                try:
                    self.root.after_cancel(id_tarea)
                except (tk.TclError, ValueError):
                    pass
        except (AttributeError, tk.TclError):
            pass

    def _abrir_desde_bandeja(self):
        """Restaura la ventana desde la bandeja"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus()

    def _salir_aplicacion(self):
        """Cierra completamente la aplicación con salida limpia"""
        try:
            # Detener bandeja si está activa
            if self.tray_icon:
                try:
                    self.tray_icon.stop()
                except Exception:
                    pass
        except Exception:
            pass
        
        try:
            # Limpiar la interfaz
            self._cancelar_tareas_after()
            self.root.quit()
        except Exception:
            pass
        
        try:
            self.root.destroy()
        except Exception:
            pass
        
        # Salida completa sin procesos zombis
        os._exit(0)

    def _crear_icono_bandeja(self):
        """Crea el icono en la bandeja del sistema"""
        if not PYSTRAY_AVAILABLE or not PIL_AVAILABLE:
            return

        try:
            menu = Menu(
                MenuItem("📖 Abrir Gestor", self._abrir_desde_bandeja),
                MenuItem("❌ Cerrar Aplicación", self._salir_aplicacion)
            )

            imagen = Image.new("RGB", (64, 64), color=(79, 150, 255))
            draw = ImageDraw.Draw(imagen)
            draw.ellipse([8, 8, 56, 56], fill=(255, 255, 255))

            self.tray_icon = Icon("GestorTareas", imagen, menu=menu)

            def run_tray():
                try:
                    self.tray_icon.run()
                except Exception:
                    pass

            hilo_tray = threading.Thread(target=run_tray, daemon=True)
            hilo_tray.start()
        except Exception:
            pass


# ==========================
# ENTRADA
# ==========================

if __name__ == "__main__":
    # ==================== CONFIGURACIÓN ====================
    # Primero, cargar o crear perfil
    perfil = cargar_perfil()
    if not perfil:
        print("Iniciando asistente de configuración...")
        perfil = iniciar_onboarding()
        if not perfil:
            print("Configuración cancelada.")
            raise SystemExit
        print("Perfil configurado exitosamente.")
    
    # ==================== APLICACIÓN ====================
    # Luego, crear y ejecutar la aplicación principal
    print("Iniciando Gestor de Tareas...")
    root = ctk.CTk()
    app = App(root, perfil)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nCerrando aplicación...")
        app.closing = True
        root.destroy()
    finally:
        # Asegurar cierre limpio
        try:
            app._salir_aplicacion()
        except Exception:
            os._exit(0)

