import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from plyer import notification
import json
import os
import math

tareas = []
hora_seleccionada = "12:00"

colores_materias = {
    "Operativa": "#3028C7",
    "Big Data": "#6BCB77",
    "Analisis numerico": "#210B31",
    "Comunicación de datos": "#6A4C93",
    "Emprendimiento e innovación": "#F7B32B",
    "Ciencia, tecnología e innovación": "#4D908E",
    "Seguridad en hardware": "#FF0000",
}

ARCHIVO = "tareas.json"

# ==========================
# GUARDAR / CARGAR
# ==========================
def guardar_tareas():
    with open(ARCHIVO, "w") as f:
        json.dump([{**t, "fecha": t["fecha"].strftime("%Y-%m-%d %H:%M")} for t in tareas], f, indent=4)

def cargar_tareas():
    if not os.path.exists(ARCHIVO):
        return
    with open(ARCHIVO) as f:
        for t in json.load(f):
            t["fecha"] = datetime.strptime(t["fecha"], "%Y-%m-%d %H:%M")
            tareas.append(t)

# ==========================
# FUNCIONES
# ==========================
def agregar_tarea():
    nombre = entry_nombre.get()

    if nombre.strip() == "" or "Ingresa" in nombre:
        messagebox.showwarning("Error", "Escribe el nombre de la tarea")
        return

    try:
        fecha_hora = datetime.strptime(
            f"{cal.get_date().strftime('%d/%m/%Y')} {hora_seleccionada}",
            "%d/%m/%Y %H:%M"
        )
    except:
        messagebox.showerror("Error", "Hora inválida")
        return

    tareas.append({
        "nombre": nombre,
        "materia": combo_materia.get(),
        "fecha": fecha_hora,
        "entregado": False,
        "notificado": False,
        "vencido_notificado": False
    })

    guardar_tareas()
    actualizar_tablero()

def cambiar_estado(tarea, estado):
    tarea["entregado"] = estado
    guardar_tareas()
    actualizar_tablero()

def eliminar_tarea(tarea):
    tareas.remove(tarea)
    guardar_tareas()
    actualizar_tablero()

# ==========================
# ESTADOS MEJORADOS 🔥
# ==========================
def get_estado(t):
    ahora = datetime.now()
    diff = t["fecha"] - ahora

    if t["entregado"]:
        return "Entregado"
    elif diff < timedelta(0):
        return "Vencido"
    elif diff < timedelta(days=1):
        return "Urgente"
    elif timedelta(days=1) <= diff <= timedelta(days=2):
        return "Proximo"
    return "Pendiente"

# ==========================
# MENÚ DERECHO
# ==========================
def mostrar_menu(event, tarea):
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="✔ Marcar entregado", command=lambda: cambiar_estado(tarea, True))
    menu.add_command(label="↩ Volver a pendiente", command=lambda: cambiar_estado(tarea, False))
    menu.add_separator()
    menu.add_command(label="🗑 Eliminar", command=lambda: eliminar_tarea(tarea))
    menu.tk_popup(event.x_root, event.y_root)

# ==========================
# TABLERO
# ==========================
def actualizar_tablero():
    for col in columnas.values():
        for w in col.winfo_children():
            w.destroy()

    for t in tareas:
        estado = get_estado(t)

        bg_color = "#2a2a40"
        if estado == "Urgente":
            bg_color = "#8B0000"

        frame = tk.Frame(columnas[estado], bg=bg_color, pady=5)
        frame.pack(fill="x", padx=5, pady=5)

        color = colores_materias.get(t["materia"], "#999")

        lbl = tk.Label(frame, text=t["nombre"], bg=color, fg="black")
        lbl.pack(fill="x")

        tk.Label(frame,
                 text=t["fecha"].strftime("%d/%m %H:%M"),
                 bg=bg_color, fg="white").pack()

        frame.bind("<Button-3>", lambda e, tarea=t: mostrar_menu(e, tarea))
        lbl.bind("<Button-3>", lambda e, tarea=t: mostrar_menu(e, tarea))

# ==========================
# NOTIFICACIONES
# ==========================
def verificar_notificaciones():
    ahora = datetime.now()

    for t in tareas:
        if t["entregado"]:
            continue

        diff = t["fecha"] - ahora

        if timedelta(days=1) <= diff <= timedelta(days=2) and not t["notificado"]:
            notification.notify(title="📚 Próximo", message=f"{t['nombre']} en 1-2 días")
            t["notificado"] = True

        elif diff < timedelta(hours=24) and not t["vencido_notificado"]:
            notification.notify(title="⚠ Urgente", message=t["nombre"])
            t["vencido_notificado"] = True

    guardar_tareas()
    root.after(60000, verificar_notificaciones)

# ==========================
# RELOJ
# ==========================
def dibujar_reloj():
    canvas.delete("all")

    cx, cy, r = 60, 60, 50
    canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline="white")

    ahora = datetime.now()
    h, m, s = ahora.hour % 12, ahora.minute, ahora.second

    ang_s = math.radians(s*6 - 90)
    ang_m = math.radians(m*6 - 90)
    ang_h = math.radians(h*30 + m/2 - 90)

    canvas.create_line(cx, cy, cx+r*0.9*math.cos(ang_s),
                       cy+r*0.9*math.sin(ang_s), fill="red")

    canvas.create_line(cx, cy, cx+r*0.7*math.cos(ang_m),
                       cy+r*0.7*math.sin(ang_m), fill="white", width=2)

    canvas.create_line(cx, cy, cx+r*0.5*math.cos(ang_h),
                       cy+r*0.5*math.sin(ang_h), fill="white", width=3)

    root.after(1000, dibujar_reloj)

# ==========================
# SELECTOR HORA
# ==========================
def abrir_selector_hora():
    ventana = tk.Toplevel(root)
    ventana.title("Seleccionar hora")
    ventana.geometry("250x180")
    ventana.configure(bg="#2a2a40")

    spin_h = tk.Spinbox(ventana, from_=0, to=23, format="%02.0f")
    spin_h.pack(pady=10)

    spin_m = tk.Spinbox(ventana, from_=0, to=59, format="%02.0f")
    spin_m.pack(pady=10)

    def confirmar():
        global hora_seleccionada
        hora_seleccionada = f"{spin_h.get()}:{spin_m.get()}"
        btn_hora.config(text=f"⏰ {hora_seleccionada}")
        ventana.destroy()

    tk.Button(ventana, text="Aceptar",
              command=confirmar).pack(pady=10)

# ==========================
# UI MODERNA 🔥
# ==========================
root = tk.Tk()
root.geometry("1100x600")
root.configure(bg="#1e1e2f")

tk.Label(root, text="📚 Gestor de universitarias",
         bg="#1e1e2f", fg="white",
         font=("Segoe UI", 18)).pack(pady=5)

canvas = tk.Canvas(root, width=120, height=120,
                   bg="#1e1e2f", highlightthickness=0)
canvas.pack()

frame_inputs = tk.Frame(root, bg="#2a2a40")
frame_inputs.pack(fill="x", pady=10)

# INPUT MODERNO
entry_nombre = tk.Entry(frame_inputs,
                        width=30,
                        bg="#3a3a55",
                        fg="white",
                        insertbackground="white",
                        relief="flat",
                        font=("Segoe UI", 10))
entry_nombre.pack(side="left", padx=10, ipady=6)
entry_nombre.insert(0, "📝 Ingresa la tarea...")

def hover(e): e.widget.config(bg="#50507a")
def leave(e): e.widget.config(bg="#3a3a55")

entry_nombre.bind("<Enter>", hover)
entry_nombre.bind("<Leave>", leave)

# COMBO
combo_materia = ttk.Combobox(frame_inputs,
                             values=list(colores_materias.keys()),
                             state="readonly")
combo_materia.set("📘 Materia")
combo_materia.pack(side="left", padx=5)

# CALENDARIO
cal = DateEntry(frame_inputs, date_pattern="dd/mm/yyyy")
cal.pack(side="left", padx=5)

# HORA
btn_hora = tk.Button(frame_inputs,
                     text="⏰ 12:00",
                     bg="#3a3a55",
                     fg="white",
                     relief="flat",
                     command=abrir_selector_hora)
btn_hora.pack(side="left", padx=5)

# BOTÓN
tk.Button(frame_inputs,
          text="➕ Agregar",
          bg="#4D96FF",
          fg="white",
          font=("Segoe UI", 10, "bold"),
          relief="flat",
          command=agregar_tarea).pack(side="left", padx=10)

# TABLERO
board = tk.Frame(root, bg="#1e1e2f")
board.pack(fill="both", expand=True)

columnas = {}
for estado in ["Pendiente", "Proximo", "Urgente", "Vencido", "Entregado"]:
    col = tk.Frame(board, bg="#2a2a40")
    col.pack(side="left", fill="both", expand=True, padx=5)

    tk.Label(col, text=estado,
             bg="#2a2a40", fg="white").pack()

    inner = tk.Frame(col, bg="#1e1e2f")
    inner.pack(fill="both", expand=True)

    columnas[estado] = inner

# ==========================
# INICIO
# ==========================
cargar_tareas()
actualizar_tablero()
verificar_notificaciones()
dibujar_reloj()

root.mainloop()