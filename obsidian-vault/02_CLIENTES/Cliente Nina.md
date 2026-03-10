---
tipo: cliente
teléfono:
dirección_fija: 122bis e/77 y 78
zona: Berisso
categoría: 🟢 Particular
---
## 🗂️    [[Tablero General]]   

# 👤 Datos del Cliente: Cliente Nina

### 📞 Contacto y Ubicación
- **Teléfono:** - **Dirección:** - **Google Maps:** [Link aquí]

### ⚡ Detalles Técnicos del Domicilio
- **Tipo de Conexión:** (Monofásica)
- **Ubicación del Tablero Principal:** pieza delantera, al lado del medidor.
- **Estado de la Instalación:** (Vieja / A reformar)
- **Notas técnicas:** (Ej: "Tiene térmica general de 25A", "Falta puesta a tierra")

---
### 🛠️ Historial de Trabajos
```dataview
TABLE fecha, estado, mano_de_obra
FROM "01_TRABAJOS"
WHERE cliente = this.file.link
SORT fecha DESC
