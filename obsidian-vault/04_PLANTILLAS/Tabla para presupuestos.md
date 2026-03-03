```dataview
TABLE precio_unitario as "Precio Material", precio_mo as "Mano de Obra"
FROM "08_PRECIOS"
WHERE precio_unitario OR precio_mo
```