#!/usr/bin/env python3
import os, re, logging
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
    client = groq.Groq(api_key="os.getenv("GROQ_API_KEY")")

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
    client = groq.Groq(api_key="os.getenv("GROQ_API_KEY")")

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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cmd_natural))
    print("Bot iniciado. Esperando comandos...")
    log_evento("Bot iniciado")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
