#!/usr/bin/env python3
"""Script para fase 2 de refactorización: actualizar métodos específicos"""

# Leer el archivo
with open('TareasUniversitarias.py', 'r', encoding='utf-8') as f:
    contenido = f.read()

cambios_realizados = []

# 1. Actualizar iniciar_onboarding
old_iniciar = '''def iniciar_onboarding():
    """Inicia el asistente de configuración inicial"""
    root = ctk.CTk()
    setup = ProfileSetup(root)
    root.mainloop()
    return setup.result'''

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

if old_iniciar in contenido:
    contenido = contenido.replace(old_iniciar, new_iniciar)
    cambios_realizados.append("✓ iniciar_onboarding actualizado")
else:
    print("⚠ No se encontró patrón exacto para iniciar_onboarding")

# 2. Actualizar dibujar_reloj
old_dibujar = '''    def dibujar_reloj(self):
        """Dibuja el reloj analógico actualizado"""
        # Detener si la ventana se está cerrando
        if self.closing:
            return
        
        try:
            self.canvas_reloj.delete("all")
        except tk.TclError:
            return

        ancho = self.canvas_reloj.winfo_width()'''

new_dibujar = '''    def dibujar_reloj(self):
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
            return

        ancho = self.canvas_reloj.winfo_width()'''

if old_dibujar in contenido:
    contenido = contenido.replace(old_dibujar, new_dibujar)
    cambios_realizados.append("✓ dibujar_reloj actualizado")
else:
    # Intentar con sin los comentarios de cierre
    old_dibujar2 = '''    def dibujar_reloj(self):
        """Dibuja el reloj analógico actualizado"""
        # Detener si la ventana se está cerrando
        if self.closing:
            return
        
        try:
            self.canvas_reloj.delete("all")
        except tk.TclError:
            return'''

    if old_dibujar2 in contenido:
        # Buscar el siguiente "ancho =" para completar el patrón
        idx = contenido.find(old_dibujar2)
        if idx != -1:
            # Buscar la siguiente línea válida
            rest = contenido[idx+len(old_dibujar2):idx+len(old_dibujar2)+200]
            if 'ancho = self.canvas_reloj.winfo_width()' in rest:
                # Tenemos el patrón completo
                full_old = old_dibujar2 + '\n\n        ancho = self.canvas_reloj.winfo_width()'
                full_new = new_dibujar
                contenido = contenido.replace(full_old, full_new)
                cambios_realizados.append("✓ dibujar_reloj actualizado (patrón alternativo)")
    else:
        print("⚠ No se encontró patrón para dibujar_reloj")

# 3. Actualizar _al_cerrar_ventana  
old_cerrar = '''    def _al_cerrar_ventana(self):
        """Minimiza la ventana a la bandeja en lugar de cerrar"""
        self.closing = True
        self.root.withdraw()'''

new_cerrar = '''    def _al_cerrar_ventana(self):
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

if old_cerrar in contenido:
    contenido = contenido.replace(old_cerrar, new_cerrar)
    cambios_realizados.append("✓ _al_cerrar_ventana actualizado")
else:
    print("⚠ No se encontró patrón exacto para _al_cerrar_ventana")

# Guardar el archivo
with open('TareasUniversitarias.py', 'w', encoding='utf-8') as f:
    f.write(contenido)

# Reportar cambios
print("\n✓ Refactorización completada (Phase 2)")
for cambio in cambios_realizados:
    print(cambio)
