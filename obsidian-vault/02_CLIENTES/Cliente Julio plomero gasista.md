---
tipo: cliente
teléfono: +54 9 221 585-3069
dirección_fija: 77 e/ 126 y 127
zona:
categoría: 🟢 Particular
---
## 🗂️    [[Tablero General]]   

# 👤 Datos del Cliente: Sin título

### 📞 Contacto y Ubicación
- **Teléfono:** - **Dirección:** - **Google Maps:** [Link aquí]

### ⚡ Detalles Técnicos del Domicilio
- **Tipo de Conexión:** (Monofásica)
- **Ubicación del Tablero Principal:** habitación - **Estado de la Instalación:** (Vieja)
- **Notas técnicas:** casa en fondo de terreno, alimentación de la casa muy larga. Hay que hacer cambio de cable de alimentación por preensamblado.

---
### 🛠️ Historial de Trabajos
```dataview
TABLE fecha, estado, mano_de_obra
FROM "01_TRABAJOS"
WHERE cliente = this.file.link
SORT fecha DESC
