---
tipo: cliente
teléfono:
dirección_fija: 49 e/131 y 132
zona: Centro
categoría: 🟢 Particular
direccion: Calle 77 y 25, La Plata
lat: -34.9354757
lon: -57.9242831
link_maps: https://www.google.com/maps?q=-34.9354757,-57.9242831
---

# 👤 Datos del Cliente: Cliente Déborah

### 📞 Contacto y Ubicación
- **Teléfono:** - **Dirección:** - **Google Maps:** [Link aquí]

### ⚡ Detalles Técnicos del Domicilio
- **Tipo de Conexión:** (Monofásica / Trifásica)
- **Ubicación del Tablero Principal:** - **Estado de la Instalación:** (Nueva / Vieja / A reformar)
- **Notas técnicas:** (Ej: "Tiene térmica general de 25A", "Falta puesta a tierra")

---
### 🛠️ Historial de Trabajos
```dataview
TABLE fecha, estado, mano_de_obra
FROM "01_TRABAJOS"
WHERE cliente = this.file.link
SORT fecha DESC
