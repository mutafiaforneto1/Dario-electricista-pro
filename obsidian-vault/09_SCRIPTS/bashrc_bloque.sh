alias sync='/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/09_SCRIPTS/sync_gdrive.sh'
alias bot_start='cd /storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/09_SCRIPTS/ && python3 asistente_electro_bot.py &'
if ! pgrep -f "asistente_electro_bot.py" > /dev/null; then
    bot_start
fi
sync &
