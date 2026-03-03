```dataview
TABLE
vision as "Visión",
progreso as "Progreso %",
deadline as "Fecha Límite",
choice(progreso >= 100, "✅", "🚀") as "Estado"
FROM "Objetivos"
WHERE tipo = "objetivo"
SORT deadline ASC
```
