#!/bin/bash
pkill -f asistente_electro_bot.py
echo "⚡ Iniciando Asistente Electro-Bot..."
python3 asistente_electro_bot.py > bot.log 2>&1 &
echo "☁️ Ejecutando Sincronización con Drive..."
rclone sync /storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault gdrive:ObsidianBackup --progress &
echo "🚀 ¡Todo listo, Dario! El bot está en camino."
