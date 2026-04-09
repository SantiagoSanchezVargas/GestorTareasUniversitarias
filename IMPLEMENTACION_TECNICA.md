# 🚀 Implementación: Sistema de Second Plano y Monitoreo de Tareas

## 📋 Descripción General

Se ha implementado un sistema robusto que permite que la aplicación Gestor de Tareas se ejecute en segundo plano con las siguientes características principales:

### ✨ Características Implementadas

#### 1. **System Tray (Bandeja de Tareas)**
- **Librería**: `pystray`
- **Funcionalidad**:
  - Icono en la barra de tareas del sistema operativo
  - Menú contextual con opciones:
    - **Abrir**: Restaura la ventana principal
    - **Salir**: Cierra completamente la aplicación
  - Minimización inteligente: Al cerrar la ventana, se minimiza a la bandeja (no se cierra)
  - Protocolo `WM_DELETE_WINDOW`: Utiliza `root.withdraw()` para ocultar la ventana sin terminar el proceso

#### 2. **Hilo de Monitoreo Optimizado**
- **Función**: `monitoreo_tareas_background()`
- **Características**:
  - Se ejecuta inmediatamente al iniciar la aplicación
  - Se ejecuta nuevamente cada **30 minutos** (1800 segundos)
  - Funcionamiento como **hilo daemon** para no bloquear la UI
  - **Optimización de RAM**: Utiliza `time.sleep()` para no consumir ciclos de CPU innecesarios

#### 3. **Lógica de Notificación Inteligente**
- **Librería**: `plyer`
- **Filtrado de tareas**:
  - Solo procesa tareas con estado **'Pendiente'** o **'Próximo'**
  - Ignora tareas ya entregadas
  
- **Condición de notificación**:
  - Se activa si la tarea vence en **menos de 24 horas**
  - Valida que NO haya sido notificada **hoy** (basado en `notificaciones_hoy.json`)
  
- **Personalización de notificaciones**:
  - Título: `{emoji} {nombre_materia}` (ejemplo: "📊 Big Data")
  - Mensaje: `'{nombre_tarea}' vence en {tiempo}` (ejemplo: "Proyecto final vence en 2h 45m")
  - Emojis por materia para identificación visual:
    - 🧮 Operativa
    - 📊 Big Data
    - 📈 Análisis numérico
    - 📡 Comunicación de datos
    - 💡 Emprendimiento e innovación
    - 🔬 Ciencia, tecnología e innovación
    - 🔐 Seguridad en hardware

#### 4. **Manejo de Errores Robusto**
- **Gestión de archivos JSON**:
  - Si `tareas.json` está vacío o mal formado, el hilo continúa sin fallar
  - Si `perfil.json` no existe, la aplicación inicia con valores por defecto
  - Los errores de lectura/escritura se ignoran silenciosamente

- **Tolerancia de fallos**:
  - Si una tarea individual tiene datos inválidos, se omite y continúa con las siguientes
  - Si `plyer` no está disponible, las notificaciones se desactivan automáticamente
  - Si `pystray` no está disponible, la app funciona normalmente sin System Tray

---

## 🔧 Detalles Técnicos

### Archivos Involucrados

| Archivo | Propósito |
|---------|-----------|
| `TareasUniversitarias.py` | Aplicación principal con todas las características |
| `tareas.json` | Base de datos de tareas |
| `perfil.json` | Datos del perfil del usuario |
| `notificaciones_hoy.json` | Registro de notificaciones enviadas hoy |
| `requirements.txt` | Dependencias del proyecto |

### Funciones Clave Nuevas

#### `monitoreo_tareas_background(archivo_tareas: str)`
```python
# Se ejecuta en un hilo daemon separado
# Itera cada 30 minutos
# Verifica tareas próximas a vencer
# Envía notificaciones inteligentes
```

#### `obtener_notificaciones_hoy() -> set`
- Obtiene las IDs de tareas ya notificadas hoy
- Verifica la fecha actual para resetear si es un nuevo día

#### `guardar_notificaciones_hoy(tarea_ids: set)`
- Persiste las notificaciones enviadas junto con la fecha

#### `enviar_notificacion(titulo: str, mensaje: str)`
- Wrapper seguro alrededor de `plyer.notification.notify()`
- Captura excepciones para evitar fallos

### Métodos de la Clase App

#### `_al_cerrar_ventana()`
- Ejecutado por protocolo `WM_DELETE_WINDOW`
- Llama a `root.withdraw()` para ocultar la ventana

#### `_abrir_desde_bandeja()`
- Restaura la ventana desde la bandeja con `deiconify()`
- `lift()` y `focus()` para traer al frente

#### `_salir_aplicacion()`
- Detiene el icono de la bandeja
- Usa `os._exit(0)` para cierre completo

#### `_crear_icono_bandeja()`
- Crea el icono en la bandeja del sistema
- Configura el menú con opciones de Abrir y Salir
- Ejecuta en un hilo separado para no bloquear la UI

---

## 📦 Dependencias

```
tkcalendar       # Selector de fecha
pillow           # Procesamiento de imágenes
pystray          # Icono en System Tray
plyer            # Notificaciones del sistema
```

### Instalación
```bash
pip install -r requirements.txt
```

---

## 🎯 Flujo de Ejecución

1. **Inicio**: La aplicación carga el perfil del usuario
2. **UI Principal**: Se construye la interfaz de Tkinter
3. **Protocolo WM_DELETE_WINDOW**: Se configura para minimizar en lugar de cerrar
4. **Hilo de Monitoreo**: Se inicia automáticamente (daemon)
5. **System Tray**: Se crea el icono en la bandeja (en hilo separado)
6. **Ciclo de Monitoreo**:
   - Cada 30 minutos (después de la primera ejecución inmediata)
   - Lee `tareas.json` y `perfil.json`
   - Filtra tareas Pendiente/Próximo
   - Envía notificaciones si vencen en < 24h
   - Actualiza el archivo de notificaciones del día

---

## 🛡️ Seguridad y Estabilidad

- **Daemon Threads**: Los hilos son daemon para no bloquear el cierre de la aplicación
- **Manejo de Excepciones**: Cada bloque crítico está envuelto en try-except
- **Sin Bloqueos**: Uso de `time.sleep()` en lugar de loops activos
- **Graceful Degradation**: Si una librería opcional no está disponible, la app sigue funcionando
- **Aislamiento de Errores**: El error en una tarea no afecta a las otras

---

## 🔍 Testing

Para verificar que todo funciona:

1. **Instalaciones requeridas**:
   ```bash
   cd c:\Codigos\GestorTareasUniversitarias
   pip install -r requirements.txt
   ```

2. **Ejecutar la aplicación**:
   ```bash
   python TareasUniversitarias.py
   ```

3. **Verificar System Tray**:
   - Busca el icono en la esquina inferior derecha de la pantalla
   - Haz clic derecho para ver el menú

4. **Verificar Notificaciones**:
   - Crea una tarea que venza en menos de 24 horas
   - Espera a que el hilo de monitoreo la procese (o 30 segundos para la primera ejecución)
   - Deberías recibir una notificación del sistema

---

## 📝 Notas Importantes

- **Archivo notificaciones_hoy.json**: Se crea automáticamente el primer día. Se resetea cada nuevo día.
- **Emojis**: Los emojis en las notificaciones dependen del sistema operativo y la fuente del terminal
- **Permisos**: En algunos SO, la app podría solicitar permisos para notificaciones
- **Performance**: El hilo de monitoreo consume mínimos recursos gracias a `time.sleep()`

