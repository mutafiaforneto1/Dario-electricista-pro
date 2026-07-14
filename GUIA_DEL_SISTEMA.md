# ⚡ Darío Electricista - Guía Completa del Sistema v4.0

## Arquitectura (4 Herramientas)

```
📱 WhatsApp Business → MacroDroid → Log
    → 🤖 Groq (resumen)
    → 📝 Notion (base de datos principal)
    → 🔧 ClickUp (respaldo)
    → ✅ Google Tasks + Calendar (recordatorios)
    → 📊 Google Sheets (clientes legacy)
```

---

## Herramienta 1: Notion → Base de Datos Principal

### Estructura de Bases de Datos

```
⚡ Darío Electricista - Sistema
├── 📋 Trabajos de Electricidad (22 propiedades)
│   ├── 🔗 Relación con Clientes
│   ├── 📸 Fotos: Antes, Después, Fotos del trabajo
│   ├── 💰 Presupuesto, Monto Cobrado, Método de pago
│   └── 📅 Fecha programada, Garantía hasta
├── 👥 Clientes (11 propiedades)
│   ├── 🔗 Relación con Trabajos y Presupuestos
│   ├── 📊 Total Gastado (calculado)
│   └── 🏷️ Estado, Zona, Origen
├── 💰 Presupuestos (13 propiedades)
│   ├── 🔗 Relación con Clientes
│   ├── 📸 Foto del presupuesto
│   └── 💰 Materiales, Mano de Obra, Total
├── 📅 Calendario y Recordatorios (8 propiedades)
│   ├── 🔗 Relación con Trabajos
│   └── 🏷️ Tipo: Trabajo, Personal, Escuela, Hijos, Cobro
└── 💵 Tarifas de Referencia (4 propiedades)
    └── 💰 Precios por categoría
```

### Token de Notion
```
NOTION_TOKEN=TU_TOKEN_AQUI
```

### Cómo usar Notion
- Los mensajes de WhatsApp se procesan y crean entradas automáticamente
- ClickUp mantiene respaldo sincronizado
- Google Tasks + Calendar para recordatorios diarios

---

## Herramienta 2: ClickUp → Respaldo

### Estructura del Espacio

```
⚡ Electricista La Plata (Folder: 90179652315)
├── 📋 Trabajos (901714935828)
├── 👥 Clientes (901714936090)
├── 💰 Tarifas (901714936121)
└── ✅ Completados (901714936124)
```

### Token de ClickUp
```
CLICKUP_TOKEN=pk_210092159_EBJMB4SH20GXBSA4QH43UTZNWXEIYZRW
```

---

## Herramienta 3: Google Tasks + Calendar → Recordatorios Diarios

### Estructura de Listas

| Lista | Contenido |
|-------|-----------|
| ⚡ Electricista La Plata | Recordatorios de trabajos, cobros, llamar a clientes |
| 🏠 Familia | Carolina, Evita, Francisco, escuela, personal |

### Cómo usar Google Tasks
- Las tareas aparecen automáticamente al procesar WhatsApp
- Se sincronizan solas con Google Calendar
- Las alarmas del calendario te avisan en el celu

---

## Herramienta 4: Google Sheets → Legacy

**Link:** [Planilla de Clientes](https://docs.google.com/spreadsheets/d/1QHNBPS3k8BTpkIBIA8yl7LssAvGF-wqJKbOSv0OGIgY/edit)

---

## Flujo WhatsApp Automático

Cuando llega un mensaje de WhatsApp:

| Quién escribe | Notion | ClickUp | Google Tasks |
|--------------|--------|---------|-------------|
| Clientes | ✅ Trabajo + Cliente | ✅ Tarea | ✅ Recordatorio |
| Carolina | ✅ Calendario ❤️ | ❌ | ✅ Recordatorio ❤️ |
| Evita/Francisco | ✅ Calendario 👧 | ❌ | ✅ Recordatorio |
| Escuela | ✅ Calendario 🏫 | ❌ | ✅ Recordatorio 🏫 |
| Número nuevo | ✅ Como cliente | ✅ Como cliente | ✅ Recordatorio |

### Para procesar WhatsApp manualmente
```bash
source /sdcard/Documents/.dario_env && python3 procesar_whatsapp.py
```

### Para dejarlo corriendo automático (cada 60s)
```bash
source /sdcard/Documents/.dario_env && python3 procesar_whatsapp.py --watch
```

---

## Scripts Disponibles

| Script | Comando | Función |
|--------|---------|---------|
| Procesador WhatsApp | `python3 procesar_whatsapp.py` | Lee log → Groq → Notion + ClickUp + Tasks |
| Calculadora Eléctrica | `python3 calculadora_electrica.py cable 20 380 10` | Calcula calibre, caída, potencia |
| Generar Planos | `python3 generar_plano_electrico.py --tipo instalacion --archivo plano.svg` | Crea planos SVG |
| Limpiar Duplicados | `python3 clickup_limpiar_duplicados.py` | Cierra tareas repetidas |
| Buscar Presupuestos | `python3 clickup_buscar_presupuestos.py` | Busca por cliente, monto |

---

## Tarifas de Referencia (13/07/2026)

| Servicio | Precio |
|----------|--------|
| Boca eléctrica (térmica o disyuntor) | $90.000 |
| Visita para presupuesto | $20.000 (se descuenta) |
| Media jornada | Desde $45.000 |
| Jornada completa | Desde $90.000 |
| Armado de tablero completo | $170.000 |
| Reconexión de acometida | $60.000 |
| Toma exterior 20A | $40.000 |
| Instalación grande (1-2 días) | Desde $80.000 |
| Urgencia | $80.000 |

---

## Respaldo y Restauración

### Para restaurar desde cero
1. Instalar Termux + Shizuku + MacroDroid
2. Clonar el repo de GitHub
3. Copiar `.dario_env` con las API keys
4. Ejecutar `restaurar_sistema.sh`
5. Re-autorizar Google Tasks + Sheets

### Archivos importantes a respaldar
| Archivo | Qué contiene |
|---------|-------------|
| `/sdcard/Documents/gtasks_token.json` | Token Google Tasks + Sheets |
| `/sdcard/Documents/.dario_env` | API keys (ClickUp, Groq, Notion, Google) |
| `/sdcard/whatsapp_trabajos.log` | Historial de WhatsApp |
| `/sdcard/Documents/WhatsApp Resumenes/` | Resúmenes por contacto |

---

## Contacto

- **Nombre:** Darío Díaz Gonzalez
- **Rubro:** Electricista en La Plata
- **Email:** diazgonzalezdario@gmail.com
- **WhatsApp Business:** +54 221 577-6391

---

*Generado el 14/07/2026 - Sistema v4.0*
