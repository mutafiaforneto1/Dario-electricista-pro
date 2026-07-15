---
name: dario-electricista
description: >
  Sistema de gestión para Darío, electricista en La Plata.
  Procesa notificaciones de WhatsApp Business (vía MacroDroid + Groq IA),
  gestiona clientes y trabajos en ClickUp + Google Tasks + Notion,
  genera presupuestos, y administra contactos.
  Incluye sistema de agentes para gestión especializada.
---

# Darío Electricista - Sistema de Gestión v4.1

## Arquitectura

```
📱 WhatsApp Business → MacroDroid → /sdcard/whatsapp_trabajos.log
    ↓ (cada 60s en background)
🤖 Groq (resumen inteligente)
    ↓
    ├── 📋 ClickUp → GESTION PRINCIPAL (trabajos, clientes, presupuestos)
    ├── ✅ Google Tasks + Calendar → RECORDATORIOS DIARIOS
    ├── 📁 Carpeta /sdcard/Documents/WhatsApp Resumenes/ → textos planos
    └── 📝 Notion → REGISTRO
```

## Sistema de Agentes

Ver `agents/AGENTS.md` para documentación completa.

| Agente | Función |
|--------|---------|
| 📋 Trabajos | Crear, actualizar, seguimiento de obras |
| 👤 Clientes | Base de datos de contactos |
| 💰 Presupuestos | Generar y gestionar presupuestos |
| 📱 WhatsApp | Procesar mensajes con IA |
| 💵 Cobros | Control de pagos y deudas |
| 🔧 Materiales | Precios y proveedores |
| 📐 Planos | Cálculos y diagramas eléctricos |
| 🏫 Familia | Asuntos personales y escuela |
| 📊 Análisis | Reportes y estadísticas |

## Herramientas

| Herramienta | Función | Prioridad |
|-------------|---------|-----------|
| ClickUp | Gestión de trabajos y clientes | ⭐ Principal |
| Google Tasks + Calendar | Recordatorios diarios | ⭐ Principal |
| Notion | Registro y backup | Secundario |
| MacroDroid | Captura notificaciones WhatsApp | Infraestructura |
| Groq | Resúmenes con IA | Infraestructura |

## API Keys

Las keys están en `/sdcard/Documents/.dario_env`:
- ClickUp, Groq, Notion, Google OAuth

## Servicio 24/7

```bash
# El servicio corre en tmux automaticamente
tmux attach -t whatsapp    # Ver el servicio
cat /tmp/watch_whatsapp.log  # Ver log
```

## Scripts

```bash
# Procesar WhatsApp (ClickUp + Tasks + Notion)
python3 scripts/procesar_whatsapp.py

# Calculadora eléctrica
python3 scripts/calculadora_electrica.py cable 20 380 10

# Generar planos
python3 scripts/generar_plano_electrico.py --tipo instalacion --archivo plano.svg
```

## Respaldo

GitHub: `mutafiaforneto1/Dario-electricista-pro`

---

*Actualizado el 15/07/2026 - Sistema v4.1 con Agentes*
