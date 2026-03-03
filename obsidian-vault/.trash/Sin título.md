---
tipo: trabajo
cliente: "[[Cliente - ]]"
telefono: 54911xxxxxxxx
prioridad: 🔵 Media
fecha: 2026-02-15 18:10
estado: 🛠️ En curso
mano_de_obra: 0
costo_materiales: 0
pagado: false
---

# 📊 Control de Obra: <% tp.file.title %>

> [!money] Finanzas de la Obra
> **Mano de Obra:** `$= dv.current().mano_de_obra`
> **Materiales estimados:** `$= dv.current().costo_materiales`
> **TOTAL PRESUPUESTO:** `$= dv.current().mano_de_obra + dv.current().costo_materiales`
> **Estado:** `$= dv.current().pagado ? "✅ FACTURADO" : "❌ PENDIENTE DE COBRO"`

---

### 📱 Acciones Rápidas (WhatsApp)
> [!contact] Comunicación con el Cliente
> [📩 Enviar Presupuesto](https://wa.me/<% tp.frontmatter.telefono %>?text=Hola%20te%20paso%20el%20presupuesto%20actualizado:%20$%20`$= dv.current().mano_de_obra + dv.current().costo_materiales`)
> 
> [💰 Recordatorio de Pago](https://wa.me/<% tp.frontmatter.telefono %>?text=Hola%20te%20escribo%20para%20pasarte%20el%20total%20pendiente:%20$%20`$= dv.current().mano_de_obra + dv.current().costo_materiales`)

---

# 📝 Detalles del Servicio
- **Descripción:** - **Urgencia:** # 🛠️ Tareas
- [ ] Relevamiento
- [ ] Compra de materiales
- [ ] Ejecución
- [ ] Prueba de seguridad y entrega

# 📦 Precios de Referencia (Termux)
| Material | Precio Ref. (ARS) |
| :--- | :--- |
| Cable 2.5mm | ![[Precios_Actualizados#^cable25]] |
| Cable 1.5mm | ![[Precios_Actualizados#^cable15]] |
| Disyuntor 25A | ![[Precios_Actualizados#^disyuntor25]] |
| Térmica 20A | ![[Precios_Actualizados#^termica20]] |

# 📸 Fotos y Notas Técnicas
- 

---
[[03_ADMIN/Balance Mensual|⬅️ Volver al Balance]] | [[00_ÍNDICE_MAESTRO|🏠 Inicio]]
