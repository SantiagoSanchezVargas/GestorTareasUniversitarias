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
    from plyer.notification import notify
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

# Emojis por materia para notificaciones
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
    """
    Hilo de monitoreo que se ejecuta inmediatamente y luego cada 30 minutos.
    Verifica tareas próximas a vencer y envía notificaciones.
    """
    def ejecutar_monitoreo():
        while True:
            try:
                ahora = datetime.now()
                notificaciones_hoy = obtener_notificaciones_hoy()

                # Leer tareas.json con manejo robusto de errores
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

                # Procesar cada tarea
                for idx, t in enumerate(tareas):
                    try:
                        tarea_id = f"{t.get('nombre', '')}_{t.get('materia', '')}_{t.get('fecha', '')}"

                        if tarea_id in notificaciones_hoy:
                            continue

                        if isinstance(t.get("fecha"), str):
                            fecha = datetime.strptime(t["fecha"], "%Y-%m-%d %H:%M")
                        else:
                            fecha = t.get("fecha")

                        if not fecha:
                            continue

                        if t.get("entregado"):
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
        if not isinstance(perfil, dict):
            return None
        if not perfil.get("materias"):
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
    return setup.result


# ==========================
# CLASE CONFIGURACIÓN INICIAL
# ==========================
class ProfileSetup:
    """Asistente interactivo para configurar el perfil inicial"""
    
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("Configurar perfil")
        self.root.geometry("680x750")
        self.root.configure(bg="#edf2f7")
        self.root.resizable(True, True)
        self.result = None
        self.materia_rows = []

        # Configurar grid principal para que se adapte
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Header
        header = tk.Frame(self.root, bg="#edf2f7")
        header.grid(row=0, column=0, sticky="ew", columnspan=2)
        tk.Label(header, text="Configura tu cuenta", bg="#edf2f7", fg="#1f2937",
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=24, pady=(12, 4))
        tk.Label(header, text="Completa tu perfil y agrega las materias con colores.",
                 bg="#edf2f7", fg="#475569", font=("Segoe UI", 10)).pack(anchor="w", padx=24, pady=(0, 12))

        # Canvas scrolleable responsive
        canvas = tk.Canvas(self.root, bg="#edf2f7", bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#edf2f7")

        # Configurar grid en scrollable_frame para que ocupe todo el ancho
        scrollable_frame.grid_columnconfigure(0, weight=1)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Actualizar ancho del canvas cuando se redimensiona la ventana
        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<Configure>", _on_canvas_configure)

        # Vincular rueda del ratón
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(0, 10))

        # Contenido dentro del frame scrolleable - usar grid para mejor control
        card = tk.Frame(scrollable_frame, bg="white", bd=0, highlightthickness=0)
        card.grid(row=0, column=0, sticky="ew", padx=0, pady=10)
        card.grid_columnconfigure(0, weight=1)

        steps_frame = tk.Frame(card, bg="white")
        steps_frame.grid(row=0, column=0, sticky="ew", pady=(20, 12), padx=20)
        steps_frame.grid_columnconfigure(0, weight=1)
        tk.Label(steps_frame, text="1. Datos personales", bg="white", fg="#0f172a",
                 font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(steps_frame, text="2. Materias y colores", bg="white", fg="#0f172a",
                 font=("Segoe UI", 11, "bold")).grid(row=0, column=1, sticky="w", padx=60)

        separator = ttk.Separator(card, orient="horizontal")
        separator.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 12))

        form_frame = tk.Frame(card, bg="white")
        form_frame.grid(row=2, column=0, sticky="ew", padx=20)
        form_frame.grid_columnconfigure(0, weight=1)

        # Fila 1: Nombre del estudiante
        label_nombre = tk.Label(form_frame, text="Nombre del estudiante", bg="white", fg="#334155",
                                font=("Segoe UI", 9, "bold"))
        label_nombre.grid(row=0, column=0, sticky="w")
        self.entry_nombre = tk.Entry(form_frame, font=("Segoe UI", 10), bd=0,
                                     relief="flat", bg="#f8fafc")
        self.entry_nombre.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # Fila 2: Perfil / Carrera
        label_carrera = tk.Label(form_frame, text="Perfil / Carrera", bg="white", fg="#334155",
                                font=("Segoe UI", 9, "bold"))
        label_carrera.grid(row=2, column=0, sticky="w")
        self.entry_carrera = tk.Entry(form_frame, font=("Segoe UI", 10), bd=0,
                                      relief="flat", bg="#f8fafc")
        self.entry_carrera.grid(row=3, column=0, sticky="ew", pady=(0, 10))

        # Materias dinámicas
        label_materias = tk.Label(card, text="Materias dinámicas", bg="white", fg="#334155",
                 font=("Segoe UI", 11, "bold"))
        label_materias.grid(row=3, column=0, sticky="w", padx=20, pady=(14, 4))
        
        label_desc = tk.Label(card, text="Define tus materias y elige el color que las represente.",
                 bg="white", fg="#64748b", font=("Segoe UI", 9))
        label_desc.grid(row=4, column=0, sticky="w", padx=20)

        materias_container = tk.Frame(card, bg="#f8fafc", bd=1, relief="solid")
        materias_container.grid(row=5, column=0, sticky="ew", padx=20, pady=(10, 12))
        materias_container.grid_columnconfigure(0, weight=1)

        header_row = tk.Frame(materias_container, bg="#f8fafc")
        header_row.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 0))
        header_row.grid_columnconfigure(0, weight=1)
        tk.Label(header_row, text="Materia", bg="#f8fafc", fg="#475569",
                 font=("Segoe UI", 9, "bold"), anchor="w").grid(row=0, column=0, sticky="ew")
        tk.Label(header_row, text="Color", bg="#f8fafc", fg="#475569",
                 font=("Segoe UI", 9, "bold"), width=12, anchor="w").grid(row=0, column=1, padx=(0, 8))
        tk.Label(header_row, text="", bg="#f8fafc", width=10).grid(row=0, column=2)

        self.frame_materias = tk.Frame(materias_container, bg="#f8fafc")
        self.frame_materias.grid(row=1, column=0, sticky="ew", padx=14, pady=(8, 12))
        self.frame_materias.grid_columnconfigure(0, weight=1)

        action_row = tk.Frame(card, bg="white")
        action_row.grid(row=6, column=0, sticky="ew", padx=20, pady=(0, 12))
        action_row.grid_columnconfigure(0, weight=1)
        
        self.btn_add_materia = tk.Button(action_row, text="Agregar materia +", bg="#2563eb", fg="white",
                                         font=("Segoe UI", 10, "bold"), bd=0, activebackground="#1d4ed8",
                                         padx=14, pady=8, command=self.agregar_materia_fila)
        self.btn_add_materia.grid(row=0, column=0, sticky="w")

        btn_guardar = tk.Button(action_row, text="Guardar y Comenzar", bg="#14b8a6", fg="white",
                                font=("Segoe UI", 11, "bold"), bd=0, activebackground="#0d9488",
                                padx=18, pady=10, command=self.guardar)
        btn_guardar.grid(row=0, column=0, sticky="e")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.agregar_materia_fila()

    def agregar_materia_fila(self, nombre="", color="#6EC1FF"):
        row_num = len(self.materia_rows)
        row = tk.Frame(self.frame_materias, bg="white", bd=1, relief="solid")
        row.grid(row=row_num, column=0, sticky="ew", pady=6, ipady=6)
        row.grid_columnconfigure(0, weight=1)

        entry = tk.Entry(row, font=("Segoe UI", 10), bd=0, relief="flat", bg="#f8fafc")
        entry.insert(0, nombre)
        entry.grid(row=0, column=0, sticky="ew", padx=(12, 10), pady=8)

        color_var = tk.StringVar(value=color)
        btn_color = tk.Button(row, text="", bg=color, width=3, bd=0,
                              command=lambda: self.elegir_color(color_var, btn_color))
        btn_color.grid(row=0, column=1, padx=(0, 10), sticky="e")

        color_label = tk.Label(row, text=color, bg="#f8fafc", fg="#334155",
                               font=("Segoe UI", 9), width=12)
        color_label.grid(row=0, column=2, padx=(0, 20), sticky="w")

        btn_quitar = tk.Button(row, text="✕", bg="#ef4444", fg="white", width=3, bd=0,
                               activebackground="#dc2626",
                               command=lambda: self.quitar_materia_fila(row))
        btn_quitar.grid(row=0, column=3, padx=10, pady=8, sticky="e")

        def actualizar_color_label(*args):
            color_label.config(text=color_var.get())

        color_var.trace_add("write", actualizar_color_label)
        self.materia_rows.append({"frame": row, "entry": entry, "color_var": color_var, "button": btn_color})

    def quitar_materia_fila(self, row):
        for item in self.materia_rows:
            if item["frame"] is row:
                item["frame"].destroy()
                self.materia_rows.remove(item)
                # Reconfigure grid para las filas restantes
                for idx, row_data in enumerate(self.materia_rows):
                    row_data["frame"].grid(row=idx, column=0, sticky="ew", pady=6, ipady=6)
                return

    def elegir_color(self, color_var, btn):
        _, color = colorchooser.askcolor(initialcolor=color_var.get(), parent=self.root)
        if color:
            color_var.set(color)
            btn.config(bg=color)

    def guardar(self):
        nombre = self.entry_nombre.get().strip()
        carrera = self.entry_carrera.get().strip()
        materias = []
        for item in self.materia_rows:
            materia = item["entry"].get().strip()
            color = item["color_var"].get()
            if materia:
                materias.append({"nombre": materia, "color": color})

        if not nombre:
            messagebox.showwarning("Atención", "Escribe el nombre del estudiante.", parent=self.root)
            return
        if not carrera:
            messagebox.showwarning("Atención", "Escribe el perfil / carrera.", parent=self.root)
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
    def __init__(self, root: tk.Tk, profile: dict):
        self.root = root
        self.root.title("Gestor de Tareas")
        self.root.geometry("1200x650")
        self.root.configure(bg="#cfe9ff")
        self.filtro_materia = tk.StringVar(value="Todas")
        self.tareas: list[dict] = []
        self.hora_var = tk.StringVar(value="12:00")
        self.profile_image = None
        self.profile = profile
        self.usuario = profile.get("nombre", USUARIO)
        self.carrera = profile.get("carrera", "")
        self.materias = [m["nombre"] for m in profile.get("materias", [])] or MATERIAS
        self.colores_materias = {m["nombre"]: m["color"] for m in profile.get("materias", [])}
        self.profile_photo_path = profile.get("foto")
        self.tray_icon = None

        # Protocolo para manejar cierre de ventana (minimizar a bandeja)
        self.root.protocol("WM_DELETE_WINDOW", self._al_cerrar_ventana)

        self._cargar_tareas()
        self._construir_ui()
        self.actualizar_tablero()

        # Iniciar hilo de monitoreo de tareas
        monitoreo_tareas_background(ARCHIVO)

        # Crear icono en la bandeja del sistema (System Tray)
        self.root.after(100, self._crear_icono_bandeja)

    # ----------------------
    # PERSISTENCIA
    # ----------------------
    def _cargar_tareas(self):
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
            else:
                tareas = []

            for t in tareas:
                t["fecha"] = datetime.strptime(t["fecha"], "%Y-%m-%d %H:%M")
                self.tareas.append(t)
        except (json.JSONDecodeError, KeyError, ValueError, OSError):
            self.tareas = []
            self._crear_archivo_tareas()

    def _crear_archivo_tareas(self):
        with open(ARCHIVO, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)

    def _guardar_tareas(self):
        with open(ARCHIVO, "w", encoding="utf-8") as f:
            json.dump(
                [{**t, "fecha": t["fecha"].strftime("%Y-%m-%d %H:%M")} for t in self.tareas],
                f, indent=4,
                ensure_ascii=False
            )

    def _mostrar_avatar_por_ruta(self, ruta: str):
        self.avatar_canvas.delete("all")
        self.avatar_canvas.create_oval(4, 4, 86, 86, fill="#d6ecff", outline="#4D96FF", width=3)

        if PIL_AVAILABLE:
            try:
                imagen = Image.open(ruta).convert("RGBA")
            except Exception:
                return

            ancho, alto = imagen.size
            lado = min(ancho, alto)
            izquierda = (ancho - lado) // 2
            superior = (alto - lado) // 2
            imagen = imagen.crop((izquierda, superior, izquierda + lado, superior + lado))
            imagen = imagen.resize((80, 80), Image.LANCZOS)

            from PIL import ImageDraw
            mask = Image.new("L", (80, 80), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 80, 80), fill=255)
            imagen.putalpha(mask)

            self.profile_image = ImageTk.PhotoImage(imagen)
        else:
            try:
                self.profile_image = tk.PhotoImage(file=ruta)
            except tk.TclError:
                return

        self.avatar_canvas.create_image(45, 45, image=self.profile_image)
        self.avatar_canvas.image = self.profile_image

    # ----------------------
    # LÓGICA DE ESTADO
    # ----------------------
    @staticmethod
    def get_estado(t: dict) -> str:
        ahora = datetime.now()
        diff = t["fecha"] - ahora

        if t["entregado"]:
            return "Entregado"

        if diff <= timedelta(0):
            return "Vencido"

        # 🔥 Forzado manual
        if t.get("manual") == "Urgente":
            return "Urgente"

        # 🔴 Urgente: faltan 4 días o menos
        if diff <= timedelta(days=4):
            return "Urgente"

        # 🔵 Próximo: misma semana
        if t["fecha"].isocalendar()[1] == ahora.isocalendar()[1]:
            return "Proximo"

        return "Pendiente"
    # ----------------------
    # ACCIONES
    # ----------------------
    def agregar_tarea(self):
        nombre = self.entry_nombre.get().strip()
        materia = self.combo_materia.get()

        if not nombre or nombre == "Nombre de la tarea":
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
        self.entry_nombre.delete(0, tk.END)

    def cambiar_estado(self, t: dict, entregado: bool):
        t["entregado"] = entregado
        t["manual"] = None
        self._guardar_tareas()
        self.actualizar_tablero()

    def marcar_urgente(self, t: dict):
        t["manual"] = "Urgente"
        self._guardar_tareas()
        self.actualizar_tablero()

    def eliminar_tarea(self, t: dict):
        if not messagebox.askyesno("Confirmar", f"¿Eliminar '{t['nombre']}'?"):
            return
        try:
            self.tareas.remove(t)
        except ValueError:
            pass  # ya fue eliminada (doble clic rápido)
        self._guardar_tareas()
        self.actualizar_tablero()

    def editar_tarea(self, t: dict):
        """Abre una ventana para editar nombre, materia y fecha/hora."""
        v = tk.Toplevel(self.root)
        v.title("Editar tarea")
        v.geometry("320x240")
        v.configure(bg="#e6f7ff")
        v.grab_set()  # modal

        tk.Label(v, text="Nombre", bg="#e6f7ff").pack(pady=(12, 2))
        entry = tk.Entry(v, width=36)
        entry.insert(0, t["nombre"])
        entry.pack()

        tk.Label(v, text="Materia", bg="#e6f7ff").pack(pady=(8, 2))
        combo = ttk.Combobox(v, values=MATERIAS, state="readonly", width=33)
        combo.set(t["materia"])
        combo.pack()

        tk.Label(v, text="Hora (HH:MM)", bg="#e6f7ff").pack(pady=(8, 2))
        hora_e = tk.Entry(v, width=10)
        hora_e.insert(0, t["fecha"].strftime("%H:%M"))
        hora_e.pack()

        def guardar():
            nuevo_nombre = entry.get().strip()
            nueva_materia = combo.get()
            if not nuevo_nombre or not nueva_materia:
                messagebox.showwarning("Atención", "Completa todos los campos.", parent=v)
                return
            try:
                nueva_hora = datetime.strptime(hora_e.get(), "%H:%M")
            except ValueError:
                messagebox.showerror("Error", "Formato de hora inválido (HH:MM).", parent=v)
                return
            t["nombre"] = nuevo_nombre
            t["materia"] = nueva_materia
            t["fecha"] = t["fecha"].replace(hour=nueva_hora.hour, minute=nueva_hora.minute)
            self._guardar_tareas()
            self.actualizar_tablero()
            v.destroy()

        tk.Button(v, text="Guardar", bg="#4D96FF", fg="white", command=guardar).pack(pady=12)

    # ----------------------
    # MENÚ CONTEXTUAL
    # ----------------------
    def mostrar_menu(self, event, t: dict):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="✏ Editar",     command=lambda: self.editar_tarea(t))
        menu.add_separator()
        menu.add_command(label="🔥 Urgente",   command=lambda: self.marcar_urgente(t))
        menu.add_command(label="✔ Entregado",  command=lambda: self.cambiar_estado(t, True))
        menu.add_command(label="↩ Pendiente",  command=lambda: self.cambiar_estado(t, False))
        menu.add_separator()
        menu.add_command(label="🗑 Eliminar",  command=lambda: self.eliminar_tarea(t))
        menu.tk_popup(event.x_root, event.y_root)

    # ----------------------
    # SELECTOR DE HORA
    # ----------------------
    def abrir_selector_hora(self):
        v = tk.Toplevel(self.root)
        v.title("Seleccionar hora")
        v.geometry("220x180")
        v.configure(bg="#e6f7ff")
        v.grab_set()

        # Inicializar con la hora actual
        ahora_h, ahora_m = self.hora_var.get().split(":")

        tk.Label(v, text="Hora (0-23)", bg="#e6f7ff").pack(pady=(16, 2))
        spin_h = tk.Spinbox(v, from_=0, to=23, format="%02.0f", width=6)
        spin_h.delete(0, tk.END)
        spin_h.insert(0, ahora_h)
        spin_h.pack()

        tk.Label(v, text="Minutos (0-59)", bg="#e6f7ff").pack(pady=(8, 2))
        spin_m = tk.Spinbox(v, from_=0, to=59, format="%02.0f", width=6)
        spin_m.delete(0, tk.END)
        spin_m.insert(0, ahora_m)
        spin_m.pack()

        def ok():
            try:
                h = int(spin_h.get())
                m = int(spin_m.get())
                if not (0 <= h <= 23 and 0 <= m <= 59):
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Hora inválida.", parent=v)
                return
            self.hora_var.set(f"{h:02d}:{m:02d}")
            self.btn_hora.config(text=f"⏰ {self.hora_var.get()}")
            v.destroy()

        tk.Button(v, text="Aceptar", bg="#6EC1FF", command=ok).pack(pady=12)

    def poner_hora_actual(self):
        ahora = datetime.now()
        self.hora_var.set(ahora.strftime("%H:%M"))
        self.btn_hora.config(text=f"⏰ {self.hora_var.get()}")

    def cambiar_foto_perfil(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar foto de perfil",
            filetypes=[
                ("Imagen PNG/GIF/JPEG", "*.png *.gif *.jpg *.jpeg"),
                ("Todos los archivos", "*.*")
            ]
        )
        if not ruta:
            return

        self.avatar_canvas.delete("all")
        self.avatar_canvas.create_oval(4, 4, 86, 86, fill="#d6ecff", outline="#4D96FF", width=3)

        if PIL_AVAILABLE:
            try:
                imagen = Image.open(ruta).convert("RGBA")
            except Exception:
                messagebox.showerror("Error", "No se pudo abrir la imagen.")
                return

            ancho, alto = imagen.size
            lado = min(ancho, alto)
            izquierda = (ancho - lado) // 2
            superior = (alto - lado) // 2
            imagen = imagen.crop((izquierda, superior, izquierda + lado, superior + lado))
            imagen = imagen.resize((80, 80), Image.LANCZOS)

            from PIL import ImageDraw
            mask = Image.new("L", (80, 80), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, 80, 80), fill=255)
            imagen.putalpha(mask)

            self.profile_image = ImageTk.PhotoImage(imagen)
            self.avatar_canvas.create_image(45, 45, image=self.profile_image)
            self.avatar_canvas.image = self.profile_image
        else:
            if not self._mostrar_avatar_por_ruta(ruta):
                try:
                    imagen = tk.PhotoImage(file=ruta)
                except tk.TclError:
                    messagebox.showerror("Error", "Solo se admiten archivos PNG o GIF si Pillow no está instalado.")
                    return
                self.profile_image = imagen
                self.avatar_canvas.create_image(45, 45, image=self.profile_image)
                self.avatar_canvas.image = self.profile_image

        self.profile_photo_path = ruta
        self.profile["foto"] = ruta
        guardar_perfil(self.profile)

    # ----------------------
    # RELOJ ANALÓGICO
    # ----------------------
    def dibujar_reloj(self):
        """Dibuja el reloj analógico en el canvas."""
        self.canvas_reloj.delete("all")
        
        # Obtener tamaño del canvas
        ancho = self.canvas_reloj.winfo_width()
        alto = self.canvas_reloj.winfo_height()
        
        if ancho < 2:  # Canvas no iniciado aún
            self.canvas_reloj.after(100, self.dibujar_reloj)
            return
        
        # Centro y radio
        cx, cy = ancho // 2, alto // 2
        radio = min(ancho, alto) // 2 - 8
        
        # Fondo con efecto Vista (degradado)
        self.canvas_reloj.create_oval(
            cx - radio, cy - radio, cx + radio, cy + radio,
            fill="#e6f4ff", outline="#9dd4e8", width=2
        )
        
        # Circulo interior (efecto vidrio)
        self.canvas_reloj.create_oval(
            cx - radio + 3, cy - radio + 3, cx + radio - 3, cy + radio - 3,
            fill="#f0faff", outline="", width=0
        )
        
        # Marcas de horas
        for i in range(12):
            angulo = math.radians(i * 30 - 90)
            x1 = cx + (radio - 12) * math.cos(angulo)
            y1 = cy + (radio - 12) * math.sin(angulo)
            x2 = cx + (radio - 4) * math.cos(angulo)
            y2 = cy + (radio - 4) * math.sin(angulo)
            self.canvas_reloj.create_line(x1, y1, x2, y2, fill="#003366", width=2)
        
        # Obtener hora actual
        ahora = datetime.now()
        horas = ahora.hour % 12
        minutos = ahora.minute
        segundos = ahora.second
        
        # Cálculo de ángulos
        angulo_h = math.radians(horas * 30 + minutos * 0.5 - 90)
        angulo_m = math.radians(minutos * 6 + segundos * 0.1 - 90)
        angulo_s = math.radians(segundos * 6 - 90)
        
        # Manecilla de horas (corta y gruesa)
        x_h = cx + (radio * 0.5) * math.cos(angulo_h)
        y_h = cy + (radio * 0.5) * math.sin(angulo_h)
        self.canvas_reloj.create_line(
            cx, cy, x_h, y_h, fill="#003366", width=6, capstyle="round"
        )
        
        # Manecilla de minutos (larga y delgada)
        x_m = cx + (radio * 0.7) * math.cos(angulo_m)
        y_m = cy + (radio * 0.7) * math.sin(angulo_m)
        self.canvas_reloj.create_line(
            cx, cy, x_m, y_m, fill="#0084c4", width=4, capstyle="round"
        )
        
        # Manecilla de segundos (muy delgada, roja)
        x_s = cx + (radio * 0.75) * math.cos(angulo_s)
        y_s = cy + (radio * 0.75) * math.sin(angulo_s)
        self.canvas_reloj.create_line(
            cx, cy, x_s, y_s, fill="#ff6b6b", width=1
        )
        
        # Centro (bulto)
        self.canvas_reloj.create_oval(
            cx - 6, cy - 6, cx + 6, cy + 6,
            fill="#003366", outline="#0084c4", width=2
        )
        
        # Hora digital debajo
        texto_hora = ahora.strftime("%H:%M:%S")
        self.canvas_reloj.create_text(
            cx, cy + radio + 20,
            text=texto_hora,
            fill="#003366",
            font=("Segoe UI", 10, "bold")
        )
        
        # Actualizar cada 1000ms (1 segundo)
        self.canvas_reloj.after(1000, self.dibujar_reloj)

    # ----------------------
    # TABLERO
    # ----------------------
    def actualizar_tablero(self):
        for inner in self.columnas.values():
            for w in inner.winfo_children():
                w.destroy()

        for t in self.tareas:
            if self.filtro_materia.get() != "Todas" and t["materia"] != self.filtro_materia.get():
                continue
            estado = self.get_estado(t)

            inner = self.columnas[estado]
            borde = 2 if estado == "Urgente" else 1
            if estado == "Entregado":
                card = tk.Frame(inner, bg="#f4f7f9", bd=borde, relief="groove")
            else:
                card = tk.Frame(inner, bg="white", bd=borde, relief="solid")
            card.pack(fill="x", padx=8, pady=5)

            color_materia = self.colores_materias.get(t["materia"], "#ddd")
            color_estado  = COLORES_ESTADO[estado]

            barra = tk.Frame(card, bg=color_estado, width=6)
            barra.pack(side="left", fill="y")

            contenido = tk.Frame(card, bg=color_materia)
            contenido.pack(side="left", fill="both", expand=True)

            lbl_nombre = tk.Label(
                contenido,
                text=t["nombre"],
                bg=color_materia,
                fg="black",
                font=("Segoe UI", 10, "bold"),
                padx=6, anchor="w",
                wraplength=160,
                justify="left",
            )
            lbl_nombre.pack(fill="x")

            lbl_info = tk.Label(
                contenido,
                text=f"{t['materia']} • {t['fecha'].strftime('%d/%m %H:%M')}",
                bg=color_materia,
                fg="#444",
                font=("Segoe UI", 8),
                padx=6, anchor="w",
            )
            lbl_info.pack(fill="x")

            for widget in (card, barra, contenido, lbl_nombre, lbl_info):
                widget.bind("<Button-3>", lambda e, tarea=t: self.mostrar_menu(e, tarea))
    # ----------------------
    # UI
    # ----------------------
    def _construir_ui(self):
        # Encabezado principal con reloj
        frame_encabezado = tk.Frame(self.root, bg="#cfe9ff", pady=10)
        frame_encabezado.pack(fill="x", padx=10)
        
        # Lado izquierdo: Avatar y textos
        frame_izq = tk.Frame(frame_encabezado, bg="#cfe9ff")
        frame_izq.pack(side="left", fill="both", expand=True)

        frame_avatar = tk.Frame(frame_izq, bg="#cfe9ff")
        frame_avatar.pack(side="left", anchor="w")

        self.avatar_canvas = tk.Canvas(
            frame_avatar,
            width=90, height=90,
            bg="#f0f7ff", highlightthickness=0
        )
        self.avatar_canvas.create_oval(4, 4, 86, 86, fill="#d6ecff", outline="#4D96FF", width=3)
        self.avatar_canvas.create_text(45, 47, text="S", font=("Segoe UI", 28, "bold"), fill="#003366")
        self.avatar_canvas.pack()
        self.avatar_canvas.bind("<Button-3>", lambda e: self.cambiar_foto_perfil())

        if self.profile_photo_path and os.path.exists(self.profile_photo_path):
            self._mostrar_avatar_por_ruta(self.profile_photo_path)

        frame_identidad = tk.Frame(frame_izq, bg="#cfe9ff")
        frame_identidad.pack(side="left", padx=12, anchor="w")

        tk.Label(
            frame_identidad,
            text=f"👋 Hola, {self.usuario}",
            bg="#cfe9ff", fg="#003366",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w")

        tk.Label(
            frame_identidad,
            text=f"📚 {self.carrera}",
            bg="#cfe9ff", fg="#005b96",
            font=("Segoe UI", 12)
        ).pack(anchor="w", pady=(4, 0))

        tk.Label(
            frame_identidad,
            text="(clic derecho en la foto para cambiar)",
            bg="#cfe9ff", fg="#005b96",
            font=("Segoe UI", 8, "italic")
        ).pack(anchor="w", pady=(4, 0))
        
        # Lado derecho: Reloj analógico
        self.canvas_reloj = tk.Canvas(
            frame_encabezado,
            width=140, height=140,
            bg="#cfe9ff", highlightthickness=0
        )
        self.canvas_reloj.pack(side="right", padx=20)
        
        # Iniciar reloj
        self.canvas_reloj.after(100, self.dibujar_reloj)

        # Panel de inputs
        frame_inputs = tk.LabelFrame(self.root, text="Nueva tarea", bg="#e6f7ff",
                                     fg="#003366", font=("Segoe UI", 10, "bold"),
                                     labelanchor="n", padx=12, pady=10)
        frame_inputs.pack(fill="x", padx=10, pady=(0, 10))

        row_nombre = tk.Frame(frame_inputs, bg="#e6f7ff")
        row_nombre.pack(fill="x", pady=(0, 8))
        tk.Label(row_nombre, text="Nombre", bg="#e6f7ff", fg="#003366").pack(anchor="w", padx=4)
        self.entry_nombre = tk.Entry(row_nombre, width=40, font=("Segoe UI", 10))
        self.entry_nombre.pack(side="left", padx=4, ipady=5)
        self._crear_entry_placeholder(self.entry_nombre, "Nombre de la tarea")
        self.entry_nombre.bind("<Return>", lambda _: self.agregar_tarea())

        row_detalles = tk.Frame(frame_inputs, bg="#e6f7ff")
        row_detalles.pack(fill="x", pady=(0, 8))
        materia_frame = tk.Frame(row_detalles, bg="#e6f7ff")
        materia_frame.pack(side="left", padx=4, fill="x", expand=True)
        tk.Label(materia_frame, text="Materia", bg="#e6f7ff", fg="#003366").pack(anchor="w")
        self.combo_materia = ttk.Combobox(
            materia_frame, values=self.materias, state="readonly", width=28
        )
        self.combo_materia.pack(fill="x")

        fecha_frame = tk.Frame(row_detalles, bg="#e6f7ff")
        fecha_frame.pack(side="left", padx=4)
        tk.Label(fecha_frame, text="Fecha", bg="#e6f7ff", fg="#003366").pack(anchor="w")
        self.cal = DateEntry(fecha_frame, width=14)
        self.cal.pack()
        self.cal.set_date(datetime.now())

        hora_frame = tk.Frame(row_detalles, bg="#e6f7ff")
        hora_frame.pack(side="left", padx=4)
        tk.Label(hora_frame, text="Hora", bg="#e6f7ff", fg="#003366").pack(anchor="w")
        self.btn_hora = tk.Button(
            hora_frame,
            text=f"⏰ {self.hora_var.get()}",
            bg="#6EC1FF",
            fg="white",
            relief="groove",
            command=self.abrir_selector_hora,
            padx=6
        )
        self.btn_hora.pack(fill="x")
        self._hover(self.btn_hora, "#6EC1FF", "#4DB8FF")

        row_acciones = tk.Frame(frame_inputs, bg="#e6f7ff")
        row_acciones.pack(fill="x")
        self.btn_hora_ahora = tk.Button(
            row_acciones,
            text="⏱ Hora actual",
            bg="#d6ecff",
            fg="#003366",
            command=self.poner_hora_actual,
            relief="flat",
            padx=10,
            pady=6
        )
        self.btn_hora_ahora.pack(side="left", padx=(4, 8))
        self._hover(self.btn_hora_ahora, "#d6ecff", "#c2f0ff")

        btn_add = tk.Button(
            row_acciones,
            text="➕ Agregar tarea",
            bg="#4D96FF", fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.agregar_tarea,
            padx=12, pady=6
        )
        btn_add.pack(side="left", padx=4)
        self._hover(btn_add, "#4D96FF", "#6EC1FF")

        filtro_frame = tk.Frame(row_acciones, bg="#e6f7ff")
        filtro_frame.pack(side="right", fill="x", expand=True)
        tk.Label(filtro_frame, text="Filtro materia", bg="#e6f7ff", fg="#003366").pack(anchor="e")
        self.combo_filtro = ttk.Combobox(
            filtro_frame,
            values=["Todas"] + self.materias,
            state="readonly",
            width=24,
            textvariable=self.filtro_materia
        )
        self.combo_filtro.pack(anchor="e")
        self.combo_filtro.bind("<<ComboboxSelected>>", lambda e: self.actualizar_tablero())

        # Tablero de columnas con scroll horizontal
        board_container = tk.Frame(self.root, bg="#cfe9ff")
        board_container.pack(fill="both", expand=True, padx=6, pady=8)

        board_canvas = tk.Canvas(board_container, bg="#cfe9ff", highlightthickness=0)
        board_canvas.pack(side="top", fill="both", expand=True)
        h_scroll = tk.Scrollbar(board_container, orient="horizontal", command=board_canvas.xview)
        board_canvas.configure(xscrollcommand=h_scroll.set)
        h_scroll.pack(side="bottom", fill="x")

        board = tk.Frame(board_canvas, bg="#cfe9ff")
        window_id = board_canvas.create_window((0, 0), window=board, anchor="nw")

        def _on_board_configure(event, canvas=board_canvas, win=window_id):
            canvas.configure(scrollregion=canvas.bbox("all"))
        board.bind("<Configure>", _on_board_configure)

        self.columnas: dict[str, tk.Frame] = {}
        for estado in ESTADOS:
            col_frame = tk.Frame(board, bg="#e6f7ff", bd=1, relief="solid")
            col_frame.pack(side="left", fill="both", expand=True, padx=4)

            # Cabecera con color del estado
            hdr = tk.Frame(col_frame, bg=COLORES_ESTADO[estado])
            hdr.pack(fill="x")
            tk.Label(
                hdr, text=estado,
                bg=COLORES_ESTADO[estado], fg="#003366",
                font=("Segoe UI", 10, "bold"), pady=4
            ).pack()

            # Canvas + scrollbar para scroll vertical
            canvas = tk.Canvas(col_frame, bg="#e6f7ff", highlightthickness=0)
            scrollbar = tk.Scrollbar(col_frame, orient="vertical", command=canvas.yview)
            canvas.configure(yscrollcommand=scrollbar.set)

            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)

            inner = tk.Frame(canvas, bg="#e6f7ff")
            window_id = canvas.create_window((0, 0), window=inner, anchor="nw")

            def _on_configure(event, c=canvas, wid=window_id):
                c.configure(scrollregion=c.bbox("all"))
                c.itemconfig(wid, width=c.winfo_width())

            inner.bind("<Configure>", _on_configure)
            canvas.bind("<Configure>", lambda e, c=canvas, wid=window_id:
                        c.itemconfig(wid, width=c.winfo_width()))

            # Scroll con rueda del mouse
            def _mousewheel(event, c=canvas):
                c.yview_scroll(int(-1 * (event.delta / 120)), "units")

            canvas.bind("<MouseWheel>", _mousewheel)
            inner.bind("<MouseWheel>", _mousewheel)

            self.columnas[estado] = inner

    def _crear_entry_placeholder(self, entry: tk.Entry, texto: str):
        entry.insert(0, texto)
        entry.config(fg="#6a6a6a")

        def on_focus_in(event):
            if entry.get() == texto:
                entry.delete(0, tk.END)
                entry.config(fg="black")

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, texto)
                entry.config(fg="#6a6a6a")

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    # ----------------------
    # SYSTEM TRAY
    # ----------------------
    def _al_cerrar_ventana(self):
        """Minimiza la ventana a la bandeja en lugar de cerrar."""
        self.root.withdraw()

    def _abrir_desde_bandeja(self):
        """Restaura la ventana desde la bandeja."""
        self.root.deiconify()
        self.root.lift()
        self.root.focus()

    def _salir_aplicacion(self):
        """Cierra completamente la aplicación."""
        try:
            if self.tray_icon:
                self.tray_icon.stop()
        except Exception:
            pass
        os._exit(0)

    def _crear_icono_bandeja(self):
        """Crea el icono en la bandeja del sistema (System Tray)."""
        if not PYSTRAY_AVAILABLE:
            return

        try:
            # Crear menú con opciones
            menu = Menu(
                MenuItem("Abrir", self._abrir_desde_bandeja),
                MenuItem("Salir", self._salir_aplicacion)
            )

            # Crear icono (usa un píxel de 16x16 como placeholder)
            from PIL import Image
            imagen = Image.new("RGB", (64, 64), color=(79, 150, 255))  # Color azul
            self.tray_icon = Icon("GestorTareas", imagen, menu=menu)

            # Ejecutar el icono en un hilo separado
            def run_tray():
                try:
                    self.tray_icon.run()
                except Exception:
                    pass

            hilo_tray = threading.Thread(target=run_tray, daemon=True)
            hilo_tray.start()
        except Exception:
            pass  # Ignorar si falla la creación del icono

    @staticmethod
    def _hover(btn: tk.Button, c1: str, c2: str):
        btn.bind("<Enter>", lambda _: btn.config(bg=c2))
        btn.bind("<Leave>", lambda _: btn.config(bg=c1))


# ==========================
# ENTRADA
# =========================
if __name__ == "__main__":
    perfil = cargar_perfil()
    if not perfil:
        perfil = iniciar_onboarding()
        if not perfil:
            raise SystemExit

    root = tk.Tk()
    App(root, perfil)
    root.mainloop()
