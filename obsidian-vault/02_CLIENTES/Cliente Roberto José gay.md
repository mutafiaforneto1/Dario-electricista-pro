---
tipo: cliente
teléfono:
dirección_fija: 17 e/ 522 y 523 n945
zona: Centro
categoría: 🟢 Particular
---
## 🗂️    [[Tablero General]]   

# 👤 Datos del Cliente: Cliente Roberto José gay

### 📞 Contacto y Ubicación
- **Teléfono:** - **Dirección:** - **Google Maps:** [Link aquí]

### ⚡ Detalles Técnicos del Domicilio
- **Tipo de Conexión:** (Monofásica)
- **Ubicación del Tablero Principal:** - **Estado de la Instalación:** (A reformar)
- **Notas técnicas:** (Ej: "Tiene térmica general de 25A", "Falta puesta a tierra")

---
### 🛠️ Historial de Trabajos
```dataview
TABLE fecha, estado, mano_de_obra
FROM "01_TRABAJOS"
WHERE cliente = this.file.link
SORT fecha DESC
