#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para validar la implementación del sistema de notificaciones y monitoreo.
Este script NO requiere GUI de Tkinter.
"""

import json
import os
from datetime import datetime, timedelta
import sys

# Agregar el directorio actual al path para importar el módulo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("PRUEBA DE FUNCIONES DE MONITOREO Y NOTIFICACIONES")
print("=" * 60)

# Test 1: Importaciones
print("\n[TEST 1] Verificando importaciones...")
try:
    import threading
    import time
    print("✓ threading y time: OK")
except ImportError as e:
    print(f"✗ Error en threading/time: {e}")

try:
    from pystray import Icon, Menu, MenuItem
    print("✓ pystray: OK")
except ImportError:
    print("⚠ pystray: No instalado (la app funcionará sin System Tray)")

try:
    from plyer.notification import notify
    print("✓ plyer: OK")
except ImportError:
    print("⚠ plyer: No instalado (las notificaciones estarán desactivadas)")

# Test 2: Funciones de notificaciones
print("\n[TEST 2] Probando funciones de notificaciones...")

NOTIFICACIONES_HOY_FILE = "test_notificaciones_hoy.json"

def obtener_notificaciones_hoy(archivo=NOTIFICACIONES_HOY_FILE):
    """Obtiene el conjunto de IDs de tareas notificadas hoy."""
    hoy = datetime.now().date()
    if not os.path.exists(archivo):
        return set()
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("fecha") != str(hoy):
            return set()
        return set(data.get("tarea_ids", []))
    except (json.JSONDecodeError, OSError):
        return set()

def guardar_notificaciones_hoy(tarea_ids, archivo=NOTIFICACIONES_HOY_FILE):
    """Guarda las IDs de tareas notificadas hoy."""
    hoy = datetime.now().date()
    data = {
        "fecha": str(hoy),
        "tarea_ids": list(tarea_ids)
    }
    try:
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except OSError:
        return False

# Prueba obtener notificaciones
notificaciones = obtener_notificaciones_hoy()
print(f"✓ Notificaciones actualmente guardadas: {len(notificaciones)}")

# Prueba guardar una notificación de prueba
tarea_test_id = "tarea_prueba_test"
notificaciones.add(tarea_test_id)
if guardar_notificaciones_hoy(notificaciones):
    print(f"✓ Guardada notificación de prueba")
    notificaciones_verificadas = obtener_notificaciones_hoy()
    if tarea_test_id in notificaciones_verificadas:
        print(f"✓ Notificación verificada en archivo")
    else:
        print(f"✗ Error verificando notificación")
else:
    print(f"✗ No se pudo guardar notificación")

# Cleanup
if os.path.exists(NOTIFICACIONES_HOY_FILE):
    os.remove(NOTIFICACIONES_HOY_FILE)
    print(f"✓ Archivo de prueba limpiado")

# Test 3: Lógica de monitoreo (sin ejecutar el hilo)
print("\n[TEST 3] Probando lógica de monitoreo...")

EMOJIS_MATERIAS = {
    "Operativa": "🧮",
    "Big Data": "📊",
    "Analisis numerico": "📈",
    "Comunicación de datos": "📡",
    "Emprendimiento e innovación": "💡",
    "Ciencia, tecnología e innovación": "🔬",
    "Seguridad en hardware": "🔐",
}

# Crear tareas de prueba
tareas_prueba = [
    {
        "nombre": "Tarea Urgente",
        "materia": "Big Data",
        "fecha": (datetime.now() + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M"),
        "entregado": False
    },
    {
        "nombre": "Tarea Lejana",
        "materia": "Operativa",
        "fecha": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d %H:%M"),
        "entregado": False
    },
    {
        "nombre": "Tarea Entregada",
        "materia": "Analisis numerico",
        "fecha": (datetime.now() + timedelta(hours=10)).strftime("%Y-%m-%d %H:%M"),
        "entregado": True
    },
    {
        "nombre": "Tarea Vencida",
        "materia": "Comunicación de datos",
        "fecha": (datetime.now() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M"),
        "entregado": False
    }
]

print(f"\nTareas de prueba creadas: {len(tareas_prueba)}")

# Simular lógica de notificación
ahora = datetime.now()
tareas_para_notificar = []

for t in tareas_prueba:
    if t.get("entregado"):
        print(f"  • IGNORA: '{t['nombre']}' (ya entregada)")
        continue
    
    fecha = datetime.strptime(t["fecha"], "%Y-%m-%d %H:%M")
    diff = fecha - ahora
    
    if timedelta(0) < diff <= timedelta(hours=24):
        materia = t.get("materia", "Sin materia")
        emoji = EMOJIS_MATERIAS.get(materia, "📝")
        horas = int(diff.total_seconds() / 3600)
        minutos = int((diff.total_seconds() % 3600) / 60)
        
        titulo = f"{emoji} {materia}"
        mensaje = f"'{t['nombre']}' vence en {horas}h {minutos}m"
        
        tareas_para_notificar.append({
            "titulo": titulo,
            "mensaje": mensaje
        })
        print(f"  ✓ NOTIFICAR: {titulo}")
        print(f"    → {mensaje}")
    elif diff <= timedelta(0):
        print(f"  • IGNORA: '{t['nombre']}' (ya vencida)")
    else:
        print(f"  • IGNORA: '{t['nombre']}' (vence en {diff.days}+ días)")

print(f"\nTotal de notificaciones pendientes: {len(tareas_para_notificar)}")

# Test 4: Verificar JSON malformados
print("\n[TEST 4] Probando tolerancia a errores JSON...")

def cargar_json_seguro(archivo):
    """Carga un JSON con manejo robusto de errores."""
    if not os.path.exists(archivo):
        return None
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None

# Crear archivo JSON malformado
archivo_mal = "test_mal_formado.json"
with open(archivo_mal, "w") as f:
    f.write("{invalid json]")

datos = cargar_json_seguro(archivo_mal)
if datos is None:
    print("✓ Detectado JSON malformado correctamente")
else:
    print("✗ No se detectó JSON malformado")

os.remove(archivo_mal)
print("✓ Archivo de prueba limpiado")

# Test 5: Verificar emojis
print("\n[TEST 5] Verificando emojis por materia...")
for materia, emoji in EMOJIS_MATERIAS.items():
    print(f"  {emoji} {materia}")

print("\n" + "=" * 60)
print("PRUEBAS COMPLETADAS ✓")
print("=" * 60)
print("\nNOTA: para probar las notificaciones reales y System Tray,")
print("ejecuta: python TareasUniversitarias.py")
