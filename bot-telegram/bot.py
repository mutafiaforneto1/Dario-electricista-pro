#!/usr/bin/env python3
import os, re, logging

# Cargar variables de entorno
_env = "/storage/emulated/0/Documents/Dario-electricista-pro/.env"
if os.path.exists(_env):
    with open(_env) as _f:
        for _l in _f:
            if "=" in _l and not _l.startswith("#"):
                k, v = _l.strip().split("=", 1)
                os.environ[k] = v
try:
    from dotenv import load_dotenv
    load_dotenv("/storage/emulated/0/Documents/Dario-electricista-pro/.env")
except: pass
from datetime import date, datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Config
TOKEN = "8785612653:AAHEbPWEqF2ytJuueOI_S1LMBIAwN_qj7mI"
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


def get_stats():
    trabajos = get_trabajos()
    mes = date.today().strftime("%Y-%m")
    activos = [t for t in trabajos if t.get("estado") in ["En curso","pendiente"]]
    sin_cobrar = [t for t in trabajos if t.get("estado")=="terminado" and t.get("pagado")=="false"]
    este_mes = [t for t in trabajos if t.get("fecha","")[:7]==mes]
    return {
        "activos": len(activos),
        "sin_cobrar": len(sin_cobrar),
        "total_mes": sum(int(t.get("mano_de_obra",0)) for t in este_mes),
        "total_pendiente": sum(int(t.get("mano_de_obra",0)) for t in sin_cobrar),
        "trabajos_activos": activos,
        "trabajos_sin_cobrar": sin_cobrar,
    }

# ─── COMANDOS ───────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = (
        "⚡ *Dario Electricista Pro*\n"
        "─────────────────────\n"
        "Comandos disponibles:\n\n"
        "📋 /registro — eventos de hoy\n"
        "📅 /agenda — resumen del día\n"
        "👤 /cliente nombre — historial de cliente\n"
        "🗓 /mes 2026-03 — trabajos del mes\n"
        "⚠️ /vencidos — deudores pendientes\n"
        "📦 /catalogo — precios DistriElectro\n"
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


async def cmd_vencidos(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    trabajos = get_trabajos()
    sin_cobrar = [t for t in trabajos if t.get("estado")=="terminado" and t.get("pagado")=="false"]
    if not sin_cobrar:
        await update.message.reply_text("✅ Sin deudores pendientes.")
        return
    lineas = [f"⚠️ *Deudores pendientes ({len(sin_cobrar)}):*\n─────────────────────"]
    for t in sin_cobrar:
        lineas.append(f"• *{t.get('cliente','?')}* — {fmt_pesos(t.get('mano_de_obra',0))} ({t.get('fecha','')})")
    total = sum(int(t.get("mano_de_obra",0)) for t in sin_cobrar)
    lineas.append(f"─────────────────────\n💵 Total: {fmt_pesos(total)}")
    await update.message.reply_text("\n".join(lineas), parse_mode="Markdown")

async def cmd_catalogo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    import sys
    sys.path.insert(0, "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/09_SCRIPTS")
    try:
        from consultas_vault import leer_catalogo
        texto = leer_catalogo()
    except Exception as e:
        texto = f"Error: {e}"
    if len(texto) > 4000:
        texto = texto[:4000] + "\n..._(recortado)_"
    await update.message.reply_text(texto, parse_mode="Markdown")

async def cmd_cliente(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Uso: /cliente NombreCliente")
        return
    nombre = " ".join(ctx.args).lower()
    trabajos = get_trabajos()
    encontrados = [t for t in trabajos if nombre in t.get("cliente","").lower()]
    if not encontrados:
        await update.message.reply_text(f"No encontré trabajos para *{nombre}*", parse_mode="Markdown")
        return
    total = sum(int(t.get("mano_de_obra",0)) for t in encontrados)
    cobrado = sum(int(t.get("mano_de_obra",0)) for t in encontrados if t.get("pagado")=="true")
    lineas = [f"👤 *{encontrados[0].get('cliente','?')}*\n─────────────────────"]
    for t in encontrados:
        emoji = "✅" if t.get("pagado")=="true" else "❌"
        lineas.append(f"{emoji} {t.get('fecha','')} — {fmt_pesos(t.get('mano_de_obra',0))} ({t.get('estado','')})")
    lineas.append(f"─────────────────────\n💵 Total: {fmt_pesos(total)} | Cobrado: {fmt_pesos(cobrado)}")
    await update.message.reply_text("\n".join(lineas), parse_mode="Markdown")

async def cmd_mes(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    from datetime import date
    mes = ctx.args[0] if ctx.args else date.today().strftime("%Y-%m")
    trabajos = get_trabajos()
    este_mes = [t for t in trabajos if t.get("fecha","")[:7]==mes]
    if not este_mes:
        await update.message.reply_text(f"Sin trabajos en {mes}")
        return
    total = sum(int(t.get("mano_de_obra",0)) for t in este_mes)
    cobrado = sum(int(t.get("mano_de_obra",0)) for t in este_mes if t.get("pagado")=="true")
    lineas = [f"📅 *{mes}* ({len(este_mes)} trabajos)\n─────────────────────"]
    for t in este_mes:
        emoji = "✅" if t.get("pagado")=="true" else "❌"
        lineas.append(f"{emoji} *{t.get('cliente','?')}* — {fmt_pesos(t.get('mano_de_obra',0))}")
    lineas.append(f"─────────────────────\n💵 Facturado: {fmt_pesos(total)} | Cobrado: {fmt_pesos(cobrado)}")
    await update.message.reply_text("\n".join(lineas), parse_mode="Markdown")

async def cmd_agenda(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    from datetime import date
    hoy = date.today().strftime("%d/%m/%Y")
    stats = get_stats()
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get("https://dolarapi.com/v1/dolares/blue")
            dolar = r.json().get("venta","?")
    except:
        dolar = "?"
    msg = (
        f"☀️ *Agenda {hoy}*\n"
        f"─────────────────────\n"
        f"🛠 Activos: *{stats['activos']}*\n"
        f"💰 Sin cobrar: *{stats['sin_cobrar']}* ({fmt_pesos(stats['total_pendiente'])})\n"
        f"📊 Este mes: *{fmt_pesos(stats['total_mes'])}*\n"
        f"💵 Dólar blue: *${dolar}*"
    )
    if stats["trabajos_activos"]:
        msg += "\n\n🔧 *En curso:*"
        for t in stats["trabajos_activos"][:5]:
            msg += f"\n• {t.get('cliente','?')} — {fmt_pesos(t.get('mano_de_obra',0))}"
    await update.message.reply_text(msg, parse_mode="Markdown")


async def cmd_natural(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Procesa mensajes de texto libre con IA."""
    mensaje = update.message.text.strip()
    await update.message.reply_text("🤔 Procesando...")

    import sys
    sys.path.insert(0, "/data/data/com.termux/files/home")
    from asistente_ia import interpretar

    accion = interpretar(mensaje)
    tipo = accion.get("accion", "responder")

    if tipo == "crear_trabajo":
        try:
            from datetime import date
            import os
            cliente = accion.get("cliente","?")
            descripcion = accion.get("descripcion","")
            monto = accion.get("monto", 0)
            fecha = date.today().strftime("%Y-%m-%d")
            TRABAJOS = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/01_TRABAJOS"
            carpeta = os.path.join(TRABAJOS, cliente)
            os.makedirs(carpeta, exist_ok=True)
            nombre = f"{cliente} - {fecha}.md"
            ruta = os.path.join(carpeta, nombre)
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(f"""---
tipo: trabajo
cliente: "[[{cliente}]]"
fecha: {fecha}
estado: pendiente
mano_de_obra: {monto}
costo_materiales: 0
pagado: false
---

# {cliente}

## Descripcion
{descripcion}

## Tareas
- [ ]

## Materiales usados

## Notas
""")
            await update.message.reply_text(
                f"✅ *Trabajo creado*\n"
                f"Cliente: {accion.get('cliente')}\n"
                f"Descripción: {accion.get('descripcion')}\n"
                f"MO: ${accion.get('monto',0):,}".replace(",","."),
                parse_mode="Markdown"
            )
            log_evento(f"Trabajo creado via IA: {accion.get('cliente')}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error al crear: {e}")

    elif tipo == "consultar_cliente":
        trabajos = get_trabajos()
        nombre = accion.get("cliente","").lower()
        encontrados = [t for t in trabajos if nombre in t.get("cliente","").lower()]
        if not encontrados:
            await update.message.reply_text(f"No encontré trabajos para {accion.get('cliente')}")
        else:
            total = sum(int(t.get("mano_de_obra",0)) for t in encontrados)
            cobrado = sum(int(t.get("mano_de_obra",0)) for t in encontrados if t.get("pagado")=="true")
            lineas = [f"👤 *{encontrados[0].get('cliente','?')}*\n─────────────────────"]
            for t in encontrados:
                emoji = "✅" if t.get("pagado")=="true" else "❌"
                lineas.append(f"{emoji} {t.get('fecha','')} — {fmt_pesos(t.get('mano_de_obra',0))}")
            lineas.append(f"─────────────────────\n💵 Total: {fmt_pesos(total)} | Cobrado: {fmt_pesos(cobrado)}")
            await update.message.reply_text("\n".join(lineas), parse_mode="Markdown")

    elif tipo == "ver_activos":
        await cmd_activos(update, ctx)

    elif tipo == "ver_cobros":
        await cmd_cobros(update, ctx)

    elif tipo == "ver_stats":
        await cmd_stats(update, ctx)

    elif tipo == "ver_dolar":
        await cmd_dolar(update, ctx)

    elif tipo == "marcar_cobrado":
        trabajos = get_trabajos()
        nombre = accion.get("cliente","").lower()
        encontrados = [t for t in trabajos
                      if nombre in t.get("cliente","").lower()
                      and t.get("estado")=="terminado"
                      and t.get("pagado")=="false"]
        if not encontrados:
            await update.message.reply_text(f"No encontré cobros pendientes para {accion.get('cliente')}")
        else:
            t = encontrados[0]
            actualizar_estado(t["_ruta"], "terminado", pagado=True)
            await update.message.reply_text(
                f"✅ *Cobrado*\n{t.get('cliente')} — {fmt_pesos(t.get('mano_de_obra',0))}",
                parse_mode="Markdown"
            )

    elif tipo == "anotar_diario":
        from datetime import datetime
        import os
        DIARIO = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/05_DIARIO"
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        hora = datetime.now().strftime("%H:%M")
        archivo = os.path.join(DIARIO, f"{fecha_hoy}.md")
        nota = accion.get("texto", mensaje)
        if not os.path.exists(archivo):
            with open(archivo, "w", encoding="utf-8") as f:
                f.write(f"# Diario {fecha_hoy}\n\n## Notas\n")
        with open(archivo, "a", encoding="utf-8") as f:
            f.write(f"- {hora}: {nota}\n")
        await update.message.reply_text(
            f"✅ *Anotado en el diario*\n🕐 {hora} — {nota}",
            parse_mode="Markdown"
        )

    else:
        texto = accion.get("texto", "No entendí. Usá /ayuda para ver los comandos.")
        await update.message.reply_text(texto)


async def cmd_precio(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Uso: /precio descripcion del trabajo")
        return
    descripcion = " ".join(ctx.args)
    await update.message.reply_text("🤔 Consultando precios...")
    import sys; sys.path.insert(0, "/data/data/com.termux/files/home")
    from ia_precios import sugerir_precio
    r = sugerir_precio(descripcion)
    if "error" in r:
        await update.message.reply_text("❌ Error: " + r["error"])
        return
    msg = (
        f"💡 *Sugerencia de precio*\n"
        f"_{descripcion}_\n"
        f"─────────────────────\n"
        f"💰 Sugerido: *${r.get('precio_sugerido',0):,}*\n"
        f"📉 Mínimo: ${r.get('precio_minimo',0):,}\n"
        f"📈 Máximo: ${r.get('precio_maximo',0):,}\n"
        f"─────────────────────\n"
        f"📝 {r.get('razon','')}"
    ).replace(",",".")
    await update.message.reply_text(msg, parse_mode="Markdown")

async def cmd_analisis(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Analizando tus ingresos...")
    import sys; sys.path.insert(0, "/data/data/com.termux/files/home")
    from ia_precios import analizar_ingresos
    resultado = analizar_ingresos()
    await update.message.reply_text("📈 *Análisis de ingresos*\n─────────────────────\n" + resultado, parse_mode="Markdown")


async def cmd_presupuesto_ia(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(
            "Uso: /presupuesto cliente, descripcion del trabajo\n\n"
            "Ejemplo:\n/presupuesto Tito, cambio de tablero 12 bocas 3 tomas y 2 llaves"
        )
        return

    texto = " ".join(ctx.args)
    await update.message.reply_text("⚡ Calculando presupuesto...")

    import sys, json, re
    sys.path.insert(0, "/data/data/com.termux/files/home")

    # Leer precios del vault
    PRECIOS_MD = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/08_PRECIOS/Precios_Actualizados.md"
    TARIFAS_MO = {
        "Boca completa": 85935,
        "Visita tecnica": 43043,
        "Servicio minimo": 40000,
        "Hora de trabajo": 43043,
        "Tablero hasta 6 bocas": 253859,
        "Tablero 7-12 bocas": 320000,
        "Tablero 13-24 bocas": 420000,
        "Tablero +24 bocas": 550000,
        "Puesta a tierra": 128855,
        "Ventilador sin luz": 80000,
        "Ventilador con luz": 90000,
    }

    try:
        with open(PRECIOS_MD, encoding="utf-8") as f:
            precios_texto = f.read()
    except:
        precios_texto = ""

    import groq
    client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

    tarifas_texto = "\n".join([f"- {k}: ${v}" for k,v in TARIFAS_MO.items()])

    prompt = (
        "Sos el asistente de Dario, electricista en La Plata.\n"
        "Analizá el trabajo pedido y armá un presupuesto detallado.\n\n"
        "TARIFAS MANO DE OBRA:\n" + tarifas_texto + "\n\n"
        "LISTA DE PRECIOS MATERIALES (DistriElectro):\n" + precios_texto[:2000] + "\n\n"
        "TRABAJO PEDIDO: " + texto + "\n\n"
        "Respondé SOLO con JSON valido:\n"
        '{"cliente": "nombre", "descripcion": "resumen", '
        '"mano_de_obra": [{"item": "nombre", "cantidad": 1, "precio_unit": 0}], '
        '"materiales": [{"item": "nombre", "cantidad": 1, "precio_unit": 0}], '
        '"ganancia_pct": 30, "observaciones": "texto opcional"}'
    )

    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2, max_tokens=800,
        )
        respuesta = re.sub("```json|```", "", chat.choices[0].message.content.strip()).strip()
        data = json.loads(respuesta)
    except Exception as e:
        await update.message.reply_text("❌ Error: " + str(e))
        return

    # Calcular totales
    ganancia = data.get("ganancia_pct", 30) / 100
    total_mo = sum(int(i.get("cantidad",1)) * int(i.get("precio_unit",0)) for i in data.get("mano_de_obra",[]))
    total_mat = sum(int(i.get("cantidad",1)) * int(i.get("precio_unit",0) * (1+ganancia)) for i in data.get("materiales",[]))
    total = total_mo + total_mat

    # Armar mensaje WhatsApp
    cliente = data.get("cliente", "Cliente")
    desc = data.get("descripcion", texto)

    lineas_mo = "\n".join([
        f"  • {i.get('item')} x{i.get('cantidad',1)}: ${int(i.get('cantidad',1)*i.get('precio_unit',0)):,}".replace(",",".")
        for i in data.get("mano_de_obra",[]) if i.get("precio_unit",0) > 0
    ])
    lineas_mat = "\n".join([
        f"  • {i.get('item')} x{i.get('cantidad',1)}: ${int(i.get('cantidad',1)*i.get('precio_unit',0)*(1+ganancia)):,}".replace(",",".")
        for i in data.get("materiales",[]) if i.get("precio_unit",0) > 0
    ])

    msg_wa = (
        f"⚡ *Presupuesto Electrico*\n"
        f"*Dario Electricista — La Plata*\n"
        f"──────────────────────────\n"
        f"Hola *{cliente}*, te paso el detalle:\n\n"
        f"🔧 *Mano de obra:*\n{lineas_mo}\n\n"
        f"📦 *Materiales (+{int(ganancia*100)}% ganancia):*\n{lineas_mat}\n\n"
        f"──────────────────────────\n"
        f"💰 *TOTAL: ${total:,}*\n\n"
        f"✅ Válido por 48hs.".replace(",",".")
    )

    if data.get("observaciones"):
        msg_wa += f"\n📝 {data.get('observaciones')}"

    await update.message.reply_text(msg_wa, parse_mode="Markdown")

    # Copiar al portapapeles via notificar
    try:
        import subprocess
        p = subprocess.Popen(["termux-clipboard-set"], stdin=subprocess.PIPE)
        p.communicate(input=msg_wa.encode("utf-8"))
        await update.message.reply_text("📋 Copiado al portapapeles — listo para WhatsApp")
    except:
        pass


async def cmd_mensaje(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(
            "Uso: /mensaje instruccion\n\n"
            "Ejemplos:\n"
            "/mensaje escribile a Tito recordandole que debe 150000, tono amigable\n"
            "/mensaje avisale a Maria Rosa que el trabajo esta listo\n"
            "/mensaje cobrale a Guillermo el trabajo de enero, tono firme"
        )
        return

    instruccion = " ".join(ctx.args)
    await update.message.reply_text("✍️ Redactando mensaje...")

    import groq, re, subprocess
    client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = (
        "Sos Dario, electricista en La Plata. Escribis el mensaje vos mismo, en primera persona.\n"
        "Nunca digas que sos un asistente ni que Dario te mando. Habla como si fueras Dario.\n"
        "Español argentino, breve, claro. Sin markdown ni asteriscos. Solo texto plano.\n"
        "No agregues explicaciones, solo el mensaje listo para enviar.\n\n"
        "INSTRUCCION: " + instruccion
    )

    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=300,
        )
        mensaje = chat.choices[0].message.content.strip()
    except Exception as e:
        await update.message.reply_text("❌ Error: " + str(e))
        return

    await update.message.reply_text(
        "📱 *Mensaje listo para WhatsApp:*\n"
        "─────────────────────\n" + mensaje,
        parse_mode="Markdown"
    )

    try:
        p = subprocess.Popen(["termux-clipboard-set"], stdin=subprocess.PIPE)
        p.communicate(input=mensaje.encode("utf-8"))
        await update.message.reply_text("📋 Copiado al portapapeles")
    except:
        pass


async def cmd_materiales(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(
            "Uso: /materiales descripcion del trabajo\n\n"
            "Ejemplo:\n/materiales instalar 4 tomas y 2 llaves en living"
        )
        return

    descripcion = " ".join(ctx.args)
    await update.message.reply_text("📦 Calculando materiales...")

    import groq, re, json, os
    api_key = os.getenv("GROQ_API_KEY")
    client = groq.Groq(api_key=api_key)

    PRECIOS_MD = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/08_PRECIOS/Precios_Actualizados.md"
    try:
        with open(PRECIOS_MD, encoding="utf-8") as f:
            precios_texto = f.read()[:3000]
    except:
        precios_texto = ""

    prompt = (
        "Sos un electricista experto en La Plata, Argentina.\n"
        "Arma la lista de materiales necesarios para el trabajo descrito.\n"
        "Usá los precios de la lista cuando estén disponibles.\n\n"
        "LISTA DE PRECIOS DISPONIBLES:\n" + precios_texto + "\n\n"
        "TRABAJO: " + descripcion + "\n\n"
        "Respondé SOLO con JSON valido:\n"
        '{"materiales": [{"item": "nombre", "cantidad": 1, "unidad": "u/m/kg", "precio_unit": 0, "nota": "opcional"}], '
        '"observaciones": "consejos o advertencias del trabajo"}'
    )

    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2, max_tokens=600,
        )
        respuesta = re.sub("```json|```", "", chat.choices[0].message.content.strip()).strip()
        data = json.loads(respuesta)
    except Exception as e:
        await update.message.reply_text("❌ Error: " + str(e))
        return

    materiales = data.get("materiales", [])
    total = sum(int(m.get("cantidad",1)) * int(m.get("precio_unit",0)) for m in materiales)

    lineas = [f"📦 *Lista de materiales*\n_{descripcion}_\n─────────────────────"]
    for m in materiales:
        cant = m.get("cantidad", 1)
        precio = int(m.get("precio_unit", 0))
        subtotal = cant * precio
        linea = f"• {m.get('item')} x{cant} {m.get('unidad','u')}"
        if precio > 0:
            linea += f" — ${subtotal:,}".replace(",",".")
        if m.get("nota"):
            linea += f"\n  _{m.get('nota')}_"
        lineas.append(linea)

    if total > 0:
        lineas.append(f"─────────────────────\n💵 Total materiales: *${total:,}*".replace(",","."))

    if data.get("observaciones"):
        lineas.append(f"\n⚠️ {data.get('observaciones')}")

    await update.message.reply_text("\n".join(lineas), parse_mode="Markdown")


async def cmd_buscar(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(
            "Uso: /buscar consulta\n\n"
            "Ejemplos:\n"
            "/buscar trabajos de tablero\n"
            "/buscar clientes que no pagaron\n"
            "/buscar problemas con termicas"
        )
        return

    consulta = " ".join(ctx.args)
    await update.message.reply_text("🔍 Buscando en tus notas...")

    import groq, re, json, os
    TRABAJOS = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/01_TRABAJOS"
    DIARIO = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/05_DIARIO"

    # Leer todos los trabajos
    notas = []
    for root, dirs, files in os.walk(TRABAJOS):
        dirs[:] = [d for d in dirs if d != "fotos"]
        for f in files:
            if not f.endswith(".md"): continue
            try:
                with open(os.path.join(root, f), encoding="utf-8") as fh:
                    texto = fh.read()
                notas.append({"archivo": f.replace(".md",""), "contenido": texto[:500]})
            except: pass

    # Leer ultimas notas del diario
    diario = []
    try:
        for f in sorted(os.listdir(DIARIO))[-7:]:
            if f.endswith(".md"):
                with open(os.path.join(DIARIO, f), encoding="utf-8") as fh:
                    diario.append(fh.read()[:300])
    except: pass

    notas_texto = "\n---\n".join([
        f"TRABAJO: {n['archivo']}\n{n['contenido']}" for n in notas[:20]
    ])
    diario_texto = "\n---\n".join(diario)

    api_key = os.getenv("GROQ_API_KEY")
    client = groq.Groq(api_key=api_key)

    prompt = (
        "Sos el asistente de Dario, electricista en La Plata.\n"
        "Busca en sus notas y responde la consulta de forma util y concreta.\n\n"
        "TRABAJOS REGISTRADOS:\n" + notas_texto + "\n\n"
        "DIARIO RECIENTE:\n" + diario_texto + "\n\n"
        "CONSULTA: " + consulta + "\n\n"
        "Responde en español argentino, maximo 10 lineas, directo y util.\n"
        "Si encontras trabajos relevantes, mencionalos con cliente y fecha."
    )

    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, max_tokens=500,
        )
        respuesta = chat.choices[0].message.content.strip()
    except Exception as e:
        await update.message.reply_text("❌ Error: " + str(e))
        return

    await update.message.reply_text(
        f"🔍 *Resultados para:* _{consulta}_\n─────────────────────\n{respuesta}",
        parse_mode="Markdown"
    )


async def cmd_clientes_ia(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👥 Analizando tus clientes...")

    import groq, os, re
    from datetime import date

    trabajos = get_trabajos()
    if not trabajos:
        await update.message.reply_text("No hay trabajos registrados.")
        return

    # Agrupar por cliente
    por_cliente = {}
    for t in trabajos:
        cliente = t.get("cliente","?")
        if cliente not in por_cliente:
            por_cliente[cliente] = {"trabajos": 0, "total": 0, "cobrado": 0, "fechas": []}
        por_cliente[cliente]["trabajos"] += 1
        monto = int(t.get("mano_de_obra", 0))
        por_cliente[cliente]["total"] += monto
        if t.get("pagado") == "true":
            por_cliente[cliente]["cobrado"] += monto
        if t.get("fecha"):
            por_cliente[cliente]["fechas"].append(t.get("fecha"))

    # Ordenar por total
    ranking = sorted(por_cliente.items(), key=lambda x: x[1]["total"], reverse=True)

    resumen = "\n".join([
        f"{c}: {d['trabajos']} trabajos, ${d['total']} facturado, ${d['cobrado']} cobrado"
        for c, d in ranking[:15]
    ])

    api_key = os.getenv("GROQ_API_KEY")
    client = groq.Groq(api_key=api_key)

    prompt = (
        "Sos el asistente de Dario, electricista en La Plata.\n"
        "Analiza sus clientes y da un informe util.\n\n"
        "DATOS POR CLIENTE:\n" + resumen + "\n\n"
        "Responde en español argentino con:\n"
        "1. Top 3 mejores clientes\n"
        "2. Clientes que deben plata\n"
        "3. Clientes mas frecuentes\n"
        "4. Consejo concreto para el negocio\n"
        "Maximo 12 lineas, directo y util."
    )

    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, max_tokens=500,
        )
        respuesta = chat.choices[0].message.content.strip()
    except Exception as e:
        await update.message.reply_text("❌ Error: " + str(e))
        return

    # Top clientes como tabla
    top = ranking[:5]
    lineas = ["👥 *Análisis de clientes*\n─────────────────────"]
    for c, d in top:
        pagado_pct = int(d["cobrado"]/d["total"]*100) if d["total"] > 0 else 0
        emoji = "⭐" if pagado_pct == 100 else "⚠️" if pagado_pct == 0 else "🔶"
        lineas.append(f"{emoji} *{c}*: {d['trabajos']} trabajos — {fmt_pesos(d['total'])}")

    lineas.append("─────────────────────\n" + respuesta)
    await update.message.reply_text("\n".join(lineas), parse_mode="Markdown")


async def cmd_prediccion(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔮 Analizando tendencias...")

    import groq, os
    from datetime import date, timedelta

    trabajos = get_trabajos()
    if not trabajos:
        await update.message.reply_text("No hay trabajos registrados.")
        return

    # Agrupar por mes
    por_mes = {}
    for t in trabajos:
        mes = t.get("fecha","")[:7]
        if not mes: continue
        if mes not in por_mes:
            por_mes[mes] = {"total": 0, "cantidad": 0, "cobrado": 0}
        monto = int(t.get("mano_de_obra", 0))
        por_mes[mes]["total"] += monto
        por_mes[mes]["cantidad"] += 1
        if t.get("pagado") == "true":
            por_mes[mes]["cobrado"] += monto

    # Mes actual y siguiente
    hoy = date.today()
    mes_actual = hoy.strftime("%Y-%m")
    mes_siguiente = (hoy.replace(day=1) + timedelta(days=32)).strftime("%Y-%m")
    dias_transcurridos = hoy.day
    import calendar
    dias_mes = calendar.monthrange(hoy.year, hoy.month)[1]

    resumen = "\n".join([
        f"{mes}: {d['cantidad']} trabajos, ${d['total']}, cobrado ${d['cobrado']}"
        for mes, d in sorted(por_mes.items())
    ])

    # Proyeccion simple del mes actual
    total_actual = por_mes.get(mes_actual, {}).get("total", 0)
    proyeccion_mes = int(total_actual * dias_mes / dias_transcurridos) if dias_transcurridos > 0 else 0

    api_key = os.getenv("GROQ_API_KEY")
    client = groq.Groq(api_key=api_key)

    prompt = (
        "Sos el asistente financiero de Dario, electricista en La Plata.\n"
        "Analiza su historial y predice sus ingresos futuros.\n\n"
        "HISTORIAL POR MES:\n" + resumen + "\n\n"
        f"Hoy es {hoy.strftime('%d/%m/%Y')}, dia {dias_transcurridos} de {dias_mes}.\n"
        f"Lo que lleva este mes ({mes_actual}): ${total_actual}\n"
        f"Proyeccion lineal del mes actual: ${proyeccion_mes}\n\n"
        "Responde en español argentino con:\n"
        f"1. Estimacion de cierre de {mes_actual}\n"
        f"2. Prediccion para {mes_siguiente}\n"
        "3. Tendencia general\n"
        "4. Consejo para mejorar ingresos\n"
        "Maximo 10 lineas, directo y concreto."
    )

    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, max_tokens=400,
        )
        respuesta = chat.choices[0].message.content.strip()
    except Exception as e:
        await update.message.reply_text("❌ Error: " + str(e))
        return

    msg = (
        f"🔮 Prediccion de ingresos\n"
        f"─────────────────────\n"
        f"Este mes llevas: {fmt_pesos(total_actual)}\n"
        f"Proyeccion al cierre: {fmt_pesos(proyeccion_mes)}\n"
        f"─────────────────────\n"
        f"{respuesta}"
    )

    await update.message.reply_text(msg)


async def cmd_recibo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(
            "Uso: /recibo cliente, descripcion, monto\n\n"
            "Ejemplo:\n/recibo Tito, instalacion de tablero 12 bocas, 320000"
        )
        return

    texto = " ".join(ctx.args)
    partes = [p.strip() for p in texto.split(",")]
    if len(partes) < 3:
        await update.message.reply_text("Faltan datos. Usá: /recibo cliente, descripcion, monto")
        return

    cliente = partes[0]
    descripcion = partes[1]
    try:
        monto = int(partes[2].replace(".","").replace("$",""))
    except:
        monto = 0

    await update.message.reply_text("📄 Generando recibo...")

    import os
    from datetime import date
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm

    fecha = date.today().strftime("%d/%m/%Y")
    numero = date.today().strftime("%Y%m%d") + str(abs(hash(cliente)))[-4:]
    output = f"/data/data/com.termux/files/home/recibo_{cliente.replace(' ','_')}_{date.today().strftime('%Y%m%d')}.pdf"

    doc = SimpleDocTemplate(output, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    elementos = []

    # Header
    estilo_titulo = ParagraphStyle("titulo", fontSize=20, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a2e"), spaceAfter=5)
    estilo_sub = ParagraphStyle("sub", fontSize=11, fontName="Helvetica",
        textColor=colors.HexColor("#444444"), spaceAfter=3)
    estilo_normal = ParagraphStyle("normal", fontSize=10, fontName="Helvetica",
        textColor=colors.HexColor("#333333"))

    elementos.append(Paragraph("⚡ DARIO ELECTRICISTA", estilo_titulo))
    elementos.append(Paragraph("La Plata, Buenos Aires", estilo_sub))
    elementos.append(Paragraph("Matrícula AAIERIC", estilo_sub))
    elementos.append(Spacer(1, 0.5*cm))

    # Linea divisoria
    tabla_linea = Table([[""]],colWidths=[17*cm])
    tabla_linea.setStyle(TableStyle([
        ("LINEABOVE", (0,0), (-1,0), 2, colors.HexColor("#f0a500")),
    ]))
    elementos.append(tabla_linea)
    elementos.append(Spacer(1, 0.5*cm))

    # Datos del recibo
    datos = [
        ["RECIBO DE PAGO", ""],
        ["N°:", numero],
        ["Fecha:", fecha],
        ["Cliente:", cliente],
    ]
    tabla_datos = Table(datos, colWidths=[4*cm, 13*cm])
    tabla_datos.setStyle(TableStyle([
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("FONTSIZE", (0,0), (-1,0), 14),
        ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor("#1a1a2e")),
        ("SPAN", (0,0), (-1,0)),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    elementos.append(tabla_datos)
    elementos.append(Spacer(1, 0.5*cm))

    # Detalle
    detalle = [
        ["Descripcion", "Monto"],
        [descripcion, f"$ {monto:,}".replace(",",".")],
        ["", ""],
        ["TOTAL", f"$ {monto:,}".replace(",",".")],
    ]
    tabla_detalle = Table(detalle, colWidths=[12*cm, 5*cm])
    tabla_detalle.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("FONTSIZE", (0,-1), (-1,-1), 12),
        ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#f0a500")),
        ("TEXTCOLOR", (0,-1), (-1,-1), colors.white),
        ("ALIGN", (1,0), (1,-1), "RIGHT"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#dddddd")),
        ("ROWBACKGROUNDS", (0,1), (-1,-2), [colors.white, colors.HexColor("#f9f9f9")]),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    elementos.append(tabla_detalle)
    elementos.append(Spacer(1, 1*cm))

    # Firma
    elementos.append(Paragraph("_______________________________", estilo_normal))
    elementos.append(Paragraph("Dario — Electricista Matriculado", estilo_normal))
    elementos.append(Spacer(1, 0.3*cm))
    elementos.append(Paragraph("Gracias por confiar en nuestro servicio ⚡", estilo_sub))

    doc.build(elementos)

    # Enviar PDF por Telegram
    with open(output, "rb") as pdf:
        await update.message.reply_document(
            document=pdf,
            filename=f"Recibo_{cliente}_{fecha.replace('/','_')}.pdf",
            caption=f"📄 Recibo para {cliente} — ${monto:,}\nFecha: {fecha}".replace(",",".")
        )

    os.remove(output)


async def cmd_llegar(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(
            "Uso: /llegar nombre del cliente\n\n"
            "Ejemplo:\n/llegar Tito\n/llegar Silvia vecina"
        )
        return

    busqueda = " ".join(ctx.args).lower()
    CLIENTES = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/02_CLIENTES"
    TRABAJOS = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/01_TRABAJOS"

    import os, re, urllib.parse

    # Buscar direccion en ficha de cliente
    direccion = None
    cliente_nombre = None

    for f in os.listdir(CLIENTES):
        if busqueda in f.lower() and f.endswith(".md"):
            cliente_nombre = f.replace("Cliente ","").replace(".md","")
            with open(os.path.join(CLIENTES, f), encoding="utf-8") as fh:
                texto = fh.read()
            m = re.search(r"direccion[:\s]+(.+)", texto, re.IGNORECASE)
            if m:
                direccion = m.group(1).strip().strip('"')
            break

    # Si no tiene en ficha, buscar en trabajos
    if not direccion:
        for root, dirs, files in os.walk(TRABAJOS):
            for f in files:
                if busqueda in f.lower() and f.endswith(".md"):
                    with open(os.path.join(root, f), encoding="utf-8") as fh:
                        texto = fh.read()
                    m = re.search(r"direcci[oó]n?[:\s]+(.+)", texto, re.IGNORECASE)
                    if m:
                        direccion = m.group(1).strip().strip('"')
                        if not cliente_nombre:
                            cliente_nombre = busqueda
                        break
            if direccion:
                break

    if not direccion:
        await update.message.reply_text(
            f"No encontré dirección para *{busqueda}*\n\n"
            "Agregá el campo en la ficha:\n`direccion: Calle 123 y 45, La Plata`",
            parse_mode="Markdown"
        )
        return

    # Generar links
    dir_encoded = urllib.parse.quote(direccion + ", La Plata, Buenos Aires")
    link_gmaps = f"https://www.google.com/maps/search/?api=1&query={dir_encoded}"
    link_osmand = f"https://osmand.net/go?q={dir_encoded}"
    link_waze = f"https://waze.com/ul?q={dir_encoded}"

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗺 Google Maps", url=link_gmaps)],
        [InlineKeyboardButton("🧭 OsmAnd", url=link_osmand)],
        [InlineKeyboardButton("🚗 Waze", url=link_waze)],
    ])

    await update.message.reply_text(
        f"📍 *{cliente_nombre}*\n`{direccion}`",
        parse_mode="Markdown",
        reply_markup=keyboard
    )


async def cmd_mapa(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Generando mapa de clientes...")

    import os, re, requests, time

    CLIENTES = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/02_CLIENTES"

    colores = {
        "centro":    "http://maps.google.com/mapfiles/ms/icons/red-dot.png",
        "berisso":   "http://maps.google.com/mapfiles/ms/icons/blue-dot.png",
        "periferia": "http://maps.google.com/mapfiles/ms/icons/yellow-dot.png",
        "norte":     "http://maps.google.com/mapfiles/ms/icons/green-dot.png",
        "sur":       "http://maps.google.com/mapfiles/ms/icons/purple-dot.png",
        "default":   "http://maps.google.com/mapfiles/ms/icons/orange-dot.png",
    }

    clientes = {}
    for f in os.listdir(CLIENTES):
        if not f.endswith(".md"): continue
        nombre = f.replace("Cliente ","").replace(".md","")
        path_c = os.path.join(CLIENTES, f)
        with open(path_c, encoding="utf-8") as fh:
            texto = fh.read()
        m_dir = re.search(r"direccion:\s*(.+)", texto, re.IGNORECASE)
        if not m_dir: continue
        direccion = m_dir.group(1).strip().strip('"')
        if not direccion or len(direccion) < 4: continue

        m_zona = re.search(r"zona:\s*(.+)", texto, re.IGNORECASE)
        zona = m_zona.group(1).strip().lower() if m_zona else "default"
        if not zona: zona = "default"

        m_lat = re.search(r"lat:\s*([-\d\.]+)", texto)
        m_lon = re.search(r"lon:\s*([-\d\.]+)", texto)

        if m_lat and m_lon:
            lat = float(m_lat.group(1))
            lon = float(m_lon.group(1))
            clientes[nombre] = (direccion, lat, lon, zona)
        else:
            try:
                time.sleep(1.5)
                query = direccion + ", La Plata, Buenos Aires, Argentina"
                r = requests.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={"q": query, "format": "json", "limit": 1},
                    headers={"User-Agent": "DarioElectricistaPro/1.0"},
                    timeout=8
                )
                data = r.json()
                if data:
                    lat = float(data[0]["lat"])
                    lon = float(data[0]["lon"])
                    clientes[nombre] = (direccion, lat, lon, zona)
                    with open(path_c, "r", encoding="utf-8") as fh:
                        fc = fh.read()
                    if "lat:" not in fc:
                        fc = fc.replace(
                            "direccion: " + direccion,
                            "direccion: " + direccion + "\nlat: " + str(lat) + "\nlon: " + str(lon)
                        )
                        with open(path_c, "w", encoding="utf-8") as fh:
                            fh.write(fc)
            except:
                pass

    if not clientes:
        await update.message.reply_text("No hay clientes con direccion registrada.")
        return

    # Estilos por zona
    estilos = ""
    for zona, icono in colores.items():
        estilos += "<Style id=\"" + zona + "\"><IconStyle><Icon><href>" + icono + "</href></Icon></IconStyle></Style>"

    kml_items = ""
    for nombre, (direccion, lat, lon, zona) in clientes.items():
        zona_key = zona if zona in colores else "default"
        kml_items += "<Placemark><name>" + nombre + "</name><description>" + direccion + " (" + zona + ")</description><styleUrl>#" + zona_key + "</styleUrl><Point><coordinates>" + str(lon) + "," + str(lat) + ",0</coordinates></Point></Placemark>"

    kml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><kml xmlns=\"http://www.opengis.net/kml/2.2\"><Document><name>Clientes Dario</name>" + estilos + kml_items + "</Document></kml>"

    output = "/data/data/com.termux/files/home/clientes_mapa.kml"
    with open(output, "w", encoding="utf-8") as f:
        f.write(kml)

    # Resumen por zona
    zonas_count = {}
    for _, (_, _, _, z) in clientes.items():
        zonas_count[z] = zonas_count.get(z, 0) + 1
    resumen = "\n".join([f"  {z}: {n}" for z, n in sorted(zonas_count.items())])

    with open(output, "rb") as f:
        await update.message.reply_document(
            document=f,
            filename="clientes_dario.kml",
            caption="Mapa de clientes — " + str(len(clientes)) + " ubicaciones\n\n" + resumen + "\n\nAbrilo con Google Maps u OsmAnd"
        )
    os.remove(output)


async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = (
        "⚡ *Dario Electricista Pro*\n"
        "─────────────────────\n"
        "Comandos disponibles:\n\n"
        "📋 /registro — eventos de hoy\n"
        "📅 /agenda — resumen del día\n"
        "👤 /cliente nombre — historial de cliente\n"
        "🗓 /mes 2026-03 — trabajos del mes\n"
        "⚠️ /vencidos — deudores pendientes\n"
        "📦 /catalogo — precios DistriElectro\n"
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


async def cmd_vencidos(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    trabajos = get_trabajos()
    sin_cobrar = [t for t in trabajos if t.get("estado")=="terminado" and t.get("pagado")=="false"]
    if not sin_cobrar:
        await update.message.reply_text("✅ Sin deudores pendientes.")
        return
    lineas = [f"⚠️ *Deudores pendientes ({len(sin_cobrar)}):*\n─────────────────────"]
    for t in sin_cobrar:
        lineas.append(f"• *{t.get('cliente','?')}* — {fmt_pesos(t.get('mano_de_obra',0))} ({t.get('fecha','')})")
    total = sum(int(t.get("mano_de_obra",0)) for t in sin_cobrar)
    lineas.append(f"─────────────────────\n💵 Total: {fmt_pesos(total)}")
    await update.message.reply_text("\n".join(lineas), parse_mode="Markdown")

async def cmd_catalogo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    import sys
    sys.path.insert(0, "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/09_SCRIPTS")
    try:
        from consultas_vault import leer_catalogo
        texto = leer_catalogo()
    except Exception as e:
        texto = f"Error: {e}"
    if len(texto) > 4000:
        texto = texto[:4000] + "\n..._(recortado)_"
    await update.message.reply_text(texto, parse_mode="Markdown")

async def cmd_cliente(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Uso: /cliente NombreCliente")
        return
    nombre = " ".join(ctx.args).lower()
    trabajos = get_trabajos()
    encontrados = [t for t in trabajos if nombre in t.get("cliente","").lower()]
    if not encontrados:
        await update.message.reply_text(f"No encontré trabajos para *{nombre}*", parse_mode="Markdown")
        return
    total = sum(int(t.get("mano_de_obra",0)) for t in encontrados)
    cobrado = sum(int(t.get("mano_de_obra",0)) for t in encontrados if t.get("pagado")=="true")
    lineas = [f"👤 *{encontrados[0].get('cliente','?')}*\n─────────────────────"]
    for t in encontrados:
        emoji = "✅" if t.get("pagado")=="true" else "❌"
        lineas.append(f"{emoji} {t.get('fecha','')} — {fmt_pesos(t.get('mano_de_obra',0))} ({t.get('estado','')})")
    lineas.append(f"─────────────────────\n💵 Total: {fmt_pesos(total)} | Cobrado: {fmt_pesos(cobrado)}")
    await update.message.reply_text("\n".join(lineas), parse_mode="Markdown")

async def cmd_mes(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    from datetime import date
    mes = ctx.args[0] if ctx.args else date.today().strftime("%Y-%m")
    trabajos = get_trabajos()
    este_mes = [t for t in trabajos if t.get("fecha","")[:7]==mes]
    if not este_mes:
        await update.message.reply_text(f"Sin trabajos en {mes}")
        return
    total = sum(int(t.get("mano_de_obra",0)) for t in este_mes)
    cobrado = sum(int(t.get("mano_de_obra",0)) for t in este_mes if t.get("pagado")=="true")
    lineas = [f"📅 *{mes}* ({len(este_mes)} trabajos)\n─────────────────────"]
    for t in este_mes:
        emoji = "✅" if t.get("pagado")=="true" else "❌"
        lineas.append(f"{emoji} *{t.get('cliente','?')}* — {fmt_pesos(t.get('mano_de_obra',0))}")
    lineas.append(f"─────────────────────\n💵 Facturado: {fmt_pesos(total)} | Cobrado: {fmt_pesos(cobrado)}")
    await update.message.reply_text("\n".join(lineas), parse_mode="Markdown")

async def cmd_agenda(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    from datetime import date
    hoy = date.today().strftime("%d/%m/%Y")
    stats = get_stats()
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get("https://dolarapi.com/v1/dolares/blue")
            dolar = r.json().get("venta","?")
    except:
        dolar = "?"
    msg = (
        f"☀️ *Agenda {hoy}*\n"
        f"─────────────────────\n"
        f"🛠 Activos: *{stats['activos']}*\n"
        f"💰 Sin cobrar: *{stats['sin_cobrar']}* ({fmt_pesos(stats['total_pendiente'])})\n"
        f"📊 Este mes: *{fmt_pesos(stats['total_mes'])}*\n"
        f"💵 Dólar blue: *${dolar}*"
    )
    if stats["trabajos_activos"]:
        msg += "\n\n🔧 *En curso:*"
        for t in stats["trabajos_activos"][:5]:
            msg += f"\n• {t.get('cliente','?')} — {fmt_pesos(t.get('mano_de_obra',0))}"
    await update.message.reply_text(msg, parse_mode="Markdown")


async def cmd_natural(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Procesa mensajes de texto libre con IA."""
    mensaje = update.message.text.strip()
    await update.message.reply_text("🤔 Procesando...")

    import sys
    sys.path.insert(0, "/data/data/com.termux/files/home")
    from asistente_ia import interpretar

    accion = interpretar(mensaje)
    tipo = accion.get("accion", "responder")

    if tipo == "crear_trabajo":
        try:
            from datetime import date
            import os
            cliente = accion.get("cliente","?")
            descripcion = accion.get("descripcion","")
            monto = accion.get("monto", 0)
            fecha = date.today().strftime("%Y-%m-%d")
            TRABAJOS = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/01_TRABAJOS"
            carpeta = os.path.join(TRABAJOS, cliente)
            os.makedirs(carpeta, exist_ok=True)
            nombre = f"{cliente} - {fecha}.md"
            ruta = os.path.join(carpeta, nombre)
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(f"""---
tipo: trabajo
cliente: "[[{cliente}]]"
fecha: {fecha}
estado: pendiente
mano_de_obra: {monto}
costo_materiales: 0
pagado: false
---

# {cliente}

## Descripcion
{descripcion}

## Tareas
- [ ]

## Materiales usados

## Notas
""")
            await update.message.reply_text(
                f"✅ *Trabajo creado*\n"
                f"Cliente: {accion.get('cliente')}\n"
                f"Descripción: {accion.get('descripcion')}\n"
                f"MO: ${accion.get('monto',0):,}".replace(",","."),
                parse_mode="Markdown"
            )
            log_evento(f"Trabajo creado via IA: {accion.get('cliente')}")
        except Exception as e:
            await update.message.reply_text(f"❌ Error al crear: {e}")

    elif tipo == "consultar_cliente":
        trabajos = get_trabajos()
        nombre = accion.get("cliente","").lower()
        encontrados = [t for t in trabajos if nombre in t.get("cliente","").lower()]
        if not encontrados:
            await update.message.reply_text(f"No encontré trabajos para {accion.get('cliente')}")
        else:
            total = sum(int(t.get("mano_de_obra",0)) for t in encontrados)
            cobrado = sum(int(t.get("mano_de_obra",0)) for t in encontrados if t.get("pagado")=="true")
            lineas = [f"👤 *{encontrados[0].get('cliente','?')}*\n─────────────────────"]
            for t in encontrados:
                emoji = "✅" if t.get("pagado")=="true" else "❌"
                lineas.append(f"{emoji} {t.get('fecha','')} — {fmt_pesos(t.get('mano_de_obra',0))}")
            lineas.append(f"─────────────────────\n💵 Total: {fmt_pesos(total)} | Cobrado: {fmt_pesos(cobrado)}")
            await update.message.reply_text("\n".join(lineas), parse_mode="Markdown")

    elif tipo == "ver_activos":
        await cmd_activos(update, ctx)

    elif tipo == "ver_cobros":
        await cmd_cobros(update, ctx)

    elif tipo == "ver_stats":
        await cmd_stats(update, ctx)

    elif tipo == "ver_dolar":
        await cmd_dolar(update, ctx)

    elif tipo == "marcar_cobrado":
        trabajos = get_trabajos()
        nombre = accion.get("cliente","").lower()
        encontrados = [t for t in trabajos
                      if nombre in t.get("cliente","").lower()
                      and t.get("estado")=="terminado"
                      and t.get("pagado")=="false"]
        if not encontrados:
            await update.message.reply_text(f"No encontré cobros pendientes para {accion.get('cliente')}")
        else:
            t = encontrados[0]
            actualizar_estado(t["_ruta"], "terminado", pagado=True)
            await update.message.reply_text(
                f"✅ *Cobrado*\n{t.get('cliente')} — {fmt_pesos(t.get('mano_de_obra',0))}",
                parse_mode="Markdown"
            )

    elif tipo == "anotar_diario":
        from datetime import datetime
        import os
        DIARIO = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/05_DIARIO"
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        hora = datetime.now().strftime("%H:%M")
        archivo = os.path.join(DIARIO, f"{fecha_hoy}.md")
        nota = accion.get("texto", mensaje)
        if not os.path.exists(archivo):
            with open(archivo, "w", encoding="utf-8") as f:
                f.write(f"# Diario {fecha_hoy}\n\n## Notas\n")
        with open(archivo, "a", encoding="utf-8") as f:
            f.write(f"- {hora}: {nota}\n")
        await update.message.reply_text(
            f"✅ *Anotado en el diario*\n🕐 {hora} — {nota}",
            parse_mode="Markdown"
        )

    else:
        texto = accion.get("texto", "No entendí. Usá /ayuda para ver los comandos.")
        await update.message.reply_text(texto)


async def cmd_precio(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text("Uso: /precio descripcion del trabajo")
        return
    descripcion = " ".join(ctx.args)
    await update.message.reply_text("🤔 Consultando precios...")
    import sys; sys.path.insert(0, "/data/data/com.termux/files/home")
    from ia_precios import sugerir_precio
    r = sugerir_precio(descripcion)
    if "error" in r:
        await update.message.reply_text("❌ Error: " + r["error"])
        return
    msg = (
        f"💡 *Sugerencia de precio*\n"
        f"_{descripcion}_\n"
        f"─────────────────────\n"
        f"💰 Sugerido: *${r.get('precio_sugerido',0):,}*\n"
        f"📉 Mínimo: ${r.get('precio_minimo',0):,}\n"
        f"📈 Máximo: ${r.get('precio_maximo',0):,}\n"
        f"─────────────────────\n"
        f"📝 {r.get('razon','')}"
    ).replace(",",".")
    await update.message.reply_text(msg, parse_mode="Markdown")

async def cmd_analisis(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📊 Analizando tus ingresos...")
    import sys; sys.path.insert(0, "/data/data/com.termux/files/home")
    from ia_precios import analizar_ingresos
    resultado = analizar_ingresos()
    await update.message.reply_text("📈 *Análisis de ingresos*\n─────────────────────\n" + resultado, parse_mode="Markdown")


async def cmd_presupuesto_ia(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(
            "Uso: /presupuesto cliente, descripcion del trabajo\n\n"
            "Ejemplo:\n/presupuesto Tito, cambio de tablero 12 bocas 3 tomas y 2 llaves"
        )
        return

    texto = " ".join(ctx.args)
    await update.message.reply_text("⚡ Calculando presupuesto...")

    import sys, json, re
    sys.path.insert(0, "/data/data/com.termux/files/home")

    # Leer precios del vault
    PRECIOS_MD = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/08_PRECIOS/Precios_Actualizados.md"
    TARIFAS_MO = {
        "Boca completa": 85935,
        "Visita tecnica": 43043,
        "Servicio minimo": 40000,
        "Hora de trabajo": 43043,
        "Tablero hasta 6 bocas": 253859,
        "Tablero 7-12 bocas": 320000,
        "Tablero 13-24 bocas": 420000,
        "Tablero +24 bocas": 550000,
        "Puesta a tierra": 128855,
        "Ventilador sin luz": 80000,
        "Ventilador con luz": 90000,
    }

    try:
        with open(PRECIOS_MD, encoding="utf-8") as f:
            precios_texto = f.read()
    except:
        precios_texto = ""

    import groq
    client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

    tarifas_texto = "\n".join([f"- {k}: ${v}" for k,v in TARIFAS_MO.items()])

    prompt = (
        "Sos el asistente de Dario, electricista en La Plata.\n"
        "Analizá el trabajo pedido y armá un presupuesto detallado.\n\n"
        "TARIFAS MANO DE OBRA:\n" + tarifas_texto + "\n\n"
        "LISTA DE PRECIOS MATERIALES (DistriElectro):\n" + precios_texto[:2000] + "\n\n"
        "TRABAJO PEDIDO: " + texto + "\n\n"
        "Respondé SOLO con JSON valido:\n"
        '{"cliente": "nombre", "descripcion": "resumen", '
        '"mano_de_obra": [{"item": "nombre", "cantidad": 1, "precio_unit": 0}], '
        '"materiales": [{"item": "nombre", "cantidad": 1, "precio_unit": 0}], '
        '"ganancia_pct": 30, "observaciones": "texto opcional"}'
    )

    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2, max_tokens=800,
        )
        respuesta = re.sub("```json|```", "", chat.choices[0].message.content.strip()).strip()
        data = json.loads(respuesta)
    except Exception as e:
        await update.message.reply_text("❌ Error: " + str(e))
        return

    # Calcular totales
    ganancia = data.get("ganancia_pct", 30) / 100
    total_mo = sum(int(i.get("cantidad",1)) * int(i.get("precio_unit",0)) for i in data.get("mano_de_obra",[]))
    total_mat = sum(int(i.get("cantidad",1)) * int(i.get("precio_unit",0) * (1+ganancia)) for i in data.get("materiales",[]))
    total = total_mo + total_mat

    # Armar mensaje WhatsApp
    cliente = data.get("cliente", "Cliente")
    desc = data.get("descripcion", texto)

    lineas_mo = "\n".join([
        f"  • {i.get('item')} x{i.get('cantidad',1)}: ${int(i.get('cantidad',1)*i.get('precio_unit',0)):,}".replace(",",".")
        for i in data.get("mano_de_obra",[]) if i.get("precio_unit",0) > 0
    ])
    lineas_mat = "\n".join([
        f"  • {i.get('item')} x{i.get('cantidad',1)}: ${int(i.get('cantidad',1)*i.get('precio_unit',0)*(1+ganancia)):,}".replace(",",".")
        for i in data.get("materiales",[]) if i.get("precio_unit",0) > 0
    ])

    msg_wa = (
        f"⚡ *Presupuesto Electrico*\n"
        f"*Dario Electricista — La Plata*\n"
        f"──────────────────────────\n"
        f"Hola *{cliente}*, te paso el detalle:\n\n"
        f"🔧 *Mano de obra:*\n{lineas_mo}\n\n"
        f"📦 *Materiales (+{int(ganancia*100)}% ganancia):*\n{lineas_mat}\n\n"
        f"──────────────────────────\n"
        f"💰 *TOTAL: ${total:,}*\n\n"
        f"✅ Válido por 48hs.".replace(",",".")
    )

    if data.get("observaciones"):
        msg_wa += f"\n📝 {data.get('observaciones')}"

    await update.message.reply_text(msg_wa, parse_mode="Markdown")

    # Copiar al portapapeles via notificar
    try:
        import subprocess
        p = subprocess.Popen(["termux-clipboard-set"], stdin=subprocess.PIPE)
        p.communicate(input=msg_wa.encode("utf-8"))
        await update.message.reply_text("📋 Copiado al portapapeles — listo para WhatsApp")
    except:
        pass


async def cmd_mensaje(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(
            "Uso: /mensaje instruccion\n\n"
            "Ejemplos:\n"
            "/mensaje escribile a Tito recordandole que debe 150000, tono amigable\n"
            "/mensaje avisale a Maria Rosa que el trabajo esta listo\n"
            "/mensaje cobrale a Guillermo el trabajo de enero, tono firme"
        )
        return

    instruccion = " ".join(ctx.args)
    await update.message.reply_text("✍️ Redactando mensaje...")

    import groq, re, subprocess
    client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = (
        "Sos Dario, electricista en La Plata. Escribis el mensaje vos mismo, en primera persona.\n"
        "Nunca digas que sos un asistente ni que Dario te mando. Habla como si fueras Dario.\n"
        "Español argentino, breve, claro. Sin markdown ni asteriscos. Solo texto plano.\n"
        "No agregues explicaciones, solo el mensaje listo para enviar.\n\n"
        "INSTRUCCION: " + instruccion
    )

    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=300,
        )
        mensaje = chat.choices[0].message.content.strip()
    except Exception as e:
        await update.message.reply_text("❌ Error: " + str(e))
        return

    await update.message.reply_text(
        "📱 *Mensaje listo para WhatsApp:*\n"
        "─────────────────────\n" + mensaje,
        parse_mode="Markdown"
    )

    try:
        p = subprocess.Popen(["termux-clipboard-set"], stdin=subprocess.PIPE)
        p.communicate(input=mensaje.encode("utf-8"))
        await update.message.reply_text("📋 Copiado al portapapeles")
    except:
        pass


async def cmd_materiales(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(
            "Uso: /materiales descripcion del trabajo\n\n"
            "Ejemplo:\n/materiales instalar 4 tomas y 2 llaves en living"
        )
        return

    descripcion = " ".join(ctx.args)
    await update.message.reply_text("📦 Calculando materiales...")

    import groq, re, json, os
    api_key = os.getenv("GROQ_API_KEY")
    client = groq.Groq(api_key=api_key)

    PRECIOS_MD = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/08_PRECIOS/Precios_Actualizados.md"
    try:
        with open(PRECIOS_MD, encoding="utf-8") as f:
            precios_texto = f.read()[:3000]
    except:
        precios_texto = ""

    prompt = (
        "Sos un electricista experto en La Plata, Argentina.\n"
        "Arma la lista de materiales necesarios para el trabajo descrito.\n"
        "Usá los precios de la lista cuando estén disponibles.\n\n"
        "LISTA DE PRECIOS DISPONIBLES:\n" + precios_texto + "\n\n"
        "TRABAJO: " + descripcion + "\n\n"
        "Respondé SOLO con JSON valido:\n"
        '{"materiales": [{"item": "nombre", "cantidad": 1, "unidad": "u/m/kg", "precio_unit": 0, "nota": "opcional"}], '
        '"observaciones": "consejos o advertencias del trabajo"}'
    )

    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2, max_tokens=600,
        )
        respuesta = re.sub("```json|```", "", chat.choices[0].message.content.strip()).strip()
        data = json.loads(respuesta)
    except Exception as e:
        await update.message.reply_text("❌ Error: " + str(e))
        return

    materiales = data.get("materiales", [])
    total = sum(int(m.get("cantidad",1)) * int(m.get("precio_unit",0)) for m in materiales)

    lineas = [f"📦 *Lista de materiales*\n_{descripcion}_\n─────────────────────"]
    for m in materiales:
        cant = m.get("cantidad", 1)
        precio = int(m.get("precio_unit", 0))
        subtotal = cant * precio
        linea = f"• {m.get('item')} x{cant} {m.get('unidad','u')}"
        if precio > 0:
            linea += f" — ${subtotal:,}".replace(",",".")
        if m.get("nota"):
            linea += f"\n  _{m.get('nota')}_"
        lineas.append(linea)

    if total > 0:
        lineas.append(f"─────────────────────\n💵 Total materiales: *${total:,}*".replace(",","."))

    if data.get("observaciones"):
        lineas.append(f"\n⚠️ {data.get('observaciones')}")

    await update.message.reply_text("\n".join(lineas), parse_mode="Markdown")


async def cmd_buscar(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(
            "Uso: /buscar consulta\n\n"
            "Ejemplos:\n"
            "/buscar trabajos de tablero\n"
            "/buscar clientes que no pagaron\n"
            "/buscar problemas con termicas"
        )
        return

    consulta = " ".join(ctx.args)
    await update.message.reply_text("🔍 Buscando en tus notas...")

    import groq, re, json, os
    TRABAJOS = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/01_TRABAJOS"
    DIARIO = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/05_DIARIO"

    # Leer todos los trabajos
    notas = []
    for root, dirs, files in os.walk(TRABAJOS):
        dirs[:] = [d for d in dirs if d != "fotos"]
        for f in files:
            if not f.endswith(".md"): continue
            try:
                with open(os.path.join(root, f), encoding="utf-8") as fh:
                    texto = fh.read()
                notas.append({"archivo": f.replace(".md",""), "contenido": texto[:500]})
            except: pass

    # Leer ultimas notas del diario
    diario = []
    try:
        for f in sorted(os.listdir(DIARIO))[-7:]:
            if f.endswith(".md"):
                with open(os.path.join(DIARIO, f), encoding="utf-8") as fh:
                    diario.append(fh.read()[:300])
    except: pass

    notas_texto = "\n---\n".join([
        f"TRABAJO: {n['archivo']}\n{n['contenido']}" for n in notas[:20]
    ])
    diario_texto = "\n---\n".join(diario)

    api_key = os.getenv("GROQ_API_KEY")
    client = groq.Groq(api_key=api_key)

    prompt = (
        "Sos el asistente de Dario, electricista en La Plata.\n"
        "Busca en sus notas y responde la consulta de forma util y concreta.\n\n"
        "TRABAJOS REGISTRADOS:\n" + notas_texto + "\n\n"
        "DIARIO RECIENTE:\n" + diario_texto + "\n\n"
        "CONSULTA: " + consulta + "\n\n"
        "Responde en español argentino, maximo 10 lineas, directo y util.\n"
        "Si encontras trabajos relevantes, mencionalos con cliente y fecha."
    )

    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, max_tokens=500,
        )
        respuesta = chat.choices[0].message.content.strip()
    except Exception as e:
        await update.message.reply_text("❌ Error: " + str(e))
        return

    await update.message.reply_text(
        f"🔍 *Resultados para:* _{consulta}_\n─────────────────────\n{respuesta}",
        parse_mode="Markdown"
    )


async def cmd_clientes_ia(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👥 Analizando tus clientes...")

    import groq, os, re
    from datetime import date

    trabajos = get_trabajos()
    if not trabajos:
        await update.message.reply_text("No hay trabajos registrados.")
        return

    # Agrupar por cliente
    por_cliente = {}
    for t in trabajos:
        cliente = t.get("cliente","?")
        if cliente not in por_cliente:
            por_cliente[cliente] = {"trabajos": 0, "total": 0, "cobrado": 0, "fechas": []}
        por_cliente[cliente]["trabajos"] += 1
        monto = int(t.get("mano_de_obra", 0))
        por_cliente[cliente]["total"] += monto
        if t.get("pagado") == "true":
            por_cliente[cliente]["cobrado"] += monto
        if t.get("fecha"):
            por_cliente[cliente]["fechas"].append(t.get("fecha"))

    # Ordenar por total
    ranking = sorted(por_cliente.items(), key=lambda x: x[1]["total"], reverse=True)

    resumen = "\n".join([
        f"{c}: {d['trabajos']} trabajos, ${d['total']} facturado, ${d['cobrado']} cobrado"
        for c, d in ranking[:15]
    ])

    api_key = os.getenv("GROQ_API_KEY")
    client = groq.Groq(api_key=api_key)

    prompt = (
        "Sos el asistente de Dario, electricista en La Plata.\n"
        "Analiza sus clientes y da un informe util.\n\n"
        "DATOS POR CLIENTE:\n" + resumen + "\n\n"
        "Responde en español argentino con:\n"
        "1. Top 3 mejores clientes\n"
        "2. Clientes que deben plata\n"
        "3. Clientes mas frecuentes\n"
        "4. Consejo concreto para el negocio\n"
        "Maximo 12 lineas, directo y util."
    )

    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, max_tokens=500,
        )
        respuesta = chat.choices[0].message.content.strip()
    except Exception as e:
        await update.message.reply_text("❌ Error: " + str(e))
        return

    # Top clientes como tabla
    top = ranking[:5]
    lineas = ["👥 *Análisis de clientes*\n─────────────────────"]
    for c, d in top:
        pagado_pct = int(d["cobrado"]/d["total"]*100) if d["total"] > 0 else 0
        emoji = "⭐" if pagado_pct == 100 else "⚠️" if pagado_pct == 0 else "🔶"
        lineas.append(f"{emoji} *{c}*: {d['trabajos']} trabajos — {fmt_pesos(d['total'])}")

    lineas.append("─────────────────────\n" + respuesta)
    await update.message.reply_text("\n".join(lineas), parse_mode="Markdown")


async def cmd_prediccion(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔮 Analizando tendencias...")

    import groq, os
    from datetime import date, timedelta

    trabajos = get_trabajos()
    if not trabajos:
        await update.message.reply_text("No hay trabajos registrados.")
        return

    # Agrupar por mes
    por_mes = {}
    for t in trabajos:
        mes = t.get("fecha","")[:7]
        if not mes: continue
        if mes not in por_mes:
            por_mes[mes] = {"total": 0, "cantidad": 0, "cobrado": 0}
        monto = int(t.get("mano_de_obra", 0))
        por_mes[mes]["total"] += monto
        por_mes[mes]["cantidad"] += 1
        if t.get("pagado") == "true":
            por_mes[mes]["cobrado"] += monto

    # Mes actual y siguiente
    hoy = date.today()
    mes_actual = hoy.strftime("%Y-%m")
    mes_siguiente = (hoy.replace(day=1) + timedelta(days=32)).strftime("%Y-%m")
    dias_transcurridos = hoy.day
    import calendar
    dias_mes = calendar.monthrange(hoy.year, hoy.month)[1]

    resumen = "\n".join([
        f"{mes}: {d['cantidad']} trabajos, ${d['total']}, cobrado ${d['cobrado']}"
        for mes, d in sorted(por_mes.items())
    ])

    # Proyeccion simple del mes actual
    total_actual = por_mes.get(mes_actual, {}).get("total", 0)
    proyeccion_mes = int(total_actual * dias_mes / dias_transcurridos) if dias_transcurridos > 0 else 0

    api_key = os.getenv("GROQ_API_KEY")
    client = groq.Groq(api_key=api_key)

    prompt = (
        "Sos el asistente financiero de Dario, electricista en La Plata.\n"
        "Analiza su historial y predice sus ingresos futuros.\n\n"
        "HISTORIAL POR MES:\n" + resumen + "\n\n"
        f"Hoy es {hoy.strftime('%d/%m/%Y')}, dia {dias_transcurridos} de {dias_mes}.\n"
        f"Lo que lleva este mes ({mes_actual}): ${total_actual}\n"
        f"Proyeccion lineal del mes actual: ${proyeccion_mes}\n\n"
        "Responde en español argentino con:\n"
        f"1. Estimacion de cierre de {mes_actual}\n"
        f"2. Prediccion para {mes_siguiente}\n"
        "3. Tendencia general\n"
        "4. Consejo para mejorar ingresos\n"
        "Maximo 10 lineas, directo y concreto."
    )

    try:
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, max_tokens=400,
        )
        respuesta = chat.choices[0].message.content.strip()
    except Exception as e:
        await update.message.reply_text("❌ Error: " + str(e))
        return

    msg = (
        f"🔮 Prediccion de ingresos\n"
        f"─────────────────────\n"
        f"Este mes llevas: {fmt_pesos(total_actual)}\n"
        f"Proyeccion al cierre: {fmt_pesos(proyeccion_mes)}\n"
        f"─────────────────────\n"
        f"{respuesta}"
    )

    await update.message.reply_text(msg)


async def cmd_recibo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(
            "Uso: /recibo cliente, descripcion, monto\n\n"
            "Ejemplo:\n/recibo Tito, instalacion de tablero 12 bocas, 320000"
        )
        return

    texto = " ".join(ctx.args)
    partes = [p.strip() for p in texto.split(",")]
    if len(partes) < 3:
        await update.message.reply_text("Faltan datos. Usá: /recibo cliente, descripcion, monto")
        return

    cliente = partes[0]
    descripcion = partes[1]
    try:
        monto = int(partes[2].replace(".","").replace("$",""))
    except:
        monto = 0

    await update.message.reply_text("📄 Generando recibo...")

    import os
    from datetime import date
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm

    fecha = date.today().strftime("%d/%m/%Y")
    numero = date.today().strftime("%Y%m%d") + str(abs(hash(cliente)))[-4:]
    output = f"/data/data/com.termux/files/home/recibo_{cliente.replace(' ','_')}_{date.today().strftime('%Y%m%d')}.pdf"

    doc = SimpleDocTemplate(output, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    elementos = []

    # Header
    estilo_titulo = ParagraphStyle("titulo", fontSize=20, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1a1a2e"), spaceAfter=5)
    estilo_sub = ParagraphStyle("sub", fontSize=11, fontName="Helvetica",
        textColor=colors.HexColor("#444444"), spaceAfter=3)
    estilo_normal = ParagraphStyle("normal", fontSize=10, fontName="Helvetica",
        textColor=colors.HexColor("#333333"))

    elementos.append(Paragraph("⚡ DARIO ELECTRICISTA", estilo_titulo))
    elementos.append(Paragraph("La Plata, Buenos Aires", estilo_sub))
    elementos.append(Paragraph("Matrícula AAIERIC", estilo_sub))
    elementos.append(Spacer(1, 0.5*cm))

    # Linea divisoria
    tabla_linea = Table([[""]],colWidths=[17*cm])
    tabla_linea.setStyle(TableStyle([
        ("LINEABOVE", (0,0), (-1,0), 2, colors.HexColor("#f0a500")),
    ]))
    elementos.append(tabla_linea)
    elementos.append(Spacer(1, 0.5*cm))

    # Datos del recibo
    datos = [
        ["RECIBO DE PAGO", ""],
        ["N°:", numero],
        ["Fecha:", fecha],
        ["Cliente:", cliente],
    ]
    tabla_datos = Table(datos, colWidths=[4*cm, 13*cm])
    tabla_datos.setStyle(TableStyle([
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("FONTSIZE", (0,0), (-1,0), 14),
        ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor("#1a1a2e")),
        ("SPAN", (0,0), (-1,0)),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    elementos.append(tabla_datos)
    elementos.append(Spacer(1, 0.5*cm))

    # Detalle
    detalle = [
        ["Descripcion", "Monto"],
        [descripcion, f"$ {monto:,}".replace(",",".")],
        ["", ""],
        ["TOTAL", f"$ {monto:,}".replace(",",".")],
    ]
    tabla_detalle = Table(detalle, colWidths=[12*cm, 5*cm])
    tabla_detalle.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("FONTSIZE", (0,-1), (-1,-1), 12),
        ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#f0a500")),
        ("TEXTCOLOR", (0,-1), (-1,-1), colors.white),
        ("ALIGN", (1,0), (1,-1), "RIGHT"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#dddddd")),
        ("ROWBACKGROUNDS", (0,1), (-1,-2), [colors.white, colors.HexColor("#f9f9f9")]),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    elementos.append(tabla_detalle)
    elementos.append(Spacer(1, 1*cm))

    # Firma
    elementos.append(Paragraph("_______________________________", estilo_normal))
    elementos.append(Paragraph("Dario — Electricista Matriculado", estilo_normal))
    elementos.append(Spacer(1, 0.3*cm))
    elementos.append(Paragraph("Gracias por confiar en nuestro servicio ⚡", estilo_sub))

    doc.build(elementos)

    # Enviar PDF por Telegram
    with open(output, "rb") as pdf:
        await update.message.reply_document(
            document=pdf,
            filename=f"Recibo_{cliente}_{fecha.replace('/','_')}.pdf",
            caption=f"📄 Recibo para {cliente} — ${monto:,}\nFecha: {fecha}".replace(",",".")
        )

    os.remove(output)


async def cmd_llegar(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(
            "Uso: /llegar nombre del cliente\n\n"
            "Ejemplo:\n/llegar Tito\n/llegar Silvia vecina"
        )
        return

    busqueda = " ".join(ctx.args).lower()
    CLIENTES = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/02_CLIENTES"
    TRABAJOS = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/01_TRABAJOS"

    import os, re, urllib.parse

    # Buscar direccion en ficha de cliente
    direccion = None
    cliente_nombre = None

    for f in os.listdir(CLIENTES):
        if busqueda in f.lower() and f.endswith(".md"):
            cliente_nombre = f.replace("Cliente ","").replace(".md","")
            with open(os.path.join(CLIENTES, f), encoding="utf-8") as fh:
                texto = fh.read()
            m = re.search(r"direccion[:\s]+(.+)", texto, re.IGNORECASE)
            if m:
                direccion = m.group(1).strip().strip('"')
            break

    # Si no tiene en ficha, buscar en trabajos
    if not direccion:
        for root, dirs, files in os.walk(TRABAJOS):
            for f in files:
                if busqueda in f.lower() and f.endswith(".md"):
                    with open(os.path.join(root, f), encoding="utf-8") as fh:
                        texto = fh.read()
                    m = re.search(r"direcci[oó]n?[:\s]+(.+)", texto, re.IGNORECASE)
                    if m:
                        direccion = m.group(1).strip().strip('"')
                        if not cliente_nombre:
                            cliente_nombre = busqueda
                        break
            if direccion:
                break

    if not direccion:
        await update.message.reply_text(
            f"No encontré dirección para *{busqueda}*\n\n"
            "Agregá el campo en la ficha:\n`direccion: Calle 123 y 45, La Plata`",
            parse_mode="Markdown"
        )
        return

    # Generar links
    dir_encoded = urllib.parse.quote(direccion + ", La Plata, Buenos Aires")
    link_gmaps = f"https://www.google.com/maps/search/?api=1&query={dir_encoded}"
    link_osmand = f"https://osmand.net/go?q={dir_encoded}"
    link_waze = f"https://waze.com/ul?q={dir_encoded}"

    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗺 Google Maps", url=link_gmaps)],
        [InlineKeyboardButton("🧭 OsmAnd", url=link_osmand)],
        [InlineKeyboardButton("🚗 Waze", url=link_waze)],
    ])

    await update.message.reply_text(
        f"📍 *{cliente_nombre}*\n`{direccion}`",
        parse_mode="Markdown",
        reply_markup=keyboard
    )


async def cmd_mapa(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🗺 Generando mapa de clientes...")

    import os, re, urllib.parse, requests

    CLIENTES = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/02_CLIENTES"
    TRABAJOS = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault/01_TRABAJOS"

    # Recolectar clientes con direccion
    clientes = {}

    # Desde fichas de clientes
    for f in os.listdir(CLIENTES):
        if not f.endswith(".md"): continue
        nombre = f.replace("Cliente ","").replace(".md","")
        with open(os.path.join(CLIENTES, f), encoding="utf-8") as fh:
            texto = fh.read()
        m = re.search(r"direccion:\s*(.+)", texto, re.IGNORECASE)
        if m:
            dir_raw = m.group(1).strip().strip('"')
            if dir_raw and len(dir_raw) > 3:
                clientes[nombre] = dir_raw

    # Desde trabajos (si no esta en clientes)
    for root, dirs, files in os.walk(TRABAJOS):
        for f in files:
            if not f.endswith(".md"): continue
            with open(os.path.join(root, f), encoding="utf-8") as fh:
                texto = fh.read()
            m_cli = re.search(r"cliente:\s*([^\n]+)", texto, re.MULTILINE)
            m_dir = re.search(r"direcci[oó]n?:\s*(.+)", texto, re.IGNORECASE)
            if m_cli and m_dir:
                nombre = m_cli.group(1).strip()
                direccion = m_dir.group(1).strip().strip('"')
                if nombre not in clientes and direccion and len(direccion) > 3:
                    clientes[nombre] = direccion

    if not clientes:
        await update.message.reply_text("No hay clientes con direccion registrada.")
        return

    # Geocodificar con Nominatim (OpenStreetMap, gratis)
    puntos = []
    for nombre, direccion in clientes.items():
        try:
            query = direccion + ", La Plata, Buenos Aires, Argentina"
            r = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": query, "format": "json", "limit": 1},
                headers={"User-Agent": "DarioElectricistaPro/1.0"},
                timeout=5
            )
            data = r.json()
            if data:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                puntos.append((nombre, direccion, lat, lon))
        except:
            pass

    if not puntos:
        await update.message.reply_text("No pude geocodificar las direcciones. Verifica conexion a internet.")
        return

    # Generar KML
    kml_items = ""
    for nombre, direccion, lat, lon in puntos:
        kml_items += f"""
    <Placemark>
      <name>{nombre}</name>
      <description>{direccion}</description>
      <Point><coordinates>{lon},{lat},0</coordinates></Point>
    </Placemark>"""

    kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
  <name>Clientes Dario Electricista</name>
  <Style id="cliente">
    <IconStyle><Icon><href>http://maps.google.com/mapfiles/ms/icons/yellow-dot.png</href></Icon></IconStyle>
  </Style>
{kml_items}
</Document>
</kml>"""

    output = "/data/data/com.termux/files/home/clientes_mapa.kml"
    with open(output, "w", encoding="utf-8") as f:
        f.write(kml)

    # Enviar archivo
    with open(output, "rb") as f:
        await update.message.reply_document(
            document=f,
            filename="clientes_dario.kml",
            caption=f"🗺 *Mapa de clientes*\n{len(puntos)} ubicaciones encontradas\n\nAbrilo con Google Maps u OsmAnd",
            parse_mode="Markdown"
        )

    os.remove(output)

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
    app.add_handler(CommandHandler("vencidos", cmd_vencidos))
    app.add_handler(CommandHandler("catalogo", cmd_catalogo))
    app.add_handler(CommandHandler("cliente", cmd_cliente))
    app.add_handler(CommandHandler("mes", cmd_mes))
    app.add_handler(CommandHandler("agenda", cmd_agenda))
    app.add_handler(CommandHandler("precio", cmd_precio))
    app.add_handler(CommandHandler("analisis", cmd_analisis))
    app.add_handler(CommandHandler("presupuesto", cmd_presupuesto_ia))
    app.add_handler(CommandHandler("mensaje", cmd_mensaje))
    app.add_handler(CommandHandler("materiales", cmd_materiales))
    app.add_handler(CommandHandler("buscar", cmd_buscar))
    app.add_handler(CommandHandler("clientes_ia", cmd_clientes_ia))
    app.add_handler(CommandHandler("prediccion", cmd_prediccion))
    app.add_handler(CommandHandler("recibo", cmd_recibo))
    app.add_handler(CommandHandler("llegar", cmd_llegar))
    app.add_handler(CommandHandler("mapa", cmd_mapa))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cmd_natural))
    print("Bot iniciado. Esperando comandos...")
    log_evento("Bot iniciado")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
