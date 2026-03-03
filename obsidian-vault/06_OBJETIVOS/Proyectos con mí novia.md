---
tipo: objetivo
anio: 2026
estado: en curso
vision: "Construir una vida y futuro sólido juntos"
progreso: 0
deadline: 2026-12-31
---
```dataview
TABLE WITHOUT ID
  "<progress value='" + progreso + "' max='100'></progress> " + progreso + "%" AS "progreso de metas"
WHERE file.name = this.file.name

```
# ❤️ Proyectos con mi Novia

**Cumplimiento de metas compartidas:** 
```dataview
TABLE WITHOUT ID
  "<progress value='" + progreso + "' max='100'></progress> " + progreso + "%" AS "cumplimiento"
WHERE file.name = this.file.name

```

> [!heart] Nuestro Norte
> Planificar momentos de calidad y proyectos que nos ilusionen a ambos, equilibrando mi trabajo de electricista y el tiempo con mis hijos.

---

### 📝 Ideas y Proyectos en Mente
- [ ] **Viaje/Escapada:** (Ej: Un fin de semana de descanso).
- [ ] **Ahorro Conjunto:** Para un gasto grande o inversión.
- [ ] **Mejoras:** Algo para compartir en nuestros espacios.
- [ ] **Citas Planificadas:** Asegurar una salida especial al menos una vez al mes.
- [ ] **planificar espacio:** para  dormir juntos
- [ ] 

---

### 📅 Próxima Charla de Planificación
*Sugerencia: Aprovechar los domingos por la tarde para ver qué queremos hacer el mes siguiente.*

---

### 💬 Notas de Conversaciones
*Anotá aquí cosas que ella mencione que le gustaría hacer o lugares a los que quiera ir.*
- 

---
### ⏳ Días para cerrar el año de proyectos: 
`$= Math.ceil((new Date(dv.current().deadline) - new Date()) / (1000 * 60 * 60 * 24))` días.
