# ⚡ Darío Electricista - Guía Completa del Sistema v4.1

## Arquitectura

```
📱 WhatsApp Business → MacroDroid → /sdcard/whatsapp_trabajos.log
    ↓ (cada 60s en background)
🤖 Groq (resumen inteligente)
    ↓
    ├── 📋 ClickUp → GESTION PRINCIPAL (trabajos, clientes, seguimiento)
    ├── ✅ Google Tasks + Calendar → RECORDATORIOS DIARIOS (sincronizado)
    ├── 📁 Carpeta /sdcard/Documents/WhatsApp Resumenes/ → textos planos
    └── 📝 Notion → REGISTRO (backup de todo)
```

## Prioridad de procesamiento

1. **ClickUp** → Trabajo principal (tareas, clientes, presupuestos)
2. **Google Tasks + Calendar** → Recordatorios que aparecen en el celu
3. **Carpeta visible** → Resúmenes por contacto
4. **Notion** → Registro de todo lo procesado

## Servicio 24/7

```bash
# El servicio corre en tmux automaticamente
tmux attach -t whatsapp    # Ver el servicio

# Crontab reinicia si algo falla (cada 5 min)
crontab -l                 # Ver crontab

# Log del servicio
cat /tmp/watch_whatsapp.log
```

## Para procesar manualmente

```bash
# Procesar ahora
python3 /root/.codex/skills/dario-electricista/scripts/procesar_whatsapp.py

# Solo test (no guarda)
python3 /root/.codex/skills/dario-electricista/scripts/procesar_whatsapp.py --test
```

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

## Respaldo

GitHub: `mutafiaforneto1/Dario-electricista-pro`

---

*Actualizado el 15/07/2026 - Sistema v4.1*
