import os
import re
import subprocess
from datetime import datetime

# CONFIGURACIÓN DE RUTAS
VAULT_PATH = "/storage/emulated/0/Documents/Obsidian trabajo optimizado 2"
TRABAJOS_PATH = os.path.join(VAULT_PATH, "01_TRABAJOS")

def enviar_notificacion(titulo, mensaje_corto, mensaje_largo):
    """
    Usa la API de Termux para crear una notificación expandible.
    """
    try:
        # --big-text es la clave para que Android permita expandirla
        subprocess.run([
            "termux-notification",
            "-t", titulo,
            "-c", mensaje_corto,
            "--big-text", mensaje_largo,
            "--priority", "high",
            "--id", "agenda_dario",
            "--icon", "event_note",
            "--led-color", "00bfff",
            "--group", "dario_jobs"
        ])
    except Exception as e:
        print(f"Error: {e}")

def analizar_notas():
    en_curso = []
    pendientes_cobro = []
    
    if not os.path.exists(TRABAJOS_PATH):
        return None, None

    for archivo in os.listdir(TRABAJOS_PATH):
        if archivo.endswith(".md"):
            try:
                with open(os.path.join(TRABAJOS_PATH, archivo), 'r', encoding='utf-8') as f:
                    # Leemos las primeras 20 líneas para buscar los estados
                    lineas = [next(f).lower() for _ in range(20)]
                    contenido = "".join(lineas)
                    nombre_obra = archivo.replace(".md", "").replace("_", " ")
                    
                    if "estado: en_curso" in contenido or 'estado: "en_curso"' in contenido:
                        en_curso.append(nombre_obra)
                    elif "pagado: false" in contenido and "estado: finalizado" in contenido:
                        pendientes_cobro.append(nombre_obra)
            except StopIteration:
                pass
            except Exception as e:
                print(f"Error leyendo {archivo}: {e}")

    return en_curso, pendientes_cobro

def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Procesando agenda...")
    obras_curso, obras_cobro = analizar_notas()
    
    if obras_curso is None:
        print("❌ Carpeta no encontrada.")
        return

    # Resumen que se ve sin expandir
    resumen_breve = f"👷 {len(obras_curso)} en curso | 💰 {len(obras_cobro)} por cobrar"
    
    # Detalle que se ve al deslizar hacia abajo la notificación
    detalle = "📋 DETALLE DE TRABAJOS:\n\n"
    
    if obras_curso:
        detalle += "🚧 EN CURSO:\n"
        for obra in obras_curso:
            detalle += f"• {obra.upper()}\n"
    else:
        detalle += "✅ Sin obras activas.\n"
        
    if obras_cobro:
        detalle += "\n💵 PENDIENTES DE PAGO:\n"
        for obra in obras_cobro:
            detalle += f"• {obra.upper()}\n"
    
    titulo = f"Resumen de Obra - {datetime.now().strftime('%d/%m')}"
    
    enviar_notificacion(titulo, resumen_breve, detalle)
    print("✅ Notificación enviada. Deslizá hacia abajo en Android para ver el detalle.")

if __name__ == "__main__":
    main()
