# 📚 Gestor de Tareas Universitarias PRO++

Aplicación de escritorio desarrollada en **Python con Tkinter**, inspirada en tableros tipo Trello, que permite gestionar trabajos universitarios de forma visual, intuitiva y eficiente.

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

* 🔔 **Notificaciones automáticas**

  * Recordatorios:

    * 1–2 días antes
    * Menos de 24h (urgente)
    * Tareas vencidas

* 🖱️ **Menú contextual (click derecho)**

  * Marcar como entregado
  * Volver a pendiente
  * Eliminar tarea

* 🎨 **Colores por materia**

  * Identificación visual rápida

* 💾 **Persistencia de datos**

  * Las tareas se guardan en `tareas.json`

---

## 🧠 Tecnologías utilizadas

* Python 3
* Tkinter (GUI)
* tkcalendar
* plyer (notificaciones)
* JSON (almacenamiento)

---

## 📦 Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/tu-usuario/gestor-tareas-pro.git
cd gestor-tareas-pro
```

2. Instala dependencias:

```bash
pip install tkcalendar plyer
```

3. Ejecuta la aplicación:

```bash
python main.py
```

---

## 🖥️ Uso

1. Escribe el nombre de la tarea
2. Selecciona la materia
3. Escoge la fecha en el calendario
4. Define la hora (botón ⏰)
5. Haz clic en **➕ Agregar**

Las tareas aparecerán automáticamente organizadas por prioridad.

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
📁 gestor-tareas-pro
│
├── TareasUniversitarias.py
├── tareas.json
└── README.md
```

---

## 💡 Ideas futuras

* Drag & Drop entre columnas
* Animaciones tipo Notion/Trello
* Exportar tareas a Excel o PDF
* Estadísticas por materia
* Versión web o móvil

---

## 👨‍💻 Autor

Desarrollado por **Santiago Andrés Sánchez Vargas**

---

## ⭐ Contribuciones

Si te gusta el proyecto:

* Dale ⭐ en GitHub
* Haz un fork
* Propón mejoras

---

## 📜 Licencia

Este proyecto es de uso educativo y personal.
