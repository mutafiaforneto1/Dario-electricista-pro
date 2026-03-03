```dataview
TABLE cliente as "Cliente", precio_total as "Presupuesto", estado as "Estado"
FROM "01_TRABAJOS"
WHERE estado != "Finalizado"
SORT fecha desc

```
