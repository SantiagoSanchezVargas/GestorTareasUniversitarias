# 🎨 Transformación del Gestor de Tareas - CustomTkinter

## 📋 Resumen de Cambios

Tu aplicación ha sido completamente refactorizada de **Tkinter estándar** a **CustomTkinter (CTK)**, transformándola en una solución profesional y moderna con características avanzadas.

---

## ✨ Principales Mejoras Implementadas

### 1. **Migración Visual a CustomTkinter**
- ✅ Interfaz completamente rediseñada con **CustomTkinter 5.2.0+**
- ✅ Tema **System** (detecta automáticamente tema oscuro/claro del sistema)
- ✅ **Corner Radius = 15px** en todos los frames y botones para bordes redondeados
- ✅ Eliminación de bordes antiguos: `border_width=0`
- ✅ Fuente moderna **"Segoe UI"** en toda la aplicación
- ✅ Colores dinámicos y adaptive al tema del sistema

### 2. **Diseño de Tarjetas Estilo Notion**
```
┌─ Barra lateral (5px) ──────────────────┐
│ 🎨 Color materia                       │
│                                        │
│ 📝 Nombre de la Tarea                  │
│ 📚 Materia • Fecha Hora                │
│                                        │
│ [✔ Entregar] [🔥 Urgente] [✏] [🗑]    │
└────────────────────────────────────────┘
```
- ✅ Barra lateral gruesa (4-5px) con color de la materia
- ✅ Fondo neutro (blanco/gris oscuro según tema)
- ✅ Botones de acción directamente en la tarjeta
- ✅ Diseño limpio e intuitivo

### 3. **Sistema de Bandeja (System Tray)**
- ✅ Integración completa con **pystray**
- ✅ Al cerrar la ventana → minimiza a la bandeja (NO cierra)
- ✅ Menú en la bandeja:
  - 📖 _Abrir Gestor_ - restaura la ventana
  - ❌ _Cerrar Aplicación_ - finaliza completamente
- ✅ Icono personalizado en la bandeja del sistema

### 4. **Notificaciones Inteligentes con Threading**
- ✅ Hilo de monitoreo que se ejecuta cada 30 minutos
- ✅ Detecta tareas que vencen en menos de 24 horas
- ✅ Notificaciones de Windows usando **plyer**
- ✅ Personalización con:
  - 🎯 Emoji de la materia
  - 🎨 Nombre de la materia
  - ⏱️ Tiempo restante en formato legible
- ✅ Tracking de notificaciones para evitar duplicados en el mismo día

### 5. **Integración Dinámica del Perfil**
- ✅ Saludo personalizado: **"👋 Hola, [Nombre]"**
- ✅ Carrera mostrada en el encabezado
- ✅ Materias cargadas dinámicamente desde `perfil.json`
- ✅ Foto de perfil cargada automáticamente (si existe)
- ✅ Avatar circular con letra inicial como placeholder
- ✅ ComboBox de materias se llena automáticamente

### 6. **Estructura Mejorada y Responsive**
- ✅ Grid con `sticky="nsew"` en todos los contenedores
- ✅ `grid_columnconfigure(0, weight=1)` para expansión horizontal
- ✅ `grid_rowconfigure(1, weight=1)` para expansión vertical
- ✅ No hay espacios vacíos a la derecha
- ✅ Diseño adaptativo a diferentes tamaños de pantalla
- ✅ Mínimo: 900x600px | Recomendado: 1400x850px

---

## 🔧 Cambios Técnicos

### Importes Actualizados
```python
# Antes
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from tkinter.ttk import Combobox

# Después
import customtkinter as ctk
from tkinter import messagebox, filedialog, colorchooser
```

### Configuración de Tema
```python
ctk.set_appearance_mode("System")  # Automático oscuro/claro
ctk.set_default_color_theme("blue")  # Tema azul profesional
```

### Widget Mapping
| Tkinter | CustomTkinter |
|---------|--------------|
| `tk.Tk()` | `ctk.CTk()` |
| `tk.Frame()` | `ctk.CTkFrame()` |
| `tk.Label()` | `ctk.CTkLabel()` |
| `tk.Button()` | `ctk.CTkButton()` |
| `tk.Entry()` | `ctk.CTkEntry()` |
| `tk.Canvas()` | `ctk.CTkCanvas()` |
| `ttk.Combobox` | `ctk.CTkComboBox()` |

---

## 📦 Dependencias Instaladas

Todas las librerías están en `requirements.txt`:

```
customtkinter>=5.2.0     # UI moderna
tkcalendar>=1.6.0        # Selector de fechas
pillow>=10.0.0           # Procesamiento de imágenes
pystray>=0.19.0          # Bandeja del sistema
plyer>=2.1.0             # Notificaciones de Windows
```

**Instalar:**
```bash
pip install -r requirements.txt
```

---

## 🚀 Uso de la Aplicación

### Inicio Normal
```bash
python TareasUniversitarias.py
```

### Primera Ejecución
Se abre el **Asistente de Configuración**:
1. Ingresa tu nombre
2. Ingresa tu carrera/perfil
3. Agrega tus materias con colores personalizado
4. Presiona **"Guardar y Comenzar"**

### Funcionalidades Principales

#### ✅ Agregar Tareas
1. Completa el nombre
2. Selecciona la materia
3. Elige la fecha (calendario interactivo)
4. Ajusta la hora (selector visual)
5. Clic en **"➕ Agregar"**

#### ✔️ Marcar Estados
- **✔ Entregar** - marca como completada
- **🔥 Urgente** - marca manualmente como urgente
- **↩ Pendiente** - devuelve a pendiente
- **✏ Editar** - modifica nombre, materia, hora
- **🗑 Eliminar** - elimina la tarea

#### 🎯 Estados Automáticos
- **Pendiente** - más de una semana
- **Próximo** - esta semana
- **Urgente** - faltan 4 días o menos
- **Vencido** - fecha ya pasó
- **Entregado** - tarea completada

#### 🔔 Notificaciones
- Se envían automáticamente cada 30 minutos
- Solo si una tarea vence en menos de 24 horas
- Una sola notificación por tarea, por día
- Personalizada con emoji y nombre de materia

#### 🎲 Reloj Analógico
- Reloj en tiempo real en el encabezado
- Actualización cada segundo
- Diseño moderno con manecillas coloridas

#### 🎨 Personalización
- **Clic derecho en la foto** → cambiar imagen de perfil
- **Filtrar por materia** → ver solo tareas de una materia
- **Foto circular con borde** → avatar profesional

---

## 📁 Estructura de Archivos

```
GestorTareasUniversitarias/
├── TareasUniversitarias.py          # Archivo principal (refactorizado)
├── TareasUniversitarias.backup.py   # Copia de seguridad del código original
├── perfil.json                       # Configuración del perfil
├── tareas.json                       # Base de datos de tareas
├── notificaciones_hoy.json           # Registro de notificaciones del día
├── requirements.txt                  # Dependencias (actualizado)
├── TRANSFORMACION_CUSTOMTKINTER.md  # Este archivo
└── GUIA_USO.md                       # Guía de usuario (original)
```

---

## 🎯 Características Mantenidas

✅ **Lógica de estados intacta** - Pendiente, Próximo, Urgente, Vencido, Entregado  
✅ **Persistencia de datos** - Tareas guardadas en JSON  
✅ **Perfil dinámico** - Materias cargadas desde perfil.json  
✅ **Monitoreo de tareas** - Notificaciones cada 30 minutos  
✅ **Control de foto** - Avatar circular con imagen de perfil  
✅ **Multiplicidad de funciones** - Editar, eliminar, filtrar, cambiar estado  

---

## 🐛 Notas Técnicas Importantes

### Tema Automático
La aplicación detecta automáticamente si el sistema usa tema oscuro o claro y se adapta.

### Performance
- No hay bloqueos de UI gracias al threading
- Scrolleable frames para muchas tareas
- Actualización eficiente del tablero

### Compatibilidad
- Windows 10/11 ✅
- Requiere Python 3.8+
- Funciona con DirectX 11+ (para mayor fluidez)

### Mejoras de Accesibilidad
- Colores de alto contraste
- Fuentes legibles (Segoe UI)
- Botones grandes y fáciles de usar
- Emojis para mejor identificación visual

---

## 💡 Próximas Sugerencias (Opcional)

Si deseas mejorar más la aplicación:

1. **Base de datos SQLite** - Reemplazar JSON para mejor escala
2. **Exportar a Excel** - Generar reportes de tareas
3. **Sincronización en la nube** - Google Drive, OneDrive
4. **Recordatorios por email** - Además de notificaciones
5. **Tema personalizable** - Dejar elegir colores al usuario
6. **Estadísticas** - Gráficos de productividad
7. **Tags/Etiquetas** - Clasificación adicional
8. **Importar ICS** - De calendarios externos

---

## 📞 Soporte

Si encuentras problemas:

1. Verifica que todas las dependencias estén instaladas: `pip install -r requirements.txt`
2. Asegúrate de tener Python 3.8+
3. En Windows, verifica que tienes permisos para la bandeja del sistema
4. Los archivos JSON deben estar en la misma carpeta que el script

---

## 🎉 ¡Listo!

Tu aplicación ahora es **profesional, moderna y eficiente**. 

**Disfruta de tu nuevo Gestor de Tareas Universitarias con CustomTkinter! 🚀**
