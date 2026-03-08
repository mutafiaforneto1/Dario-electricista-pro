# --- BLOQUE DE AUTORUN PARA DARIO ---

# Alias útiles para el día a día
alias sync='/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/09_SCRIPTS/sync_gdrive.sh'
alias log_bot='tail -f /storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/09_SCRIPTS/nohup.out'
alias log_sync='cat /storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/09_SCRIPTS/sync_log.txt'
alias bot_stop='pkill -f asistente_electro_bot.py'
alias bot_start='cd /storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/09_SCRIPTS/ && python3 asistente_electro_bot.py &'

# 1. Iniciar el Bot si no está corriendo
if ! pgrep -f "asistente_electro_bot.py" > /dev/null; then
    echo "⚡ Iniciando Asistente Electro-Bot..."
    bot_start
fi

# 2. Ejecutar sincronización inicial en segundo plano
echo "☁️ Sincronizando Vault con Google Drive en segundo plano..."
sync &

echo "🚀 Entorno de Dario listo. ¡A trabajar!"
# ------------------------------------