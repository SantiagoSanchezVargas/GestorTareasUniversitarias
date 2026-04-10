#!/usr/bin/env python3
"""Script para refactorizar TareasUniversitarias.py"""

import re

# Leer el archivo
with open('TareasUniversitarias.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remover el contenido duplicado (después del primer "if __name__ == "__main__":")
# Encontrar el primer if __name__
match = re.search(r'(if __name__ == "__main__":.*?root\.destroy\(\))', content, re.DOTALL)
if match:
    # Encontrar el final correcto del bloque if __name__ (después de root.destroy())
    first_if_name_end = match.end()
    # Remover todo después de este punto
    content_before_duplicate = content[:first_if_name_end]
    # Agregar comentario de fin
    content_before_duplicate += '\n'
    content = content_before_duplicate
    print("✓ Contenido duplicado removido")

# 2. Actualizar iniciar_onboarding para destruir completamente CTk
old_iniciar = r'''def iniciar_onboarding\(\):
    """Inicia el asistente de configuración inicial"""
    root = ctk\.CTk\(\)
    setup = ProfileSetup\(root\)
    root\.mainloop\(\)
    return setup\.result'''

new_iniciar = '''def iniciar_onboarding():
    """Inicia el asistente de configuración inicial"""
    root = ctk.CTk()
    setup = ProfileSetup(root)
    root.mainloop()
    result = setup.result
    # Destruir completamente la ventana antes de retornar
    try:
        root.destroy()
    except (tk.TclError, AttributeError):
        pass
    return result'''

content = re.sub(old_iniciar, new_iniciar, content)
print("✓ iniciar_onboarding actualizado")

# 3. Actualizar método dibujar_reloj para verificar si widget existe
old_dibujar_reloj = r'''    def dibujar_reloj\(self\):
        """Dibuja el reloj analógico actualizado"""
        # Detener si la ventana se está cerrando
        if self\.closing:
            return
        
        try:
            self\.canvas_reloj\.delete\("all"\)
        except tk\.TclError:
            return'''

new_dibujar_reloj = '''    def dibujar_reloj(self):
        """Dibuja el reloj analógico actualizado"""
        # Detener si la ventana se está cerrando
        if self.closing:
            return
        
        # Verificar que el widget existe antes de intentar operaciones
        try:
            if not self.canvas_reloj.winfo_exists():
                return
            self.canvas_reloj.delete("all")
        except (tk.TclError, AttributeError):
            return'''

content = re.sub(old_dibujar_reloj, new_dibujar_reloj, content)
print("✓ dibujar_reloj actualizado")

# 4. Actualizar _al_cerrar_ventana para manejar protocolo de cierre
old_al_cerrar = r'''    def _al_cerrar_ventana\(self\):
        """Minimiza la ventana a la bandeja en lugar de cerrar"""
        self\.closing = True
        self\.root\.withdraw\(\)'''

new_al_cerrar = '''    def _al_cerrar_ventana(self):
        """Cancela tareas programadas y cierra la aplicación de forma segura"""
        self.closing = True
        # Cancelar todas las tareas programadas con after
        self._cancelar_tareas_after()
        # Detener la aplicación de forma segura
        self.root.withdraw()
    
    def _cancelar_tareas_after(self):
        """Cancela todas las tareas pendientes programadas con after"""
        try:
            # Obtener todas las tareas después pendientes
            for id_tarea in self.root.after_info():
                try:
                    self.root.after_cancel(id_tarea)
                except (tk.TclError, ValueError):
                    pass
        except (AttributeError, tk.TclError):
            pass'''

content = re.sub(old_al_cerrar, new_al_cerrar, content)
print("✓ _al_cerrar_ventana actualizado")

# 5. Actualizar bloque if __name__ para control secuencial
old_if_name = r'''if __name__ == "__main__":
    perfil = cargar_perfil\(\)
    if not perfil:
        perfil = iniciar_onboarding\(\)
        if not perfil:
            raise SystemExit

    root = ctk\.CTk\(\)
    app = App\(root, perfil\)
    try:
        root\.mainloop\(\)
    except KeyboardInterrupt:
        app\.closing = True
        root\.destroy\(\)'''

new_if_name = '''if __name__ == "__main__":
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
            os._exit(0)'''

content = re.sub(old_if_name, new_if_name, content)
print("✓ bloque if __name__ actualizado")

# Guardar el archivo
with open('TareasUniversitarias.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✓ Refactorización completada exitosamente")
