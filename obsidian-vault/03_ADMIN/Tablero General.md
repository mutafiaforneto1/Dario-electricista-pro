---
sticker: emoji//1f4ca
---
```dataview
TABLE dirección as Dirección, prioridad as Prioridad, estado as Estado
FROM "01_TRABAJOS"
WHERE estado != "✅ Terminado"
SORT prioridad ASC
```



💸 Dinero en la calle (Terminado sin cobrar):
```dataview
TABLE cliente as Cliente, mano_de_obra as "Monto", fecha as "Finalizado"
FROM "01_TRABAJOS"
WHERE pagado = false AND (estado = "🛠️ terminado" OR estado = "🛠️ Terminado")


```




📊 REGISTRO DE DINERO
```dataview
TABLE cliente as Cliente, mano_de_obra as "Monto", fecha as "Cobrado"
FROM "01_TRABAJOS"
WHERE pagado = true AND (estado = "🛠️ terminado" OR estado = "🛠️ Terminado")


```

```dataview
LIST "Total: " + sum(rows.mano_de_obra)
FROM "01_TRABAJOS"
WHERE pagado = true
GROUP BY tipo

```
# 📅 "Próximos Compromisos" 

```dataview
TABLE dirección as "Dirección", prioridad as "Prioridad"
FROM "01_TRABAJOS"
WHERE estado = "🛠️ pendiente" OR estado = "🛠️ En curso"
SORT fecha ASC

```



# 📅 Planificación Semanal

## 🔥 Trabajos en Curso
```dataview
LIST FROM "01_TRABAJOS"
WHERE estado = "🛠️ En curso"
```
```dataviewjs
let pages = dv.pages('"01_TRABAJOS"').where(p => p.mano_de_obra);

if (pages.length > 0) {
    let totalCualquierFecha = pages.mano_de_obra.array().reduce((a, b) => a + b, 0);
    dv.paragraph("✅ Se encontraron " + pages.length + " trabajos con monto.");
    dv.header(3, "Total Histórico: $" + totalCualquierFecha.toLocaleString());
} else {
    dv.paragraph("❌ No encontré ninguna nota en '01_TRABAJOS' que tenga el campo 'mano_de_obra'.");
}
```


# 💰 Panel de Control de Ingresos

```dataviewjs
// 1. Forzamos el mes y año que queremos buscar (Febrero 2026)
let mesBuscado = "02"; 
let añoBuscado = "2026";
let filtroTexto = añoBuscado + "-" + mesBuscado; // Busca "2026-02"

// 2. Traemos todos los trabajos que tengan monto y estén pagados
let pagados = dv.pages('"01_TRABAJOS"')
    .where(p => p.mano_de_obra && (p.pagado === true || p.pagado === "true"));

// 3. Filtramos por fecha usando una técnica de texto (más robusta)
let deEsteMes = pagados.filter(p => {
    if (!p.fecha) return false;
    // Convertimos la fecha a texto por si no es un objeto Date
    let fechaTxt = String(p.fecha); 
    return fechaTxt.includes(filtroTexto);
});

// 4. Sumamos
let total = deEsteMes.mano_de_obra.array().reduce((a, b) => a + b, 0);

// 5. Resultado
dv.header(3, "💰 Total Cobrado en Febrero: $" + total.toLocaleString());

// Ayuda visual si sigue dando 0
if (total === 0) {
    dv.paragraph("---");
    dv.paragraph("⚠️ **Dato encontrado:** " + pagados.length + " trabajos pagados en total.");
    dv.paragraph("🔍 **Ejemplo de fecha detectada:** " + (pagados.length > 0 ? pagados[0].fecha : "Ninguna"));
}
```

```dataview
LIST FROM "01_TRABAJOS"
WHERE contains(estado, "En curso") OR contains(estado, "🛠️")
```


## 🔥 Trabajos en Curso
```dataview
LIST FROM "01_TRABAJOS"
WHERE contains(estado, "En curso") OR contains(estado, "🛠️")
WHERE pagado = false OR pagado = null
```
