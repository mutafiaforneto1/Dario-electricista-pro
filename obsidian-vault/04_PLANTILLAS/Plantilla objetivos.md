---
tipo: objetivo
anio: 2026
estado: en curso
vision: 
progreso: 0
deadline: 2026-12-31
---

# 🎯 Objetivo: {{title}}

**Progreso Actual:** INPUT[slider(min(0), max(100), step(5)):progreso] 

> [!info] Visión Relacionada
> `VIEW[{vision}]`

---
### 📅 Días restantes: 
`$= Math.ceil((new Date(dv.current().deadline) - new Date()) / (1000 * 60 * 60 * 24))` días.
