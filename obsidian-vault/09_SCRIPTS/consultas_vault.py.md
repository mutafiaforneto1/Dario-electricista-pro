import os

# Rutas manuales y directas
VAULT = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault"
TRABAJOS = VAULT + "/01_TRABAJOS"
PRECIOS = VAULT + "/08_PRECIOS/Lista de Precios DistriElectro.md"

async def cmd_vencidos(u, c):
    try:
        archivos = os.listdir(TRABAJOS)
        pendientes = []
        for a in archivos:
            if a.endswith(".md"):
                with open(TRABAJOS + "/" + a, 'r', encoding='utf-8') as f:
                    if "- [ ]" in f.read():
                        pendientes.append(a.replace(".md", ""))
        
        if pendientes:
            texto = "PENDIENTES DE COBRO:\n" + "\n".join(pendientes)
        else:
            texto = "No encontre deudas."
        await u.message.reply_text(texto)
    except Exception as e:
        await u.message.reply_text("Error leyendo archivos.")

async def cmd_catalogo(u, c):
    try:
        with open(PRECIOS, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
            # Solo enviamos las primeras 10 lineas para evitar errores
            texto = "PRECIOS:\n" + "".join(lineas[:10])
            await u.message.reply_text(texto)
    except:
        await u.message.reply_text("No pude leer los precios.")

async def cmd_stats(u, c):
    archivos = [f for f in os.listdir(TRABAJOS) if f.endswith('.md')]
    await u.message.reply_text(f"Tenes {len(archivos)} trabajos.")