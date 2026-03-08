import os
from datetime import datetime

VAULT = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault"
TRABAJOS_DIR = os.path.join(VAULT, "01_TRABAJOS")

def obtener_agenda_dia():
    hoy = datetime.now().strftime("%Y-%m-%d")
    pendientes = []
    # Busca en todas tus fichas de trabajo
    for archivo in os.listdir(TRABAJOS_DIR):
        if archivo.endswith(".md"):
            with open(os.path.join(TRABAJOS_DIR, archivo), 'r') as f:
                if hoy in f.read():
                    pendientes.append(archivo.replace(".md", ""))
    
    if not pendientes:
        return "☕ No hay trabajos programados para hoy. ¡Día tranquilo!"
    
    msg = f"⚡ *AGENDA DEL DÍA ({hoy})*\n\n"
    for p in pendientes:
        msg += f"📍 {p}\n"
    return msg
