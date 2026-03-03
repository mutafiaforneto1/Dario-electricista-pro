```dataview
TABLE 
    cliente as "Cliente", 
    default(mano_de_obra, 0) + default(costo_materiales, 0) as "Presupuesto",
    choice(pagado, "✅ Cobrado", "❌ Pendiente") as "Estado"
FROM "01_TRABAJOS"
WHERE estado != "Finalizado"
SORT fecha desc

```

```dataview
TABLE WITHOUT ID
    "TOTAL EN LA CALLE" as "Concepto",
    "$" + sum(rows.total) as "Monto Total"
FROM "01_TRABAJOS"
WHERE estado != "Finalizado" AND pagado = false
FLATTEN (default(mano_de_obra, 0) + default(costo_materiales, 0)) as total
GROUP BY true

```