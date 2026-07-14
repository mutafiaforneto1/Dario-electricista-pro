---
name: dario-electricista
description: >
  Sistema de gestión para Darío, electricista en La Plata.
  Procesa notificaciones de WhatsApp Business (vía MacroDroid + Groq IA),
  gestiona clientes y trabajos en Notion + ClickUp + Google Tasks + Google Sheets,
  genera presupuestos, y administra contactos.
---

# Darío Electricista - Sistema de Gestión v4.0

## Arquitectura (4 Herramientas)

```
📱 WhatsApp Business → MacroDroid → /sdcard/whatsapp_trabajos.log
    ↓
🤖 Groq (resumen inteligente)
    ↓
    ├── 📝 Notion → BASE DE DATOS PRINCIPAL (clientes, trabajos, calendario)
    ├── 🔧 ClickUp → RESPALDO (trabajos, seguimiento, IA)
    ├── ✅ Google Tasks → TAREAS DIARIAS + RECORDATORIOS (sincronizado con Calendar)
    └── 📁 Carpeta /sdcard/Documents/WhatsApp Resumenes/ → textos planos
```

### Regla de ruteo de WhatsApp

| Contacto | Notion | ClickUp | Google Tasks |
|----------|--------|---------|-------------|
| Clientes (Claudia, Jess, Romina, etc.) | ✅ Trabajo + Cliente | ✅ Como tarea | ✅ Recordatorio |
| Carolina | ✅ Calendario ❤️ | ❌ | ✅ Recordatorio ❤️ |
| Evita, Francisco | ✅ Calendario 👧👦 | ❌ | ✅ Recordatorio 👧👦 |
| Escuela (6°5°, 2do1ra) | ✅ Calendario 🏫 | ❌ | ✅ Recordatorio 🏫 |
| Números nuevos | ✅ Como cliente | ✅ Como cliente | ✅ Recordatorio |

## Notion → Base de Datos Principal

Token: `NOTION_TOKEN` en `/sdcard/Documents/.dario_env`

| Base de datos | ID | Uso |
|---------------|-----|------|
| 📋 Trabajos de Electricidad | `71872a30-fc98-4938-b199-2acbef5c4a4f` | Trabajos activos, presupuestos |
| 👥 Clientes | `39dfaa44-15dc-81b8-8e27-c7c4f0c85e06` | Contactos, teléfonos, zonas |
| 💰 Presupuestos | `39dfaa44-15dc-814a-b8b5-d05d254988e8` | Detalle materiales, mano de obra |
| 📅 Calendario y Recordatorios | `39dfaa44-15dc-8190-8f53-f529da913a04` | Eventos, llamadas |
| 💵 Tarifas de Referencia | `39dfaa44-15dc-8144-935f-c47053da483f` | Lista de precios |

## ClickUp → Respaldo

Token: `CLICKUP_TOKEN` en `/sdcard/Documents/.dario_env`

| Lista | ID | Uso |
|-------|-----|------|
| 📋 Trabajos | 901714935828 | Trabajos activos |
| 👥 Clientes | 901714936090 | Contactos |
| 💰 Tarifas | 901714936121 | Precios |
| ✅ Completados | 901714936124 | Historial |

## Google Tasks → Recordatorios (sincronizado con Calendar)

| Lista | Uso |
|-------|------|
| ⚡ Electricista La Plata | Trabajos, cobros, clientes |
| 🏠 Familia | Carolina, hijos, escuela |

## Google Sheets → Legacy

**Link:** [Planilla de Clientes](https://docs.google.com/spreadsheets/d/1QHNBPS3k8BTpkIBIA8yl7LssAvGF-wqJKbOSv0OGIgY/edit)

## API Keys

Las keys están en `/sdcard/Documents/.dario_env`:
- ClickUp, Groq, Notion, Google OAuth (Tasks + Sheets)

## Scripts

```bash
# Procesar WhatsApp (crea en Notion + ClickUp + Tasks)
source /sdcard/Documents/.dario_env && python3 scripts/procesar_whatsapp.py

# Calculadora eléctrica
python3 scripts/calculadora_electrica.py cable 20 380 10

# Generar planos
python3 scripts/generar_plano_electrico.py --tipo instalacion --archivo plano.svg

# Limpiar duplicados en ClickUp
python3 scripts/clickup_limpiar_duplicados.py
```

## Google Tasks Token

El token OAuth2 está en: `/sdcard/Documents/gtasks_token.json`

## Respaldo GitHub

```bash
git clone https://github.com/mutafiaforneto1/Dario-electricista-pro.git
```
