import requests
import os

def obtener_blue():
    try:
        r = requests.get("https://dolarapi.com/v1/dolares/blue", timeout=10)
        return r.json()['venta']
    except:
        return 1440  # Valor de respaldo

# Precios base en USD (Ajustalos a tu gusto)
materiales = {
    "cable25": ["Cable 2.5mm (100m)", 45.5],
    "cable15": ["Cable 1.5mm (100m)", 32.0],
    "disyuntor25": ["Disyuntor 25A Sica", 55.0],
    "termica20": ["Termica 20A Sica", 12.0]
}

blue = obtener_blue()
fecha = os.popen('date +%Y-%m-%d').read().strip()

output = f"---\nfecha: {fecha}\ndolar_ref: {blue}\n---\n\n"
output += "### 🛒 Lista de Precios de Referencia\n\n"

for id, data in materiales.items():
    nombre = data[0]
    usd = data[1]
    precio_ars = int(usd * blue)
    # Aquí creamos el 'ID' que la plantilla reconoce
    output += f"{nombre}: ${precio_ars} ^{id}\n"

with open("08_PRECIOS/Precios_Actualizados.md", "w", encoding="utf-8") as f:
    f.write(output)

print(f"✅ Precios actualizados y vinculados a plantilla. Dólar: ${blue}")

