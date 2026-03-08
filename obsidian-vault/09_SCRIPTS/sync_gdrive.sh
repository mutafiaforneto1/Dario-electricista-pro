#!/bin/bash
LOCAL="/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault"
REMOTE="gdrive:ObsidianBackup"
LOG_FILE="$LOCAL/09_SCRIPTS/sync_log.txt"
rclone sync "$LOCAL" "$REMOTE" --drive-chunk-size 32M --log-file "$LOG_FILE"
if [ $? -eq 0 ]; then
    echo "✅ [$(date)] Sync OK" >> "$LOG_FILE"
else
    echo "❌ [$(date)] Sync Error" >> "$LOG_FILE"
fi
