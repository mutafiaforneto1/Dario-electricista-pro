---
tipo: cliente
teléfono: +54 9 221 595-2923
dirección_fija: Dig 80 e/2 y 3 . Casi 2
zona:
categoría: 🟢 Particular
---
## 🗂️    [[Tablero General]]   

# 👤 Datos del Cliente: {{title}}

### 📞 Contacto y Ubicación
- **Teléfono:** - **Dirección:** - **Google Maps:** [Link aquí]

### ⚡ Detalles Técnicos del Domicilio
- **Tipo de Conexión:** (Monofásica / Trifásica)
- **Ubicación del Tablero Principal:** - **Estado de la Instalación:** (Nueva / Vieja / A reformar)
- **Notas técnicas:** dos tableros. Veterinaria dig 80  y tablero de calle 45

---
### 🛠️ Historial de Trabajos
```dataview
TABLE fecha, estado, mano_de_obra
FROM "01_TRABAJOS"
WHERE cliente = this.file.link
SORT fecha DESC
