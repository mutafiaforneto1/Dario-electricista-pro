```dataview
TABLE cliente as "Cliente", mano_de_obra as "Monto", fecha as "Fecha"
FROM "01_TRABAJOS"
WHERE pagado = false AND estado = "terminado"
SORT fecha ASC

```