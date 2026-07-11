#!/system/bin/sh
# Wrapper para MacroDroid - Procesa mensajes de WhatsApp Business
# MacroDroid llama a este script, que ejecuta el procesador Python
# El log se lee via shizuku, los resúmenes van a ClickUp + Obsidian

SCRIPT="/sdcard/Documents/Obsidian trabajo optimizado 2/Scripts/whatsapp_processor/procesar_whatsapp.py"

if [ -f "$SCRIPT" ]; then
    # Intentar con python3 de Termux
    if command -v python3 >/dev/null 2>&1; then
        exec python3 "$SCRIPT"
    # Sino, intentar con shizuku ejecutando python3 como root
    else
        exec shizuku sh -c "python3 $SCRIPT"
    fi
else
    echo "ERROR: $SCRIPT no encontrado" >&2
    exit 1
fi
