---
aliases: [panel, control]
---

# 🎛 Panel de Control
## Dario Electricista — La Plata

---

## 📊 Indicadores

| | Activos | A Cobrar | Este Mes | Esta Semana |
|---|---|---|---|---|
| **Cantidad** | | | | |
| **Monto $** | | | | |

---

## 🛠 Trabajos Activos

```dataview
TABLE cliente, mano_de_obra AS "$", fecha
FROM "01_TRABAJOS"
WHERE estado = "En curso" OR estado = "pendiente"
SORT fecha DESC
```

---

## 💸 Dinero en la Calle

```dataview
TABLE cliente, mano_de_obra AS "$", fecha
FROM "01_TRABAJOS"
WHERE pagado = false AND estado = "terminado"
SORT fecha DESC
```

---

## 📅 Últimos Trabajos Terminados

```dataview
TABLE cliente, mano_de_obra AS "$", pagado
FROM "01_TRABAJOS"
WHERE estado = "terminado"
SORT file.mtime DESC
LIMIT 8
```

---

## 🔌 Compras Pendientes

- [ ] 
- [ ] 
- [ ] 
- [ ] 

---

## ⚡ Accesos Rápidos

| Sección | Link |
|---|---|
| Dashboard | [[00_DASHBOARD]] |
| Agenda | [[Agenda Semanal Kanban]] |
| Kanban | [[Tablero Kanban Trabajos]] |
| Balance | [[03_ADMIN/Balance mensual]] |
| Cobros | [[03_ADMIN/Control de cobros]] |
| Precios | [[08_PRECIOS/Precios_Actualizados]] |
| Gráfico | [[03_ADMIN/Grafico de Ingresos]] |
