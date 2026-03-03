---
Tension_V: 220
Corriente_A: 5
Longitud_m: 30
Seccion_mm2: 2.5
Material_K: 56
---


```dataview
TABLE
    round(Perdida_V, 2) as "Caída (V)",
    round((Perdida_V / Tension_V) * 100, 2) + "%" as "Pérdida (%)",
    choice(Perdida_V / Tension_V <= 0.03, "✅ Óptimo", "⚠️ Revisar Sección") as "Estado"
FLATTEN 
    ((2 * Longitud_m * Corriente_A) / (Material_K * Seccion_mm2)) as Perdida_V
WHERE file.name = this.file.name
```
