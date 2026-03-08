#!/usr/bin/env python3
import os, re, logging
from datetime import date, datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Config
TOKEN = "8785612653:AAHGs7ik8gJWHI2wo-lo2p--U7tgjjpePJw"
CHAT_ID = 922023252
VAULT = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault"
TRABAJOS = f"{VAULT}/01_TRABAJOS"
LOG_FILE = f"{VAULT}/09_SCRIPTS/registro_bot.md"

logging.basicConfig(level=logging.WARNING)

# ─── UTILIDADES ─────────────────────────────────────────

def parse_fm(contenido):
    data = {}
    m = re.match(r"^---\n(.*?)\n---", contenido, re.DOTALL)
    if not m:
        return data
    for linea in m.group(1).split("\n"):
        kv = re.match(r"^(\w+):\s*(.*)$", linea)
        if kv:
            v = kv.group(2).strip().strip('"')
            v = re.sub(r"\[\[.*?\|(.+?)\]\]", r"\1", v)
            v = re.sub(r"\[\[(.+?)\]\]", r"\1", v)
            data[kv.group(1)] = v
    return data

def get_trabajos():
    trabajos = []
    for root, dirs, files in os.walk(TRABAJOS):
        dirs[:] = [d for d in dirs if d != "fotos"]
        for archivo in files:
            if not archivo.endswith(".md"):
                continue
            try:
                with open(os.path.join(root, archivo), "r", encoding="utf-8") as f:
                    contenido = f.read()
                data = parse_fm(contenido)
                if data.get("tipo") == "trabajo":
                    cliente = data.get("cliente", "")
                    if "/" in cliente:
                        cliente = cliente.split("/")[-1]
                    data["cliente"] = cliente
                    data["_archivo"] = archivo
                    trabajos.append(data)
            except:
                pass
    return trabajos

def fmt_pesos(n):
    try:
        return f"${int(n):,}".replace(",", ".")
    except:
        return "$0"

def log_evento(evento):
    """Guarda evento en el registro del vault."""
    hoy = datetime.now().strftime("%Y-%m-%d %H:%M")
    linea = f"| {hoy} | {evento} |\n"
    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w") as f:
                f.write("# Registro del Bot\n\n| Fecha | Evento |\n|---|---|\n")
        with open(LOG_FILE, "a") as f:
            f.write(linea)
    except:
        pass

# ─── COMANDOS ───────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = (
        "⚡ *Dario Electricista Pro*\n"
        "─────────────────────\n"
        "Comandos disponibles:\n\n"
        "📋 /registro — eventos de hoy\n"
        "📊 /semana — resumen semanal\n"
        "🛠 /activos — trabajos en curso\n"
        "💰 /cobros — pendientes de cobrar\n"
        "📈 /stats — estadísticas del mes\n"
        "💵 /dolar — cotización blue\n"
        "❓ /ayuda — esta lista"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def cmd_ayuda(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await cmd_start(update, ctx)

async def cmd_activos(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    trabajos = get_trabajos()
    activos = [t for t in trabajos if t.get("estado") in ["En curso", "pendiente"]]
    if not activos:
        await update.message.reply_text("✅ No hay trabajos activos.")
        return
    lineas = [f"🛠 *Trabajos activos* ({len(activos)})\n─────────────────────"]
    for t in activos:
        emoji = "🔧" if t.get("estado") == "En curso" else "⏳"
        lineas.append(
            f"{emoji} *{t.get('cliente', '?')}*\n"
            f"   Estado: {t.get('estado')}\n"
            f"   MO: {fmt_pesos(t.get('mano_de_obra', 0))}\n"
            f"   Fecha: {t.get('fecha', '?')}"
        )
    await update.message.reply_text("\n\n".join(lineas), parse_mode="Markdown")

async def cmd_cobros(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    trabajos = get_trabajos()
    sin_cobrar = [t for t in trabajos
                  if t.get("estado") == "terminado" and t.get("pagado") == "false"]
    if not sin_cobrar:
        await update.message.reply_text("✅ No hay cobros pendientes.")
        return
    total = sum(int(t.get("mano_de_obra", 0)) for t in sin_cobrar)
    lineas = [f"💰 *Sin cobrar* ({len(sin_cobrar)})\n─────────────────────"]
    for t in sin_cobrar:
        lineas.append(
            f"• *{t.get('cliente', '?')}*\n"
            f"  {fmt_pesos(t.get('mano_de_obra', 0))} — {t.get('fecha', '?')}"
        )
    lineas.append(f"─────────────────────\n💵 *Total: {fmt_pesos(total)}*")
    await update.message.reply_text("\n\n".join(lineas), parse_mode="Markdown")

async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    trabajos = get_trabajos()
    hoy = date.today()
    mes = hoy.strftime("%Y-%m")
    este_mes = [t for t in trabajos if t.get("fecha", "")[:7] == mes]
    total_mes = sum(int(t.get("mano_de_obra", 0)) for t in este_mes)
    cobrado_mes = sum(int(t.get("mano_de_obra", 0)) for t in este_mes
                      if t.get("pagado") == "true")
    activos = len([t for t in trabajos if t.get("estado") in ["En curso", "pendiente"]])
    sin_cobrar_total = sum(int(t.get("mano_de_obra", 0)) for t in trabajos
                           if t.get("estado") == "terminado" and t.get("pagado") == "false")
    msg = (
        f"📈 *Estadísticas — {hoy.strftime('%B %Y').capitalize()}*\n"
        f"─────────────────────\n"
        f"🗓 Trabajos este mes: {len(este_mes)}\n"
        f"💵 Facturado: {fmt_pesos(total_mes)}\n"
        f"✅ Cobrado: {fmt_pesos(cobrado_mes)}\n"
        f"⏳ Sin cobrar: {fmt_pesos(sin_cobrar_total)}\n"
        f"🔧 Activos ahora: {activos}"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def cmd_semana(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    from datetime import timedelta
    trabajos = get_trabajos()
    hoy = date.today()
    lunes = hoy - timedelta(days=hoy.weekday())
    semana = [t for t in trabajos
              if t.get("fecha", "") >= lunes.strftime("%Y-%m-%d")]
    total = sum(int(t.get("mano_de_obra", 0)) for t in semana)
    cobrado = sum(int(t.get("mano_de_obra", 0)) for t in semana
                  if t.get("pagado") == "true")
    lineas = [
        f"📅 *Semana del {lunes.strftime('%d/%m')}*\n"
        f"─────────────────────\n"
        f"Trabajos: {len(semana)}\n"
        f"Facturado: {fmt_pesos(total)}\n"
        f"Cobrado: {fmt_pesos(cobrado)}\n"
        f"─────────────────────"
    ]
    for t in semana:
        cobrado_txt = "✅" if t.get("pagado") == "true" else "❌"
        lineas.append(f"{cobrado_txt} *{t.get('cliente','?')}* — {fmt_pesos(t.get('mano_de_obra',0))}")
    await update.message.reply_text("\n".join(lineas), parse_mode="Markdown")

async def cmd_registro(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lineas = f.readlines()
        hoy = date.today().strftime("%Y-%m-%d")
        eventos_hoy = [l.strip() for l in lineas if hoy in l and "|" in l]
        if not eventos_hoy:
            await update.message.reply_text(f"📋 Sin eventos registrados hoy ({hoy}).")
            return
        msg = f"📋 *Registro de hoy {hoy}*\n─────────────────────\n"
        for e in eventos_hoy[-20:]:
            partes = [p.strip() for p in e.split("|") if p.strip()]
            if len(partes) >= 2:
                msg += f"• {partes[0][11:]} — {partes[1]}\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
    except:
        await update.message.reply_text("📋 Sin registro disponible.")

async def cmd_dolar(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get("https://dolarapi.com/v1/dolares/blue")
            data = r.json()
        compra = data.get("compra", "?")
        venta = data.get("venta", "?")
        msg = (
            f"💵 *Dólar Blue*\n"
            f"─────────────────────\n"
            f"Compra: ${compra}\n"
            f"Venta:  ${venta}"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ─── NOTIFICADOR (llamado desde otros scripts) ──────────

async def notificar(app, mensaje):
    await app.bot.send_message(chat_id=CHAT_ID, text=mensaje, parse_mode="Markdown")

# ─── MAIN ───────────────────────────────────────────────

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("ayuda", cmd_ayuda))
    app.add_handler(CommandHandler("activos", cmd_activos))
    app.add_handler(CommandHandler("cobros", cmd_cobros))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("semana", cmd_semana))
    app.add_handler(CommandHandler("registro", cmd_registro))
    app.add_handler(CommandHandler("dolar", cmd_dolar))
    print("Bot iniciado. Esperando comandos...")
    log_evento("Bot iniciado")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
