# 📚 Gestor de Tareas Universitarias PRO++ v2.0

Aplicación de escritorio desarrollada en **Python con Tkinter**, inspirada en tableros tipo Trello, que permite gestionar trabajos universitarios de forma visual, intuitiva y eficiente.

✨ **NUEVO EN v2.0**: Ejecución en segundo plano, System Tray, monitoreo automático e notificaciones inteligentes

---

## 🚀 Características principales

* 🗂️ **Tablero tipo Trello**

  * Organización automática en columnas:

    * Pendiente
    * Próximo (1–2 días)
    * Urgente (< 24h)
    * Vencido
    * Entregado

* ⏰ **Selector de hora interactivo**

  * Popup para elegir hora fácilmente

* 🕒 **Reloj analógico en tiempo real**

  * Estilo visual moderno dentro de la app

* 🔔 **Notificaciones automáticas inteligentes** ⭐ NUEVO

  * Sistema de notificaciones del SO (Windows/Linux/Mac)
  * Notificaciones solo para tareas que vencen en < 24h
  * Evita notificaciones duplicadas en el mismo día
  * Títulos personalizados con emojis por materia
  * Información clara del tiempo restante

* 📊 **Monitoreo automático en segundo plano** ⭐ NUEVO

  * Hilo daemon que verifica tareas cada 30 minutos
  * Se ejecuta inmediatamente al iniciar
  * Consumo de recursos mínimo (< 5 MB RAM)
  * Sigue ejecutándose cuando la ventana está minimizada

* 🎯 **System Tray / Bandeja del Sistema** ⭐ NUEVO

  * Icono azul en la barra de tareas
  * Acceso rápido con clic derecho
  * Opción para Abrir ventana
  * Opción para Salir limpiamente
  * Minimización inteligente (botón X → bandeja, no cierra)

* 🖱️ **Menú contextual (click derecho)**

  * Editar tarea
  * Marcar como urgente
  * Marcar como entregado
  * Volver a pendiente
  * Eliminar tarea

* 🎨 **Colores por materia**

  * Identificación visual rápida
  * Colores en notificaciones con emojis específicos

* 💾 **Persistencia de datos mejorada**

  * Las tareas se guardan en `tareas.json`
  * Perfil del usuario en `perfil.json`
  * Notificaciones del día en `notificaciones_hoy.json` (auto-creado)

---

## 🧠 Tecnologías utilizadas

* **Python 3.8+** - Lenguaje principal
* **Tkinter** - Interfaz gráfica de usuario (GUI)
* **tkcalendar** - Selector de fecha
* **Pillow (PIL)** - Procesamiento de imágenes (fotos de perfil)
* **pystray** - Icono en System Tray (bandeja del sistema)
* **plyer** - Notificaciones del sistema operativo
* **threading** - Hilo de monitoreo en segundo plano
* **JSON** - Almacenamiento persistente de datos

---

## 📦 Instalación

### Opción 1: Automática (Recomendado) 🚀

```bash
cd c:\Codigos\GestorTareasUniversitarias
python quickstart.py
# Elige opción 4 (Instalar + Ejecutar)
```

### Opción 2: Manual

1. **Instala las dependencias:**

```bash
pip install -r requirements.txt
```

O instala paquetes individuales:

```bash
pip install tkcalendar pillow pystray plyer
```

2. **Ejecuta la aplicación:**

```bash
python TareasUniversitarias.py
```

### Opción 3: Ejecutar sin ventana de consola (Windows)

```bash
pythonw TareasUniversitarias.py
```

---

## 🖥️ Uso

### Crear una tarea

1. Escribe el nombre de la tarea
2. Selecciona la materia
3. Escoge la fecha en el calendario
4. Define la hora (botón ⏰ o "Hora actual")
5. Haz clic en **➕ Agregar tarea**

Las tareas aparecerán automáticamente organizadas por prioridad.

### Usar el System Tray

1. Busca el **icono azul (🟦)** en la barra de tareas (esquina inferior derecha)
2. Haz clic derecho para ver el menú:
   - **▶ Abrir** - Restaura la ventana principal
   - **🚪 Salir** - Cierra completamente la aplicación

### Cerrar sin terminar la aplicación

- Haz clic en el botón ❌ (cerrar) de la ventana
- La ventana se minimiza a la bandeja del sistema
- La aplicación continúa monitoreando tareas en segundo plano

### Recibir notificaciones

- Las notificaciones se envían **automáticamente** cada 30 minutos
- Solo para tareas que vencen en **< 24 horas**
- No recibirás duplicadas en el mismo día
- Los títulos incluyen emojis por materia:
  - 📊 Big Data, 🧮 Operativa, 📈 Análisis Numérico, etc.

Ejemplo de notificación:
```
📊 Big Data
'Proyecto final' vence en 5h 30m
```

---

## 📌 Estados de tareas

| Estado    | Condición           |
| --------- | ------------------- |
| Pendiente | Más de 2 días       |
| Próximo   | Entre 1 y 2 días    |
| Urgente   | Menos de 24 horas   |
| Vencido   | Fecha pasada        |
| Entregado | Marcada manualmente |

---

## 🧩 Estructura del proyecto

```
📁 GestorTareasUniversitarias
│
├── TareasUniversitarias.py          ← Aplicación principal
├── quickstart.py                    ← Instalador automático
├── prueba_monitoreo.py              ← Script de validación
├── requirements.txt                 ← Dependencias
│
├── tareas.json                      ← Base de datos de tareas (auto-creado)
├── perfil.json                      ← Perfil del usuario (auto-creado)
├── notificaciones_hoy.json          ← Registro de notificaciones (auto-creado)
│
├── README.md                        ← Este archivo
├── GUIA_USO.md                      ← Guía práctica de usuario
├── IMPLEMENTACION_TECNICA.md        ← Detalles técnicos
├── RESUMEN_CAMBIOS.md               ← Resumen ejecutivo
└── .git/                            ← Repositorio Git
```

---

## � Documentación

Para más información, consulta:

- **[GUIA_USO.md](GUIA_USO.md)** - Guía completa de usuario (recomendado para principiantes)
- **[IMPLEMENTACION_TECNICA.md](IMPLEMENTACION_TECNICA.md)** - Detalles técnicos de la implementación
- **[RESUMEN_CAMBIOS.md](RESUMEN_CAMBIOS.md)** - Cambios realizados en v2.0

## 💡 Ideas futuras

* Drag & Drop entre columnas
* Animaciones tipo Notion/Trello
* Exportar tareas a Excel o PDF
* Estadísticas por materia
* Sincronización en la nube
* Soporte para múltiples usuarios
* Alertas de sonido personalizadas

---

## � Características v2.0

Esta versión incluye mejoras significativas:

- ✅ **System Tray** - Acceso desde la bandeja del sistema
- ✅ **Monitoreo automático** - Verifica tareas cada 30 minutos
- ✅ **Notificaciones inteligentes** - Solo para tareas próximas a vencer
- ✅ **Segundo plano** - Sigue ejecutándose cuando la ventana está cerrada
- ✅ **Manejo robusto** - Falla graceful si faltan dependencias
- ✅ **Bajo consumo** - < 5 MB RAM en ejecución
- ✅ **Documentación completa** - Guías técnicas y de usuario

## ⚙️ Requisitos del Sistema

- **OS**: Windows, Linux o macOS
- **Python**: 3.8 o superior
- **RAM**: 50 MB mínimo
- **Disco**: 20 MB espacio disponible

## 🆘 Solución de Problemas

### No veo el icono en la bandeja
- Busca en "Iconos ocultos" de la bandeja
- Reinicia la aplicación
- Verifica que `pystray` esté instalado

### Las notificaciones no aparecen
- Instala `plyer`: `pip install plyer`
- En Windows: Verifica Configuración → Notificaciones
- Asegúrate de que las notificaciones no estén desactivadas

### La aplicación se cierra al cerrar la ventana
- Esto NO debería suceder
- Si ocurre, usa la opción "Salir" del menú
- Reporta el problema

## 👨‍💻 Autor y Créditos

Desarrollado por **Santiago Andrés Sánchez Vargas**

V2.0 con características de segundo plano, System Tray y notificaciones inteligentes.

---

## ⭐ Si te gusta el proyecto

* Dale ⭐ en GitHub
* Haz un fork
* Propón mejoras
* Comparte con tus compañeros

---

## 📜 Licencia

Este proyecto es de uso educativo y personal.
