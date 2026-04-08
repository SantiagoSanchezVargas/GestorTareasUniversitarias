import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import json, os
import math

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ==========================
# CONFIG
# ==========================
ARCHIVO = "tareas.json"
USUARIO = "Santiago"

MATERIAS = [
    "Operativa",
    "Big Data",
    "Analisis numerico",
    "Comunicación de datos",
    "Emprendimiento e innovación",
    "Ciencia, tecnología e innovación",
    "Seguridad en hardware",
]

COLORES_MATERIAS = {
    "Operativa": "#6EC1FF",
    "Big Data": "#7CFFB2",
    "Analisis numerico": "#BFA6FF",
    "Comunicación de datos": "#8ED1FC",
    "Emprendimiento e innovación": "#FFE066",
    "Ciencia, tecnología e innovación": "#A0E7E5",
    "Seguridad en hardware": "#FF8FA3",
}

COLORES_ESTADO = {
    "Pendiente": "#d6ecff",
    "Proximo":   "#c2f0ff",
    "Urgente":   "#ffb3b3",
    "Vencido":   "#ff8c8c",
    "Entregado": "#caffbf",
}

ESTADOS = ["Pendiente", "Proximo", "Urgente", "Vencido", "Entregado"]


# ==========================
# CLASE PRINCIPAL
# ==========================
class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Gestor de Tareas")
        self.root.geometry("1200x650")
        self.root.configure(bg="#cfe9ff")
        self.filtro_materia = tk.StringVar(value="Todas")
        self.tareas: list[dict] = []
        self.hora_var = tk.StringVar(value="12:00")
        self.profile_image = None

        self._cargar_tareas()
        self._construir_ui()
        self.actualizar_tablero()

    # ----------------------
    # PERSISTENCIA
    # ----------------------
    def _cargar_tareas(self):
        if not os.path.exists(ARCHIVO):
            return
        try:
            with open(ARCHIVO) as f:
                for t in json.load(f):
                    t["fecha"] = datetime.strptime(t["fecha"], "%Y-%m-%d %H:%M")
                    self.tareas.append(t)
        except (json.JSONDecodeError, KeyError, ValueError):
            messagebox.showerror("Error", "No se pudo cargar el archivo de tareas.")

    def _guardar_tareas(self):
        with open(ARCHIVO, "w") as f:
            json.dump(
                [{**t, "fecha": t["fecha"].strftime("%Y-%m-%d %H:%M")} for t in self.tareas],
                f, indent=4
            )

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
            try:
                imagen = tk.PhotoImage(file=ruta)
            except tk.TclError:
                messagebox.showerror("Error", "Solo se admiten archivos PNG o GIF si Pillow no está instalado.")
                return
            self.profile_image = imagen
            self.avatar_canvas.create_image(45, 45, image=self.profile_image)
            self.avatar_canvas.image = self.profile_image

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

            color_materia = COLORES_MATERIAS.get(t["materia"], "#ddd")
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

        frame_identidad = tk.Frame(frame_izq, bg="#cfe9ff")
        frame_identidad.pack(side="left", padx=12, anchor="w")

        tk.Label(
            frame_identidad,
            text=f"👋 Hola, {USUARIO}",
            bg="#cfe9ff", fg="#003366",
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w")

        tk.Label(
            frame_identidad,
            text="📚 Gestor de tareas universitarias",
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
            materia_frame, values=MATERIAS, state="readonly", width=28
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
            values=["Todas"] + MATERIAS,
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

    @staticmethod
    def _hover(btn: tk.Button, c1: str, c2: str):
        btn.bind("<Enter>", lambda _: btn.config(bg=c2))
        btn.bind("<Leave>", lambda _: btn.config(bg=c1))


# ==========================
# ENTRADA
# ==========================
if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
