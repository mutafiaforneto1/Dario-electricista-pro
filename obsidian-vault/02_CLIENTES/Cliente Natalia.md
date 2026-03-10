---
tipo: cliente
teléfono:
dirección_fija: 67 y 116
zona: Periferia
categoría: 🟢 Particular
---
## 🗂️    [[Tablero General]]   

# 👤 Datos del Cliente: Cliente Natalia

### 📞 Contacto y Ubicación
- **Teléfono:** - **Dirección:** - **Google Maps:** [Link aquí]

### ⚡ Detalles Técnicos del Domicilio
- **Tipo de Conexión:** (Monofásica)
- **Ubicación del Tablero Principal:** cocina
- **Estado de la Instalación:** (Nueva / Vieja)
- **Notas técnicas:** (Ej: "Tiene térmica general de 25A", "Falta puesta a tierra")

---
### 🛠️ Historial de Trabajos
```dataview
TABLE fecha, estado, mano_de_obra
FROM "01_TRABAJOS"
WHERE cliente = this.file.link
SORT fecha DESC
