import urllib.request
import json
import os
from datetime import datetime

# Configuración de Materiales (Precios base en USD)
MATERIALES = {
    "cable25":       ("Cable 2.5mm (100m)",      45.5),
    "cable15":       ("Cable 1.5mm (100m)",       32.0),
    "disyuntor25":   ("Disyuntor 25A Sica",       55.0),
    "termica20":     ("Térmica 20A Sica",          12.0),
    "toma20":        ("Toma 20A módulo",           8.5),
}

def get_dolar_blue():
    try:
        with urllib.request.urlopen("https://dolarapi.com/v1/dolares/blue", timeout=10) as r:
            data = json.loads(r.read())
            return float(data['venta'])
    except Exception as e:
        return None

def main():
    blue = get_dolar_blue()
    if not blue:
        print("❌ Sin conexión o error de API.")
        return

    output_path = "08_PRECIOS/Precios_Actualizados.md"
    fecha = datetime.now().strftime("%Y-%m-%d")
    
    lines = [
        f"---",
        f"fecha: {fecha}",
        f"dolar_ref: {blue}",
        f"---\n",
        f"### 🛒 Precios de Referencia (Dólar Blue: ${blue:,.0f})\n",
        f"| Material | USD | ARS (aprox) |",
        f"| :--- | ---: | ---: |"
    ]
    
    for id_mat, (nombre, usd) in MATERIALES.items():
        ars = int(usd * blue)
        lines.append(f"| {nombre} | u$s{usd} | ${ars:,} |")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"✅ Precios actualizados con Dólar Blue a ${blue:,.0f}")

if __name__ == "__main__":
    main()
