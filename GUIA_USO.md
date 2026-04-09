# 📖 Guía de Uso - Sistema de Bandeja y Monitoreo

## 🎯 Descripción Rápida

Tu aplicación ahora tiene:
- ✅ **System Tray**: Icono en la barra de tareas para acceso rápido
- ✅ **Monitoreo Automático**: Hilo que revisa tareas cada 30 minutos
- ✅ **Notificaciones Inteligentes**: Alertas cuando las tareas están por vencer
- ✅ **Ejecución en Segundo Plano**: Sigue funcionando incluso con la ventana cerrada

---

## 🚀 Instalación de Dependencias

### Opción 1: Instalación Automática (Recomendado)

```bash
cd c:\Codigos\GestorTareasUniversitarias
pip install -r requirements.txt
```

### Opción 2: Instalación Manual

```bash
pip install tkcalendar pillow pystray plyer
```

---

## 💻 Cómo Ejecutar

### Ejecución Normal
```bash
python TareasUniversitarias.py
```

### Ejecución en Segundo Plano (Windows)

**Método 1: Acceso Directo con Minimización**
1. Crea un acceso directo de `TareasUniversitarias.py`
2. Haz clic derecho → Propiedades
3. En "Ejecutar", selecciona "Minimizado"

**Método 2: Ejecutar desde PowerShell (Sin Ventana de Consola)**
```powershell
pythonw TareasUniversitarias.py
```

---

## 🎮 Uso del System Tray

### Cómo Encontrar el Icono

1. Busca en la **esquina inferior derecha** de tu pantalla (bandeja del sistema)
2. El icono es un **cuadrado azul** (🟦)
3. Si no lo ves, puede estar **oculto**:
   - Haz clic en **"Mostrar elementos ocultos"** en la bandeja
   - O mira en **"Iconos ocultos"**

### Opciones del Menú

**Clic Derecho sobre el Icono:**

```
┌─────────────────┐
│ ▶ Abrir         │ ← Restaura la ventana principal
├─────────────────┤
│ 🚪 Salir        │ ← Cierra completamente la aplicación
└─────────────────┘
```

### Minimizar sin Cerrar

Cuando hace clic en el botón ❌ (cerrar) de la ventana:
- ✅ La ventana desaparece (se minimiza a la bandeja)
- ✅ La aplicación sigue ejecutándose en segundo plano
- ✅ Recupera la ventana desde el icono de la bandeja

---

## 🔔 Sistema de Notificaciones

### ¿Cuándo Recibirás Notificaciones?

La app te enviará una notificación cuando:

1. **Una tarea está por vencer EN MENOS DE 24 HORAS**
2. **Aún NO ha sido notificada hoy**
3. **Está en estado "Pendiente" o "Próximo"** (no "Entregada")

### Ejemplo de Notificación

```
┌─────────────────────────────────────┐
│ 📊 Big Data                         │
├─────────────────────────────────────┤
│ 'Proyecto final' vence en 5h 30m    │
└─────────────────────────────────────┘
```

### Emojis por Materia

| Materia | Emoji |
|---------|-------|
| Operativa | 🧮 |
| Big Data | 📊 |
| Análisis Numérico | 📈 |
| Comunicación de Datos | 📡 |
| Emprendimiento e Innovación | 💡 |
| Ciencia, Tecnología e Innovación | 🔬 |
| Seguridad en Hardware | 🔐 |

---

## ⏱️ Ciclo de Monitoreo

```
INICIO DE LA APP
        ↓
   Primer Chequeo (Inmediato)
   ↓ Chequea tareas y envía notificaciones
        ↓
   Espera 30 minutos
        ↓
   Segundo Chequeo
   ↓ Chequea tareas y envía notificaciones
        ↓
   Espera 30 minutos
        ↓
   ... (repite indefinidamente)
```

### ¿Qué Sucede en Cada Chequeo?

1. **Lee `tareas.json`** - Obtiene todas las tareas
2. **Filtra tareas** - Solo Pendiente/Próximo y no entregadas
3. **Calcula tiempo restante** - ¿Cuánto falta para vencer?
4. **Evalúa notificación** - ¿Vence en < 24h? ¿Ya notificada hoy?
5. **Envía notificación** - Si cumple condiciones
6. **Actualiza registro** - Guarda que fue notificada hoy

---

## 📁 Archivos Generados Automáticamente

### `notificaciones_hoy.json`

Se crea automáticamente para rastrear qué tareas fueron notificadas hoy.

**Ejemplo:**
```json
{
    "fecha": "2026-04-09",
    "tarea_ids": [
        "Proyecto final_Big Data_2026-04-09 18:30",
        "Informe_Operativa_2026-04-09 20:00"
    ]
}
```

**Comportamiento:**
- Se resetea automáticamente cada nuevo día
- Evita notificaciones duplicadas el mismo día
- Se limpia si la app se abre en un nuevo día

---

## 🐛 Solución de Problemas

### 1️⃣ "No veo el icono en la bandeja"

**Solución:**
- Busca en los iconos ocultos (click en "Mostrar")
- Reinicia la aplicación
- Verifica que `pystray` esté instalado: `pip install pystray`

### 2️⃣ "Las notificaciones no aparecen"

**Posibles causas:**
- `plyer` no está instalado
- Las notificaciones están desactivadas en Windows
- Hiciste clic en "No mostrar notificaciones" anteriormente

**Soluciones:**
```bash
pip install plyer
```

En Windows, verifica Configuración → Notificaciones → Aplicaciones y Alertas → Gestor de Tareas debe estar habilitado.

### 3️⃣ "La aplicación cierra cuando doy clic al botón X"

**Esperado o No?**
- ✅ **Normal**: La ventana desaparece, pero la app sigue en segundo plano (bandeja)
- ❌ **Problema**: Si cierras completamente, deberías usar "Salir" del menú

### 4️⃣ "El hilo de monitoreo está consumiendo mucha RAM"

**Verificación:**
- El hilo debería consumir **<5 MB** en el Administrador de Tareas
- Si usa más, reporta el problema

---

## 🔧 Configuración Avanzada

### Cambiar el Intervalo de Monitoreo

En `TareasUniversitarias.py`, busca esta línea:

```python
time.sleep(1800)  # 30 minutos = 1800 segundos
```

**Cambiar a 15 minutos:**
```python
time.sleep(900)  # 15 minutos
```

**Cambiar a 1 hora:**
```python
time.sleep(3600)  # 1 hora
```

### Personalizar Notificación de Menos de 24h

En el archivo, busca:
```python
if timedelta(0) < diff <= timedelta(hours=24):
```

**Para notificaciones de menos de 12 horas:**
```python
if timedelta(0) < diff <= timedelta(hours=12):
```

---

## 📝 Archivos del Proyecto

```
c:\Codigos\GestorTareasUniversitarias\
├── TareasUniversitarias.py          ← Aplicación principal
├── tareas.json                      ← Base de datos de tareas
├── perfil.json                      ← Datos del usuario
├── notificaciones_hoy.json          ← (Se crea automáticamente)
├── requirements.txt                 ← Dependencias
├── README.md                        ← Descripción general
├── IMPLEMENTACION_TECNICA.md        ← Detalles técnicos
├── GUIA_USO.md                      ← Este archivo
└── prueba_monitoreo.py              ← Script de prueba
```

---

## ✨ Características Destacadas

### Optimización de Recursos
- ✅ Hilo daemon (no bloquea el cierre)
- ✅ Sleep eficiente (no consume CPU)
- ✅ Variable de control (puede pausarse si es necesario)

### Robustez
- ✅ Manejo de errores en JSON
- ✅ Tolerancia a fallos de bibliotecas
- ✅ Aislamiento de errores (una tarea defectuosa no arruina el monitoreo)

### Experiencia de Usuario
- ✅ Notificaciones personalizadas con emojis
- ✅ Access rápido desde la bandeja
- ✅ Minimización silenciosa (sin cerrar)
- ✅ Cierre limpio con "Salir"

---

## 🎓 Resumen de Mejoras

| Característica | Antes | Después |
|---|---|---|
| Acceso a la app | Minimizar y buscar | Click en bandeja |
| Monitoreo manual | No había | Automático cada 30 min |
| Notificaciones | Ninguna | Inteligentes y personalizadas |
| Ejecución | Se cerraba | Sigue en segundo plano |
| Recursos | Interfaz siempre visible | Minimizada, bajo consumo |

---

## 📞 Contacto & Soporte

Si tienes problemas:

1. Verifica que las dependencias estén instaladas
2. Revisa el archivo `IMPLEMENTACION_TECNICA.md`
3. Ejecuta `prueba_monitoreo.py` para validar el sistema

¡Disfruta de tu Gestor de Tareas mejorado! 🚀

