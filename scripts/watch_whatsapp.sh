#!/bin/bash
# WhatsApp Processor Watch Service
# Runs every 60 seconds, processes new messages

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROCESSOR="$SCRIPT_DIR/procesar_whatsapp.py"
ENV_FILE="/sdcard/Documents/.dario_env"
LOG_FILE="/tmp/watch_whatsapp.log"

echo "$(date): Watch service started" >> "$LOG_FILE"

while true; do
    if [ -f "$ENV_FILE" ]; then
        cd "$SCRIPT_DIR/.."
        python3 "$PROCESSOR" >> "$LOG_FILE" 2>&1
    fi
    sleep 60
done
