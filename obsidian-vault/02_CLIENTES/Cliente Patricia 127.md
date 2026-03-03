---
tipo: cliente
teléfono: +54 9 221 436-4960
dirección_fija: 127 e/77 y 78
zona:
categoría: 🟢 Particular
---

# 👤 Datos del Cliente: Cliente Patricia 127

### 📞 Contacto y Ubicación
- **Teléfono:** +54 9 221 436-4960- **Dirección:** - **Google Maps:** [Link aquí]

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
