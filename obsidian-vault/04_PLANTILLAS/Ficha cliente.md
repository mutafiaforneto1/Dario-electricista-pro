---
tipo: cliente
telefono: 
direccion:
zona:
categoria: Particular
pagador: bueno
---

# Cliente: {{title}}

---

## Contacto
- **Telefono:** 
- **Direccion:** 
- **Google Maps:** 

---

## Detalles Tecnicos
- **Tipo de conexion:** Monofasica / Trifasica
- **Tablero principal:** 
- **Estado instalacion:** Nueva / Vieja / A reformar
- **Notas tecnicas:** 

---

## Historial de Trabajos

\`\`\`dataview
TABLE fecha, estado, mano_de_obra AS "Monto", pagado
FROM "01_TRABAJOS"
WHERE cliente = this.file.link
SORT fecha DESC
\`\`\`

---

## Resumen Economico

\`\`\`dataview
TABLE sum(rows.mano_de_obra) AS "Total facturado"
FROM "01_TRABAJOS"
WHERE cliente = this.file.link
GROUP BY true
\`\`\`

---

## Notas

