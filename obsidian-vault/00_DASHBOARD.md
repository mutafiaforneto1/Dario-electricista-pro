---
aliases: [inicio, home, dashboard]
---

# ⚡ Centro de Comando — Dario Electricista

---

## 🔧 TRABAJOS ACTIVOS

\`\`\`dataview
TABLE cliente, mano_de_obra AS "Mano de obra", fecha
FROM "01_TRABAJOS"
WHERE estado = "En curso" OR estado = "pendiente"
SORT fecha DESC
\`\`\`

---

## 💸 DINERO EN LA CALLE

\`\`\`dataview
TABLE cliente, mano_de_obra AS "Monto", fecha
FROM "01_TRABAJOS"
WHERE pagado = false AND estado = "terminado"
SORT fecha ASC
\`\`\`

---

## 📋 PRESUPUESTOS PENDIENTES

\`\`\`dataview
TABLE cliente, mano_de_obra AS "Monto", fecha
FROM "01_TRABAJOS"
WHERE estado = "presupuesto"
SORT fecha DESC
\`\`\`

---

## 📅 TRABAJOS DEL MES

\`\`\`dataview
TABLE cliente, estado, mano_de_obra AS "Monto", pagado
FROM "01_TRABAJOS"
WHERE date(fecha).month = date(today).month
  AND date(fecha).year = date(today).year
SORT fecha DESC
\`\`\`

---

## 📓 DIARIO RECIENTE

\`\`\`dataview
LIST
FROM "05_DIARIO"
SORT file.name DESC
LIMIT 5
\`\`\`

---

## 📊 RESUMEN DEL MES

\`\`\`dataview
TABLE sum(rows.mano_de_obra) AS "Total Facturado"
FROM "01_TRABAJOS"
WHERE date(fecha).month = date(today).month
  AND date(fecha).year = date(today).year
GROUP BY true
\`\`\`

---

## ⚡ ACCESOS RÁPIDOS

| Acción | Nota |
|---|---|
| ➕ Nuevo trabajo | [[Nueva Plantilla Trabajo]] |
| 👤 Nuevo cliente | [[Ficha cliente]] |
| 💲 Precios | [[08_PRECIOS/Precios_Actualizados]] |
| 🔌 Info técnica | [[07_INFO_TECNICA/Canal de comunicacion electrica]] |
