import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import json, os

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

    # ----------------------
    # TABLERO
    # ----------------------
    def actualizar_tablero(self):
        for inner in self.columnas.values():
            for w in inner.winfo_children():
                w.destroy()

        for t in self.tareas:
            # ✅ FILTRO BIEN INDENTADO
            if self.filtro_materia.get() != "Todas" and t["materia"] != self.filtro_materia.get():
                continue

            estado = self.get_estado(t)
            inner = self.columnas[estado]

            # ✅ USAR BORDE CORRECTAMENTE
            borde = 2 if estado == "Urgente" else 1
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
        # Encabezado
        tk.Label(
            self.root,
            text=f"👋 Hola, {USUARIO}",
            bg="#cfe9ff", fg="#003366",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=(10, 0))

        tk.Label(
            self.root,
            text="📚 Gestor de tareas universitarias",
            bg="#cfe9ff", fg="#005b96"
        ).pack()

        # Panel de inputs
        frame_inputs = tk.Frame(self.root, bg="#e6f7ff", pady=6)
        frame_inputs.pack(fill="x", padx=10)

        self.entry_nombre = tk.Entry(frame_inputs, width=28, font=("Segoe UI", 10))
        self.entry_nombre.pack(side="left", padx=8, ipady=4)
        self.entry_nombre.bind("<Return>", lambda _: self.agregar_tarea())
        
        self.combo_materia = ttk.Combobox(
            frame_inputs, values=MATERIAS, state="readonly", width=28
        )
        self.combo_materia.pack(side="left", padx=4)
        self.combo_filtro = ttk.Combobox(
            frame_inputs,
            values=["Todas"] + MATERIAS,
            state="readonly",
            width=20,
            textvariable=self.filtro_materia
        )
        self.combo_filtro.pack(side="left", padx=4)
        self.combo_filtro.bind("<<ComboboxSelected>>", lambda e: self.actualizar_tablero())

        self.cal = DateEntry(frame_inputs, width=12)
        self.cal.pack(side="left", padx=4)

        self.btn_hora = tk.Button(
            frame_inputs,
            textvariable=None,
            text=f"⏰ {self.hora_var.get()}",
            bg="#6EC1FF",
            command=self.abrir_selector_hora
        )
        self.btn_hora.pack(side="left", padx=4)

        btn_add = tk.Button(
            frame_inputs,
            text="➕ Agregar",
            bg="#4D96FF", fg="white",
            font=("Segoe UI", 10, "bold"),
            command=self.agregar_tarea,
        )
        btn_add.pack(side="left", padx=8)
        self._hover(btn_add, "#4D96FF", "#6EC1FF")

        # Tablero de columnas con scroll
        board = tk.Frame(self.root, bg="#cfe9ff")
        board.pack(fill="both", expand=True, padx=6, pady=8)

        self.columnas: dict[str, tk.Frame] = {}
        for estado in ESTADOS:
            col_frame = tk.Frame(board, bg="#e6f7ff")
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
