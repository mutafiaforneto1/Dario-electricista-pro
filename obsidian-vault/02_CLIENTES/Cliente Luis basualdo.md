---
tipo: cliente
teléfono:
dirección_fija: 122bis e/77 y 78
zona:
categoría: 🟢 Particular
---

# 👤 Datos del Cliente: Cliente Luis basualdo

### 📞 Contacto y Ubicación
- **Teléfono:**+54 9 221 674-3210 - **Dirección:** - **Google Maps:** [Link aquí]

### ⚡ Detalles Técnicos del Domicilio
- **Tipo de Conexión:** (Monofásica)
- **Ubicación del Tablero Principal:** - **Estado de la Instalación:** (Nueva / Vieja / A reformar)
- **Notas técnicas:** (Ej: "Tiene térmica general de 25A", "Falta puesta a tierra")

---
### 🛠️ Historial de Trabajos
```dataview
TABLE fecha, estado, mano_de_obra
FROM "01_TRABAJOS"
WHERE cliente = this.file.link
SORT fecha DESC
