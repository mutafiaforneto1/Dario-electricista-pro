import os

ruta_test = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/01_TRABAJOS/Andrea deudora.md"

print(f"--- Probando acceso a: {ruta_test} ---")

if os.path.exists(ruta_test):
    print("✅ ¡El archivo existe!")
    with open(ruta_test, 'r', encoding='utf-8', errors='ignore') as f:
        contenido = f.read()
        print("--- Contenido de la nota (primeros 200 caracteres) ---")
        print(contenido[:200])
        print("-----------------------------------------------------")
else:
    print("❌ El archivo NO existe en esa ruta.")
    print("Carpetas encontradas en 01_TRABAJOS:")
    try:
        print(os.listdir("/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/01_TRABAJOS"))
    except:
        print("No se pudo listar la carpeta.")
