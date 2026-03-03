---
tipo: cliente
teléfono:
dirección_fija: 40 168 y169 número 4559 Berisso
zona:
categoría: 🟢 Particular
---
## 🗂️    [[Tablero General]]   

# 👤 Datos del Cliente: Cliente Rosa de la 8

### 📞 Contacto y Ubicación
- **Teléfono:** - **Dirección:** - **Google Maps:** [https://maps.app.goo.gl/FANMLLF4Ktydyx57A]

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
