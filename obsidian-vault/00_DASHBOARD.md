---
aliases: [inicio, home, dashboard]
---

# ⚡ Centro de Comando — Dario Electricista

> Actualizado automáticamente por Dataview

---

## 🔧 TRABAJOS ACTIVOS

```dataview
TABLE cliente, mano_de_obra, fecha
FROM "01_TRABAJOS"
WHERE estado = "activo" OR estado = "en curso"
SORT fecha DESC
```

---

## 💸 DINERO EN LA CALLE

```dataview
TABLE cliente, mano_de_obra, fecha
FROM "01_TRABAJOS"
WHERE pagado = false OR pagado = "no" OR pagado = "pendiente"
SORT fecha DESC
```

---

## 📅 SEMANA ACTUAL

```dataview
TABLE file.day, cliente, estado
FROM "01_TRABAJOS"
WHERE file.day >= date(today) - dur(7 days)
SORT file.day DESC
```

---

## 📓 DIARIO RECIENTE

```dataview
LIST
FROM "05_DIARIO"
SORT file.name DESC
LIMIT 5
```

---

## 🎯 OBJETIVOS ACTIVOS

```dataview
LIST
FROM "06_OBJETIVOS"
WHERE estado != "completado"
SORT file.mtime DESC
```

---

## 📊 RESUMEN DEL MES

```dataview
TABLE sum(rows.mano_de_obra) AS "Total Facturado"
FROM "01_TRABAJOS"
WHERE date(fecha).month = date(today).month
  AND date(fecha).year = date(today).year
GROUP BY true
```

---

## ⚡ ACCESOS RÁPIDOS

| Acción | Nota |
|---|---|
| ➕ Nuevo trabajo | [[Nueva Plantilla Trabajo]] |
| 👤 Nuevo cliente | [[Ficha cliente]] |
| 💰 Registrar cobro | [[Control de cobros]] |
| 📋 Historial | [[Historial de Trabajos]] |
| 🔌 Info técnica | [[07_INFO_TECNICA/Canal de comunicacion electrica]] |
| 💲 Precios | [[08_PRECIOS/Precios_Actualizados]] |
