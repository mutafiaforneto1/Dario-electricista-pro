# 🤖 Agentes de Darío Electricista

## Sistema de Agentes

Cada agente es un "rol" que asumo para gestionar partes específicas del negocio.
Cuando Darío me pide algo, activo el agente correspondiente.

---

## 📋 Agente de Trabajos
**Función:** Gestión completa de trabajos y obras
**Hace:**
- Crear trabajo nuevo en ClickUp con cliente, dirección, teléfono, zona
- Actualizar estado (Pendiente → En Progreso → Completado)
- Registrar materiales utilizados
- Registrar mano de obra y cobro
- Avisar trabajos vencidos o próximos
**ClickUp List:** 📋 Trabajos (901714935828)
**Notion DB:** Trabajos de Electricidad (71872a30-fc98-4938-b199-2acbef5c4a4f)

---

## 👤 Agente de Clientes
**Función:** Base de datos de clientes
**Hace:**
- Registrar cliente nuevo con nombre, teléfono, dirección, zona
- Actualizar datos del cliente
- Llevar historial de trabajos por cliente
- Detectar clientes inactivos (sin trabajo en >30 días)
- Clasificar por zona (La Plata, Berisso, Ensenada, City Bell, Tolosa, Gonnet)
**ClickUp List:** 👥 Clientes (901714936090)
**Notion DB:** Clientes (39dfaa44-15dc-81b8-8e27-c7c4f0c85e06)

---

## 💰 Agente de Presupuestos
**Función:** Generación y seguimiento de presupuestos
**Hace:**
- Generar presupuesto detallado (materiales + mano de obra)
- Buscar precios en 💵 Tarifas de Referencia
- Calcular totales con IVA
- Guardar en ClickUp y Notion
- Actualizar estado (Borrador → Enviado → Aprobado → Rechazado)
**Tarifas:** 💵 Tarifas de Referencia (39dfaa44-15dc-8144-935f-c47053da483f)
**Notion DB:** Presupuestos (39dfaa44-15dc-814a-b8b5-d05d254988e8)

---

## 📱 Agente de WhatsApp
**Función:** Procesamiento inteligente de mensajes
**Hace:**
- Leer log de MacroDroid
- Resumir mensajes con Groq IA
- Clasificar por contacto (cliente, familia, escuela, etc.)
- Enviar a ClickUp, Google Tasks, Notion según corresponda
- Guardar resúmenes en carpeta visible
**Prioridad:** ClickUp → Google Tasks → Carpeta → Notion

---

## 💵 Agente de Cobros
**Función:** Control de pagos y facturación
**Hace:**
- Registrar monto cobrado por trabajo
- Llevar control de deudas pendientes
- Avisar cobros vencidos
- Generar resumen de facturación semanal/mensual
**ClickUp List:** ✅ Completados (901714936124)

---

## 🔧 Agente de Materiales
**Función:** Gestión de materiales y proveedores
**Hace:**
- Mantener precios actualizados en 💵 Tarifas de Referencia
- Registrar nuevos materiales comprados
- Calcular necesidades por trabajo
- Comparar precios entre proveedores
**Notion DB:** Tarifas de Referencia (39dfaa44-15dc-8144-935f-c47053da483f)

---

## 📐 Agente de Planos
**Función:** Generación de planos y cálculos eléctricos
**Hace:**
- Calcular calibre de cable por longitud y corriente
- Calcular caída de tensión
- Generar diagramas SVG de instalaciones
- Calcular potencia máxima por toma
- Diseñar esquemas de tableros
**Script:** calculadora_electrica.py, generar_plano_electrico.py

---

## 🏫 Agente Familia
**Función:** Gestión de asuntos personales y familiares
**Hace:**
- Resumir mensajes de grupos escolares
- Crear recordatorios de escuela
- Registrar eventos de Evita y Francisco
- Gestionar contacto con Carolina
**Google Tasks List:** 🏠 Familia
**Notion DB:** Calendario y Recordatorios (39dfaa44-15dc-8190-8f53-f529da913a04)

---

## 📊 Agente de Análisis
**Función:** Reportes y estadísticas del negocio
**Hace:**
- Generar reporte semanal de trabajos
- Calcular facturación mensual
- Analizar trabajos más rentables
- Detectar zonas con más demanda
- Comparar períodos
- Predecir demanda

---

## Cómo usar los agentes

Cuando Darío me pide algo, yo activo el agente correspondiente:

| Pedido del usuario | Agente activado |
|-------------------|-----------------|
| "Creame un presupuesto para Joaquín" | Agente de Presupuestos |
| "Qué trabajos tengo pendientes?" | Agente de Trabajos |
| "Procesa los mensajes de hoy" | Agente de WhatsApp |
| "Cuánto me deben?" | Agente de Cobros |
| "Calculame el cable para 20m" | Agente de Planos |
| "Cómo voy este mes?" | Agente de Análisis |
| "Actualiza los precios" | Agente de Materiales |
| "Resumi lo de la escuela" | Agente Familia |

