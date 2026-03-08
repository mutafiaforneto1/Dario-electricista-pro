---
tipo: cliente
dirección: Jorgelina122 e/77 y 78
teléfono: +54 9 221 608-4940
dirección_fija: Martin berisso
teléfono 2: +54 9 221 600-6840
zona:
categoría: 🟢 Particular
---
## 🗂️    [[Tablero General]]   

# 👤 Datos del Cliente: {{title}}

### 📞 Contacto y Ubicación
- **Teléfono:** - **Dirección:** - **Google Maps:** https://maps.app.goo.gl/EiACxMw4An6FJ2Lt8

### ⚡ Detalles Técnicos del Domicilio
- **Tipo de Conexión:** (Monofásica)
- **Ubicación del Tablero Principal:** - **Estado de la Instalación:** (Nueva / Vieja / A reformar)
- **Notas técnicas:** se queda sin luz el quincho, posible problema de fuga por el cable subterráneo.
- 

---
### 🛠️ Historial de Trabajos
```dataview
TABLE fecha, estado, mano_de_obra
FROM "01_TRABAJOS"
WHERE cliente = this.file.link
SORT fecha DESC
