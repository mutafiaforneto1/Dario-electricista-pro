---
tipo: objetivo
anio: 2026
estado: en curso
vision: "Tranquilidad financiera a largo plazo"
progreso: 0
meta_anual: 0
deadline: 2045-12-31
---
```dataview
TABLE WITHOUT ID
  "<progress value='" + progreso + "' max='100'></progress> " + progreso + "%" AS "Avance del poyecto"
WHERE file.name = this.file.name

```
# 🏦 Fondo de Jubilación y Futuro

```dataview
TABLE WITHOUT ID
  "<progress value='" + progreso + "' max='100'></progress> " + progreso + "%" AS "meta anual"
WHERE file.name = this.file.name

```

> [!info] Estrategia para Electricista Independiente
> Separar el 10% de la mano de obra de cada trabajo cobrado de lunes a viernes.

---
### 📈 Registro de Aportes 2026
| Mes | Monto ($) | Estado |
| --- | --- | --- |
| Enero | | |
| Febrero | | |
| Marzo | | |

---
### 📋 Tareas de Seguridad Financiera
- [ ] Investigar cuenta de inversión/billetera virtual que genere intereses.
- [ ] Definir monto fijo de "sueldo" para gastos diarios y separar el resto.
- [ ] Consultar con un asesor sobre fondos de retiro.

---
### 📅 Tiempo para el retiro: 
`$= Math.ceil((new Date(dv.current().deadline) - new Date()) / (1000 * 60 * 60 * 24 * 365))` años restantes.
