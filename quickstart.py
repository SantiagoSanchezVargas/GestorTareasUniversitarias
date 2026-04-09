#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🚀 QUICKSTART - Gestor de Tareas Universitarias

Este script facilita la instalación y ejecución inmediata.
"""

import subprocess
import sys
import os
from pathlib import Path

def instalar_dependencias():
    """Instala las dependencias requeridas."""
    print("\n" + "="*60)
    print("📦 INSTALANDO DEPENDENCIAS")
    print("="*60)
    
    try:
        # Intentar instalar desde requirements.txt
        requirements_path = Path(__file__).parent / "requirements.txt"
        if requirements_path.exists():
            print(f"\n📥 Instalando desde {requirements_path}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "-r", str(requirements_path)
            ])
            print("\n✅ Dependencias instaladas correctamente")
            return True
        else:
            print("⚠️  requirements.txt no encontrado")
            print("Intentando instalación manual...")
            
            paquetes = ["tkcalendar", "pillow", "pystray", "plyer"]
            for paquete in paquetes:
                print(f"\n📥 Instalando {paquete}...")
                try:
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install", paquete
                    ])
                    print(f"✅ {paquete} instalado")
                except subprocess.CalledProcessError:
                    print(f"⚠️  No se pudo instalar {paquete}")
                    print("   (La app puede funcionar sin él)")
    
    except Exception as e:
        print(f"\n❌ Error durante instalación: {e}")
        print("\nIntentar instalación manual:")
        print("  pip install tkcalendar pillow pystray plyer")
        return False
    
    return True


def ejecutar_app():
    """Ejecuta la aplicación principal."""
    print("\n" + "="*60)
    print("🎯 INICIANDO APLICACIÓN")
    print("="*60 + "\n")
    
    try:
        script_principal = Path(__file__).parent / "TareasUniversitarias.py"
        if not script_principal.exists():
            print(f"❌ No se encontró {script_principal}")
            return False
        
        print(f"▶️  Ejecutando {script_principal}...\n")
        subprocess.call([sys.executable, str(script_principal)])
        return True
        
    except Exception as e:
        print(f"❌ Error al ejecutar: {e}")
        return False


def run_tests():
    """Ejecuta los tests de validación."""
    print("\n" + "="*60)
    print("🧪 EJECUTANDO PRUEBAS")
    print("="*60 + "\n")
    
    try:
        script_prueba = Path(__file__).parent / "prueba_monitoreo.py"
        if script_prueba.exists():
            subprocess.call([sys.executable, str(script_prueba)])
            return True
        else:
            print(f"⚠️  {script_prueba} no encontrado")
            return False
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        return False


def menu_principal():
    """Muestra menú interactivo."""
    while True:
        print("\n" + "="*60)
        print("📚 GESTOR DE TAREAS UNIVERSITARIAS - MENÚ")
        print("="*60)
        print("\n¿Qué deseas hacer?\n")
        print("  1️⃣  Instalar dependencias")
        print("  2️⃣  Ejecutar aplicación")
        print("  3️⃣  Ejecutar pruebas")
        print("  4️⃣  Instalar + Ejecutar")
        print("  5️⃣  Ver documentación")
        print("  0️⃣  Salir")
        print("\n" + "-"*60)
        
        opcion = input("\nElige una opción [0-5]: ").strip()
        
        if opcion == "1":
            instalar_dependencias()
        elif opcion == "2":
            ejecutar_app()
        elif opcion == "3":
            run_tests()
        elif opcion == "4":
            if instalar_dependencias():
                ejecutar_app()
        elif opcion == "5":
            mostrar_documentacion()
        elif opcion == "0":
            print("\n👋 ¡Hasta luego!\n")
            break
        else:
            print("\n❌ Opción inválida. Intenta de nuevo.")


def mostrar_documentacion():
    """Muestra ubicación de documentación."""
    print("\n" + "="*60)
    print("📖 DOCUMENTACIÓN DISPONIBLE")
    print("="*60)
    
    docs = {
        "GUIA_USO.md": "📖 Guía práctica de uso (COMIENZA AQUÍ)",
        "IMPLEMENTACION_TECNICA.md": "🔧 Detalles técnicos de implementación",
        "RESUMEN_CAMBIOS.md": "📋 Resumen ejecutivo de cambios",
        "README.md": "📚 Descripción general del proyecto",
    }
    
    ruta = Path(__file__).parent
    print(f"\nArchivos disponibles en: {ruta}\n")
    
    for archivo, descripcion in docs.items():
        ruta_completa = ruta / archivo
        estado = "✓" if ruta_completa.exists() else "✗"
        print(f"  {estado} {descripcion}")
        print(f"    → {archivo}")
    
    print("\n💡 Abre GUIA_USO.md para comenzar")


def main():
    """Entrada principal del programa."""
    print("\n" + "="*60)
    print("🚀 QUICKSTART - GESTOR DE TAREAS UNIVERSITARIAS")
    print("="*60)
    print("\n📌 Primera ejecución: INSTALA DEPENDENCIAS +EJECUTA APP (opción 4)")
    print("📌 Ejecuciones posteriores: Opción 2\n")
    
    if len(sys.argv) > 1:
        # Argumentos de línea de comandos
        if sys.argv[1] == "--install":
            instalar_dependencias()
        elif sys.argv[1] == "--run":
            ejecutar_app()
        elif sys.argv[1] == "--test":
            run_tests()
        elif sys.argv[1] == "--docs":
            mostrar_documentacion()
        else:
            print(f"Opción desconocida: {sys.argv[1]}")
            print("\nUso:")
            print("  python quickstart.py --install  (Instalar dependencias)")
            print("  python quickstart.py --run      (Ejecutar app)")
            print("  python quickstart.py --test     (Ejecutar pruebas)")
            print("  python quickstart.py --docs     (Ver documentación)")
            print("  python quickstart.py             (Menú interactivo)")
    else:
        # Menú interactivo
        menu_principal()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada por el usuario\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}\n")
        sys.exit(1)
