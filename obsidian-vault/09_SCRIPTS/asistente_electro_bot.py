import os
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler

TOKEN = "8785612653:AAHGs7ik8gJWHI2wo-lo2p--U7tgjjpePJw"
VAULT = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault"
T_DIR = os.path.join(VAULT, "01_TRABAJOS")

CLIENTE, DIRECCION, TAREA = range(3)

async def start(u, c):
    await u.message.reply_text("⚡ *Bot GitHub Activo*\n/nuevo - Obra\n/resumen - Balance")

async def cmd_resumen(u, c):
    obras = [f for f in os.listdir(T_DIR) if f.endswith(".md")]
    await u.message.reply_text(f"📊 *SISTEMA GITHUB*\nObras: {len(obras)}")

async def n_in(u, c):
    await u.message.reply_text("👤 Cliente:"); return CLIENTE
async def n_cl(u, c):
    c.user_data['c'] = u.message.text
    await u.message.reply_text("📍 Dirección:"); return DIRECCION
async def n_di(u, c):
    c.user_data['d'] = u.message.text
    await u.message.reply_text("📝 Tarea:"); return TAREA
async def n_fi(u, c):
    f_hoy = datetime.now().strftime("%Y-%m-%d")
    nom = f"{c.user_data['c']} - {c.user_data['d']}.md".replace("/","-")
    with open(os.path.join(T_DIR, nom), "w", encoding="utf-8") as f:
        f.write(f"---\ntipo: trabajo\nfecha: {f_hoy}\n---\n# {u.message.text}")
    await u.message.reply_text("✅ Guardado en Nuevo Vault"); return -1

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(ConversationHandler(entry_points=[CommandHandler("nuevo", n_in)], states={CLIENTE:[MessageHandler(filters.TEXT & ~filters.COMMAND, n_cl)], DIRECCION:[MessageHandler(filters.TEXT & ~filters.COMMAND, n_di)], TAREA:[MessageHandler(filters.TEXT & ~filters.COMMAND, n_fi)]}, fallbacks=[CommandHandler("cancel", lambda u,c: -1)]))
    app.add_handler(CommandHandler("resumen", cmd_resumen))
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__": main()
