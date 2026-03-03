import requests
from bs4 import BeautifulSoup
import os

# CONFIGURACIÓN: Links directos a productos populares
productos = {
    "Cable 2.5mm (100m)": "https://www.mercadolibre.com.ar/p/MLA15194451",
    "Cable 1.5mm (100m)": "https://www.mercadolibre.com.ar/p/MLA15194450",
    "Disyuntor 25A Sica": "https://www.mercadolibre.com.ar/p/MLA19515234",
    "Termica 20A Sica": "https://www.mercadolibre.com.ar/p/MLA19515228"
}

def obtener_precio(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept-Language": "es-AR,es;q=0.9"
        }
        r = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # ML suele usar esta clase para la parte entera del precio
        precio_entero = soup.find("span", {"class": "andes-money-amount__fraction"})
        
        if precio_entero:
            return precio_entero.text.replace(".", "")
        return "Revisar Link"
    except Exception as e:
        return "Error Red"

# Crear contenido
fecha_hoy = os.popen('date +%Y-%m-%d').read().strip()
contenido = f"---\nultima_actualizacion: {fecha_hoy}\n---\n\n"
contenido += "### 🛒 Precios Reales de Mercado Libre\n\n"
contenido += "| Material | Precio Actual (ARS) |\n| :--- | :--- |\n"

print(f"Actualizando precios al {fecha_hoy}...")

for nombre, url in productos.items():
    precio = obtener_precio(url)
    # Usamos :: para que Dataview lo reconozca como propiedad
    contenido += f"| {nombre} | precio_unitario:: {precio} |\n"
    print(f"✅ {nombre}: ${precio}")

with open("Precios_MercadoLibre.md", "w", encoding="utf-8") as f:
    f.write(contenido)

print("\n¡Listo! Nota actualizada en Obsidian.")

