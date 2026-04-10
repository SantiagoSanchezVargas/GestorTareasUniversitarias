#!/usr/bin/env python3
"""Script mejorado para refactorizar TareasUniversitarias.py"""

# Leer el archivo
with open('TareasUniversitarias.py', 'r', encoding='utf-8') as f:
    lineas = f.readlines()

# 1. Encontrar la línea donde comienza la duplicación (después del primer if __name__)
# Buscamos el primer "if __name__" y luego encontramos el final de ese bloque

primer_if_name_idx = None
for i, linea in enumerate(lineas):
    if 'if __name__ == "__main__":' in linea and primer_if_name_idx is None:
        primer_if_name_idx = i
        break

# Si encontramos el primer if __name__, encontramos dónde termina el bloque
if primer_if_name_idx is not None:
    # El bloque if __name__ termina approx en root.destroy() o root.mainloop()
    # Buscamos la primera línea que comienza sin indentación después de if __name__
    fin_bloque_idx = None
    for i in range(primer_if_name_idx + 1, len(lineas)):
        linea = lineas[i]
        # Si la línea comienza con "import" sin indentación, hemos encontrado el duplicado
        if linea.startswith('import ') or (linea.strip() and not linea.startswith(' ') and not linea.startswith('\t')):
            if not linea.startswith('#'):  # Ignorar comentarios
                fin_bloque_idx = i
                break
    
    if fin_bloque_idx is None:
        # Si no encontramos el límite, tomar las primeras ~1250 líneas
        fin_bloque_idx = 1250
    
    # Remover las líneas desde fin_bloque_idx hasta el final
    lineas = lineas[:fin_bloque_idx]
    print(f"✓ Removido contenido duplicado (lineas {fin_bloque_idx} a fin)")

# 2. Ahora actualizar el bloque if __name__ al final
# Encontrar el nuevo final después de truncar
primer_if_name_idx = None
for i, linea in enumerate(lineas):
    if 'if __name__ == "__main__":' in linea:
        primer_if_name_idx = i
        break

if primer_if_name_idx is not None:
    # Reemplazar el bloque if __name__ completo
    # Primero encontrar dónde termina (buscamos root.mainloop() u otra última línea)
    fin_actual = len(lineas)
    for i in range(primer_if_name_idx + 1, len(lineas)):
        if lineas[i].startswith('import '):
            fin_actual = i
            break
    
    # Crear el nuevo bloque if __name__
    nuevo_bloque = '''if __name__ == "__main__":
    # ==================== CONFIGURACIÓN ====================
    # Primero, cargar o crear perfil
    perfil = cargar_perfil()
    if not perfil:
        print("Iniciando asistente de configuración...")
        perfil = iniciar_onboarding()
        if not perfil:
            print("Configuración cancelada.")
            raise SystemExit
        print("Perfil configurado exitosamente.")
    
    # ==================== APLICACIÓN ====================
    # Luego, crear y ejecutar la aplicación principal
    print("Iniciando Gestor de Tareas...")
    root = ctk.CTk()
    app = App(root, perfil)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\\nCerrando aplicación...")
        app.closing = True
        root.destroy()
    finally:
        # Asegurar cierre limpio
        try:
            app._salir_aplicacion()
        except Exception:
            os._exit(0)
'''
    
    # Reemplazar las líneas del bloque if __name__
    lineas = lineas[:primer_if_name_idx] + [nuevo_bloque + '\n']
    print("✓ Bloque if __name__ actualizado")

# Guardar el archivo
with open('TareasUniversitarias.py', 'w', encoding='utf-8') as f:
    f.writelines(lineas)

print("✓ Refactorización completada (Phase 1)")
print(f"✓ Archivo contiene {len(lineas)} líneas")
