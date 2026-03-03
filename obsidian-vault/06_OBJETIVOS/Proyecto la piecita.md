---
tipo: objetivo
anio: 2026
estado: en curso
vision: Mejorar mi hogar y tener un espacio funcional
progreso: 0
deadline: 2026-06-30
---
```dataview
TABLE WITHOUT ID
  "<progress value='" + progreso + "' max='100'></progress> " + progreso + "%" AS "Avance de la Obra"
WHERE file.name = this.file.name

```
# 🏗️ Objetivo: Terminar la Piecita


> [!tip] Plan de Electricista
> Aprovechar los lunes, miércoles y viernes antes de que lleguen los chicos (13:30) para tareas de compra de materiales o planificación, y los sábados que no estoy con ellos para la mano de obra pesada.

---

### 📝 Lista de Tareas (Proyectos)

- [ ] **Fase 1: Limpieza y Nivelación**
	- [ ] Vaciar la habitación.
	- [ ] Revisar humedad en paredes/piso.
- [ ] **Fase 2: Instalación Eléctrica (¡Mi especialidad!)**
	- [ ] Diseñar plano de bocas y tomas.
	- [ ] Cableado y térmicas independientes.
- [ ] **Fase 3: Albañilería y Terminaciones**
	- [ ] Revoques o placas de yeso.
	- [ ] Pintura y piso.
- [ ] **Fase 4: Mobiliario**
	- [ ] Armado de estantes o escritorio.

---

### 💰 Presupuesto Estimado
| Ítem | Costo Est. | Comprado |
| --- | --- | --- |
| Cables/Cajas | $ | [ ] |
| Pintura | $ | [ ] |
| Placas/Cemento| $ | [ ] |

---
### 📅 Días restantes para el objetivo: 
`$= Math.ceil((new Date(dv.current().deadline) - new Date()) / (1000 * 60 * 60 * 24))` días.
