---
tipo: cliente
teléfono:
dirección_fija: "125 Norte  #2113 entre 18 y 18 Este"
zona: 
categoría: 🟢 Particular
---
## 🗂️    [[Tablero General]]   

# 👤 Datos del Cliente: Cliente María Rosa

### 📞 Contacto y Ubicación
- **Teléfono:** +54 9 221 418-0139 - **Dirección:** - 125 Norte  #2113 entre 18 y 18 Este**Google Maps:** [Link aquí]

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
