from telegram.ext import Application, CommandHandler
from consultas_vault import *

# Tu Token de BotFather
TOKEN = "8785612653:AAHGs7ik8gJWHI2wo-lo2p--U7tgjjpePJw"

def main():
    print("🚀 Bot iniciado. Presioná Ctrl+C para detener.")
    app = Application.builder().token(TOKEN).build()
    
    # Comandos disponibles
    app.add_handler(CommandHandler("vencidos", cmd_vencidos))
    app.add_handler(CommandHandler("catalogo", cmd_catalogo))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("materiales", cmd_materiales))
    
    app.run_polling()

if __name__ == "__main__":
    main()