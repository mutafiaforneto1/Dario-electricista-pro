---
aliases: [estadisticas, stats, ingresos]
---

# 📊 Estadísticas Mensuales
> Actualizado automáticamente por Dataview

---

## 💰 Ingresos por Mes

```dataview
TABLE WITHOUT ID
  key AS "Mes",
  sum(rows.mano_de_obra) AS "Total $",
  length(rows.file.name) AS "Trabajos"
FROM "01_TRABAJOS"
WHERE mano_de_obra > 0
GROUP BY dateformat(date(fecha), "yyyy-MM")
SORT key DESC
```

---

## 📈 Trabajos Este Mes

```dataview
TABLE cliente, mano_de_obra AS "$", estado, pagado
FROM "01_TRABAJOS"
WHERE date(fecha).year = date(today).year AND date(fecha).month = date(today).month
SORT fecha DESC
```

---

## 📉 Mes Anterior

```dataview
TABLE cliente, mano_de_obra AS "$", estado, pagado
FROM "01_TRABAJOS"
WHERE date(fecha).year = (date(today) - dur(1 month)).year AND date(fecha).month = (date(today) - dur(1 month)).month
SORT fecha DESC
```

---

## 💸 Pendiente de Cobro

```dataview
TABLE cliente, mano_de_obra AS "$", fecha AS "Fecha"
FROM "01_TRABAJOS"
WHERE pagado = false AND estado = "terminado"
SORT fecha ASC
```

---

## 🏆 Top Clientes

```dataview
TABLE WITHOUT ID
  cliente AS "Cliente",
  sum(rows.mano_de_obra) AS "Total $",
  length(rows.file.name) AS "Trabajos"
FROM "01_TRABAJOS"
WHERE mano_de_obra > 0
GROUP BY cliente
SORT sum(rows.mano_de_obra) DESC
LIMIT 10
```

---

## 📅 Trabajos por Estado

```dataview
TABLE WITHOUT ID
  estado AS "Estado",
  length(rows.file.name) AS "Cantidad",
  sum(rows.mano_de_obra) AS "Total $"
FROM "01_TRABAJOS"
GROUP BY estado
SORT length(rows.file.name) DESC
```
