---
tipo: cliente
teléfono:
dirección_fija: 82 e/122 y 123
zona:
categoría: 🟢 Particular
---

# 👤 Datos del Cliente: Cliente mica amiga mica

### 📞 Contacto y Ubicación
- **Teléfono:** - **Dirección:** - **Google Maps:** [Link aquí]

### ⚡ Detalles Técnicos del Domicilio
- **Tipo de Conexión:** (Monofásica que viene desde la madre)
- **Ubicación del Tablero Principal:** - **Estado de la Instalación:** (A reformar)
- **Notas técnicas:** (Ej: "Tiene térmica general de 25A", "Falta puesta a tierra")

---
### 🛠️ Historial de Trabajos
```dataview
TABLE fecha, estado, mano_de_obra
FROM "01_TRABAJOS"
WHERE cliente = this.file.link
SORT fecha DESC
