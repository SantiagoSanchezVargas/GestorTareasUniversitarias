# 📚 CustomTkinter - Guía de Referencia Rápida

## 🎯 ¿Qué es CustomTkinter?

CustomTkinter es una librería que moderniza Tkinter con:
- Widgets prediseñados hermosos
- Tema oscuro/claro automático
- Bordes redondeados
- Efectos visuales suaves
- Compatible 100% con tkinter

---

## 🔧 Setup Básico

```python
import customtkinter as ctk

# Configuración global
ctk.set_appearance_mode("System")  # "Light", "Dark", "System"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

# Crear ventana principal
root = ctk.CTk()
root.geometry("800x600")
root.title("Mi Aplicación")

# Mostrar
root.mainloop()
```

---

## 🎨 Widgets Principales

### CTkFrame (Contenedor)
```python
frame = ctk.CTkFrame(root, corner_radius=15, fg_color="gray20")
frame.pack(padx=20, pady=20, fill="both", expand=True)

# También con grid
frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
```

### CTkLabel (Texto)
```python
label = ctk.CTkLabel(
    frame,
    text="Hola Mundo",
    font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
    text_color="white"
)
label.pack(pady=10)
```

### CTkEntry (Campo de texto)
```python
entry = ctk.CTkEntry(
    frame,
    placeholder_text="Escribe aquí...",
    corner_radius=8,
    height=40,
    font=ctk.CTkFont(size=12)
)
entry.pack(fill="x", padx=10, pady=10)

# Obtener valor
valor = entry.get()

# Establecer valor
entry.insert(0, "Texto inicial")

# Limpiar
entry.delete(0, ctk.END)
```

### CTkButton (Botón)
```python
btn = ctk.CTkButton(
    frame,
    text="Presiona aquí",
    command=mi_funcion,
    corner_radius=8,
    height=40,
    fg_color="green",
    hover_color="darkgreen",
    font=ctk.CTkFont(size=12, weight="bold")
)
btn.pack(fill="x", padx=10, pady=5)

# Deshabilitar
btn.configure(state="disabled")
```

### CTkComboBox (Desplegable)
```python
combo = ctk.CTkComboBox(
    frame,
    values=["Opción 1", "Opción 2", "Opción 3"],
    state="readonly",
    corner_radius=8,
    height=40
)
combo.pack(fill="x", padx=10, pady=10)

# Obtener valor
valor = combo.get()

# Establecer valor
combo.set("Opción 1")
```

### CTkCheckbox (Casilla)
```python
var = ctk.BooleanVar()
checkbox = ctk.CTkCheckBox(
    frame,
    text="Aceptar términos",
    variable=var,
    onvalue=True,
    offvalue=False
)
checkbox.pack()

# Obtener estado
estado = var.get()
```

### CTkSwitch (Interruptor)
```python
switch_var = ctk.BooleanVar()
switch = ctk.CTkSwitch(
    frame,
    text="Modo Oscuro",
    variable=switch_var,
    command=lambda: print(switch_var.get())
)
switch.pack(pady=10)
```

### CTkSlider (Deslizador)
```python
slider_var = ctk.DoubleVar()
slider = ctk.CTkSlider(
    frame,
    from_=0,
    to=100,
    variable=slider_var,
    command=lambda v: print(f"Valor: {v}")
)
slider.pack(fill="x", padx=10, pady=10)
```

### CTkProgressBar (Barra de progreso)
```python
progress = ctk.CTkProgressBar(frame, indeterminate_speed=1)
progress.set(0.5)  # 50%
progress.pack(fill="x", padx=10, pady=10)
```

### CTkScrollableFrame (Área scrolleable)
```python
scroll_frame = ctk.CTkScrollableFrame(
    frame,
    fg_color="gray20",
    corner_radius=10
)
scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
scroll_frame.grid_columnconfigure(0, weight=1)

# Agregar widgets dentro
for i in range(20):
    ctk.CTkLabel(scroll_frame, text=f"Elemento {i}").pack()
```

### CTkToplevel (Ventana secundaria)
```python
def abrir_diálogo():
    dialog = ctk.CTkToplevel(root)
    dialog.geometry("400x300")
    dialog.title("Diálogo")
    dialog.grab_set()  # Modal
    
    ctk.CTkLabel(dialog, text="Contenido").pack(padx=20, pady=20)
    ctk.CTkButton(dialog, text="Cerrar", command=dialog.destroy).pack()

btn = ctk.CTkButton(root, text="Abrir", command=abrir_diálogo)
btn.pack()
```

---

## 🎨 Estilos y Colores

### CTkFont (Fuentes)
```python
font_pequeña = ctk.CTkFont(family="Segoe UI", size=10)
font_normal = ctk.CTkFont(family="Segoe UI", size=12)
font_grande = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
font_mono = ctk.CTkFont(family="Courier", size=11)

label = ctk.CTkLabel(frame, text="Texto", font=font_grande)
```

### Colores
```python
# Colores comunes
colores = {
    "Azul": "#0084ff",
    "Verde": "#00c957",
    "Rojo": "#ff4444",
    "Gris": "#808080",
    "Negro": "#000000",
    "Blanco": "#ffffff"
}

# Para fondos
btn = ctk.CTkButton(frame, text="Azul", fg_color="#0084ff")
btn = ctk.CTkButton(frame, text="Verde", fg_color="#00c957")
```

### Corner Radius
```python
# Sin redondas
frame = ctk.CTkFrame(root, corner_radius=0)

# Ligeramente redondeado
frame = ctk.CTkFrame(root, corner_radius=8)

# Muy redondeado (estándar)
frame = ctk.CTkFrame(root, corner_radius=15)

# Más options
btn = ctk.CTkButton(root, text="Botón", corner_radius=20)
entry = ctk.CTkEntry(root, corner_radius=8)
```

---

## 📐 Layout (Pack vs Grid)

### Pack (simple)
```python
frame = ctk.CTkFrame(root)
frame.pack(fill="both", expand=True, padx=10, pady=10)

btn1 = ctk.CTkButton(frame, text="1")  
btn1.pack(side="left", padx=5)

btn2 = ctk.CTkButton(frame, text="2")
btn2.pack(side="left", padx=5)
```

### Grid (control preciso)
```python
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

frame = ctk.CTkFrame(root)
frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
frame.grid_rowconfigure(1, weight=1)
frame.grid_columnconfigure(0, weight=1)

label = ctk.CTkLabel(frame, text="Fila 0")
label.grid(row=0, column=0, sticky="w", pady=10)

entry = ctk.CTkEntry(frame)
entry.grid(row=1, column=0, sticky="ew", pady=10)

btn = ctk.CTkButton(frame, text="Enviar")
btn.grid(row=2, column=0, sticky="ew", pady=10)
```

---

## 🎭 Tema (Appearance Mode)

```python
# Automático (detecta Windows oscuro/claro)
ctk.set_appearance_mode("System")

# Siempre oscuro
ctk.set_appearance_mode("Dark")

# Siempre claro
ctk.set_appearance_mode("Light")

# Cambiar dinámicamente
def cambiar_tema():
    modo_actual = ctk.get_appearance_mode()
    nuevo_modo = "Dark" if modo_actual == "Light" else "Light"
    ctk.set_appearance_mode(nuevo_modo)
```

### Temas de Color
```python
# Opciones: "blue", "green", "dark-blue"
ctk.set_default_color_theme("blue")
ctk.set_default_color_theme("green")
ctk.set_default_color_theme("dark-blue")
```

---

## 🔄 Variables y Bindings

### StringVar
```python
var = ctk.StringVar(value="inicial")
entry = ctk.CTkEntry(root, textvariable=var)
entry.pack()

# Obtener valor
print(var.get())

# Establecer valor
var.set("nuevo valor")

# Observar cambios
var.trace("w", lambda *args: print(f"Cambió a: {var.get()}"))
```

### IntVar
```python
numero = ctk.IntVar(value=0)
slider = ctk.CTkSlider(root, from_=0, to=100, variable=numero)
slider.pack()

print(numero.get())
numero.set(50)
```

### BooleanVar
```python
checked = ctk.BooleanVar()
checkbox = ctk.CTkCheckBox(root, text="Aceptar", variable=checked)
checkbox.pack()

print(checked.get())  # True o False
```

### Bind (Eventos del teclado)
```python
entry = ctk.CTkEntry(root)
entry.pack()

# Presionar Enter
entry.bind("<Return>", lambda e: print("Enter presionado"))

# Soltar tecla
entry.bind("<KeyRelease>", lambda e: print(f"Tecla: {e.char}"))
```

---

## 💾 Diálogos Comunes

### Filedialog
```python
from tkinter import filedialog

# Abrir archivo
archivo = filedialog.askopenfilename(
    title="Selecciona un archivo",
    filetypes=[("Imágenes", "*.png *.jpg"), ("Todos", "*.*")]
)
print(archivo)

# Guardar como
guardar = filedialog.asksaveasfilename(
    defaultextension=".txt",
    filetypes=[("Texto", "*.txt")]
)
```

### Messagebox
```python
from tkinter import messagebox

# Información
messagebox.showinfo("Título", "Mensaje informativo")

# Advertencia
messagebox.showwarning("Advertencia", "¡Cuidado!")

# Error
messagebox.showerror("Error", "Algo salió mal")

# Pregunta (Sí/No)
respuesta = messagebox.askyesno("Confirmar", "¿Estás seguro?")
if respuesta:
    print("Usuario dijo sí")
```

### Colorchooser
```python
from tkinter import colorchooser

color_tupla, color_hex = colorchooser.askcolor(
    initialcolor="#0084ff",
    title="Elige un color"
)
print(f"Color HEX: {color_hex}")
```

---

## 📋 Ejemplo Completo

```python
import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App:
    def __init__(self, root):
        self.root = root
        self.root.geometry("500x400")
        self.root.title("Mi Primera App CustomTkinter")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.crear_ui()
    
    def crear_ui(self):
        frame = ctk.CTkFrame(self.root, corner_radius=15)
        frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Título
        titulo = ctk.CTkLabel(
            frame,
            text="Bienvenido",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        titulo.grid(row=0, column=0, pady=10)
        
        # Campo de entrada
        self.entry = ctk.CTkEntry(
            frame,
            placeholder_text="Tu nombre...",
            corner_radius=8,
            height=40
        )
        self.entry.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        
        # Botón
        btn = ctk.CTkButton(
            frame,
            text="Saludar",
            command=self.saludar,
            corner_radius=8,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        btn.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
    
    def saludar(self):
        nombre = self.entry.get()
        if nombre:
            messagebox.showinfo("Saludo", f"¡Hola {nombre}!")
        else:
            messagebox.showwarning("Atención", "Por favor ingresa tu nombre")

if __name__ == "__main__":
    root = ctk.CTk()
    app = App(root)
    root.mainloop()
```

---

## 🚀 Tips Profesionales

1. **Usa grid para layouts complejos** - Más control que pack
2. **Cambia corner_radius entre 8-15px** - Profesional y moderno
3. **Aprovecha CTkFont para consistencia** - Define fuentes centrales
4. **Siempre usa System para tema** - Se adapta al usuario
5. **Crea clases para aplicaciones grandes** - Mejor organización
6. **Usa grid_columnconfigure(weight=1)** - Diseño responsive
7. **Threading para operaciones largas** - Sin bloquear UI
8. **Documenta el código CTK** - Diferente a tkinter tradicional

---

## 📖 Recursos Oficiales

- Repositorio: https://github.com/TomSchimansky/CustomTkinter
- Documentación: https://customtkinter.tomschimansky.com/

---

**¡Feliz diseño con CustomTkinter! 🎨**
