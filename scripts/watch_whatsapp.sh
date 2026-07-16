#!/bin/bash
# WhatsApp Processor Watch Service + Agent Monitor

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROCESSOR="$SCRIPT_DIR/procesar_whatsapp.py"
MONITOR="$SCRIPT_DIR/agent_monitor.py"
ENV_FILE="/sdcard/Documents/.dario_env"
LOG_FILE="/tmp/watch_whatsapp.log"

echo "$(date): Watch service started (with Agent Monitor)" >> "$LOG_FILE"

LAST_MONITOR=0
MONITOR_INTERVAL=14400  # 4 hours in seconds

while true; do
    if [ -f "$ENV_FILE" ]; then
        cd "$SCRIPT_DIR/.."
        
        # Process WhatsApp messages (every 60s)
        python3 "$PROCESSOR" >> "$LOG_FILE" 2>&1
        
        # Agent Monitor (every 4 hours)
        NOW=$(date +%s)
        DIFF=$((NOW - LAST_MONITOR))
        if [ $DIFF -ge $MONITOR_INTERVAL ]; then
            echo "$(date): Running Agent Monitor..." >> "$LOG_FILE"
            python3 "$MONITOR" >> "$LOG_FILE" 2>&1
            LAST_MONITOR=$NOW
        fi
    fi
    sleep 60
done
