```dataview
TABLE WITHOUT ID
  choice(date(fecha), dateformat(date(fecha), "yyyy-MM"), "Formato Incorrecto") as "Mes",
  sum(rows.mano_de_obra) as "Total Cobrado"
```
