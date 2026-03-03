---
color: "linear-gradient(45deg, #23d4fd 0%, #3a98f0 50%, #b721ff 100%)"
---
# 🛠️ GESTIÓN DE TRABAJOS

> [!multi-column]
>
> > [!todo] **TRABAJOS ACTIVOS**
> > `button-nuevo-cliente` (Luego configuramos este botón)
>
> > [!info] **PRECIOS RÁPIDOS**
> > [[08_PRECIOS/Precios_Actualizados|Ver Lista de Precios]]

---

### 📋 Listado de Clientes y Estados
```dataview
TABLE estado as "Estado", prioridad as "Prioridad", fecha as "Fecha Inicio"
FROM "01_TRABAJOS"
WHERE tipo = "trabajo"
SORT fecha DESC
