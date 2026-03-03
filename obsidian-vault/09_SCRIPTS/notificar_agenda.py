import os
import subprocess
from datetime import datetime
import sys

# CONFIGURACIÓN DE RUTA (Ahora busca en todo el Vault)
VAULT_PATH = "/storage/emulated/0/Documents/Obsidian trabajo optimizado 2"

def enviar_notificacion(titulo, mensaje_corto, detalle_completo):
    """Manda la notificación con el botón de acción para ver el detalle"""
    try:
        script_path = os.path.abspath(__file__)
        subprocess.run([
            "termux-notification",
            "-t", titulo,
            "-c", mensaje_corto,
            "--priority", "high",
            "--id", "agenda_dario",
            "--icon", "construction", 
            "--led-color", "ffa500",
            "--action", f"python {script_path} --show-popup" 
        ])
    except Exception as e:
        print(f"Error: {e}")

def mostrar_popup(detalle):
    """Muestra el detalle en un cuadro de diálogo centrado"""
    subprocess.run([
        "termux-dialog", "confirm",
        "-t", "🛠️ Agenda de Trabajo",
        "-i", detalle
    ])

def analizar_todo_el_vault():
    en_curso = []
    pendientes_cobro = []
    
    # Emojis que usás para identificar trabajos
    EMOJIS_TRABAJO = ["🛠️", "🔨"]

    # Buscamos en todas las subcarpetas del Vault
    for raiz, carpetas, archivos in os.walk(VAULT_PATH):
        for archivo in archivos:
            if archivo.endswith(".md"):
                # CASO 1: Si el nombre tiene alguno de tus emojis
                tiene_emoji = any(e in archivo for e in EMOJIS_TRABAJO)
                
                nombre_limpio = archivo.replace(".md", "")
                for e in EMOJIS_TRABAJO:
                    nombre_limpio = nombre_limpio.replace(e, "")
                nombre_limpio = nombre_limpio.strip().upper()

                if tiene_emoji:
                    en_curso.append(nombre_limpio)
                else:
                    # CASO 2: Si no tiene emoji en el nombre, miramos adentro
                    try:
                        with open(os.path.join(raiz, archivo), 'r', encoding='utf-8') as f:
                            contenido = "".join([next(f).lower() for _ in range(20)])
                            if "estado: en_curso" in contenido or 'estado: "en_curso"' in contenido:
                                en_curso.append(nombre_limpio)
                            elif "pagado: false" in contenido and "estado: finalizado" in contenido:
                                pendientes_cobro.append(nombre_limpio)
                    except:
                        pass

    return en_curso, pendientes_cobro

def main(popup_mode=False):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Escaneando todo el Vault...")
    obras_curso, obras_cobro = analizar_todo_el_vault()
    
    detalle = ""
    if obras_curso:
        detalle += "🚧 TRABAJOS ACTIVOS:\n"
        for o in obras_curso:
            detalle += f"• {o}\n"
        detalle += "\n"
    
    if obras_cobro:
        detalle += "💵 POR COBRAR:\n"
        for o in obras_cobro:
            detalle += f"• {o}\n"
    
    if not detalle: 
        detalle = "No encontré notas con 🛠️, 🔨 o estado 'en_curso'."

    if popup_mode:
        mostrar_popup(detalle)
    else:
        resumen = f"🛠️ {len(obras_curso)} en obra | 💰 {len(obras_cobro)} cobros"
        titulo = f"Resumen Diario - {datetime.now().strftime('%d/%m')}"
        enviar_notificacion(titulo, resumen, detalle)
        print(f"✅ Notificación enviada: {resumen}")

if __name__ == "__main__":
    is_popup = "--show-popup" in sys.argv
    main(popup_mode=is_popup)

