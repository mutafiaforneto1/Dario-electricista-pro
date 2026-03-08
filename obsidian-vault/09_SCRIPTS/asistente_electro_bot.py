#!/usr/bin/env python3
import os, re, glob
from datetime import date
from pathlib import Path
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)

TOKEN   = "8785612653:AAHGs7ik8gJWHI2wo-lo2p--U7tgjjpePJw"
CHAT_ID = 922023252
VAULT   = "/storage/emulated/0/Documents/Obsidian trabajo optimizado 2"
TRABAJOS_DIR = f"{VAULT}/01_TRABAJOS"
PRECIOS_MD   = f"{VAULT}/08_PRECIOS/Lista de Precios DistriElectro.md"

ESPERANDO_ITEM=1; ESPERANDO_MO=2; ESPERANDO_NOMBRE=3
COBRAR_ELEGIR=10; CERRAR_ELEGIR=11
NUEVO_CLIENTE=20; NUEVO_DIR=21; NUEVO_DESC=22; NUEVO_MONTO=23

def leer_frontmatter(archivo):
    datos = {}
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
        match = re.match(r'^---\n(.*?)\n---', contenido, re.DOTALL)
        if not match:
            return datos
        for linea in match.group(1).split("\n"):
            if ":" in linea:
                clave, _, valor = linea.partition(":")
                datos[clave.strip()] = valor.strip().strip('"').strip("'")
    except:
        pass
    return datos

def actualizar_campo(archivo, campo, valor):
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
        nuevo = re.sub(rf"^{campo}:.*$", f"{campo}: {valor}", contenido, flags=re.MULTILINE)
        if nuevo == contenido:
            nuevo = contenido.replace("---\n", f"---\n{campo}: {valor}\n", 1)
        with open(archivo, "w", encoding="utf-8") as f:
            f.write(nuevo)
        return True
    except:
        return False

def listar_trabajos(filtro=None):
    trabajos = []
    for archivo in sorted(glob.glob(f"{TRABAJOS_DIR}/**/*.md", recursive=True)):
        datos = leer_frontmatter(archivo)
        if not datos or datos.get("tipo") != "trabajo":
            continue
        estado = datos.get("estado", "").lower()
        pagado = datos.get("pagado", "false").lower()
        if filtro == "deuda":
            if estado != "terminado" or pagado == "true":
                continue
        elif filtro == "activos":
            if estado not in ["pendiente", "en_curso"]:
                continue
        else:
            if estado == "terminado" and pagado == "true":
                continue
        datos["_archivo"] = archivo
        datos["_nombre"] = Path(archivo).stem
        trabajos.append(datos)
    return trabajos

def cargar_precios():
    precios = {}
    dolar_blue = None
    try:
        with open(PRECIOS_MD, "r", encoding="utf-8") as f:
            contenido = f.read()
        m = re.search(r'dolar_blue:\s*([\d.,]+)', contenido)
        if m:
            dolar_blue = m.group(1)
        for linea in contenido.split("\n"):
            if "|" not in linea:
                continue
            partes = [p.strip() for p in linea.split("|") if p.strip()]
            if len(partes) < 2:
                continue
            nombre = partes[0].lower()
            if nombre in ["material", "materiales", "---", ":---"] or "---" in nombre:
                continue
            for parte in partes[1:]:
                limpio = re.sub(r'[~$\s]', '', parte).replace(".", "").replace(",", "")
                if limpio.isdigit() and int(limpio) > 100:
                    precios[nombre] = int(limpio)
                    break
    except:
        pass
    return precios, dolar_blue

def buscar_material(query, precios):
    query = query.lower().strip()
    resultado = [(n, p) for n, p in precios.items() if query in n]
    resultado.sort(key=lambda x: (0 if x[0].startswith(query) else 1, len(x[0])))
    return resultado[:6]

def parsear_items(texto, precios):
    items = []
    errores = []
    for parte in re.split(r'[,;]', texto):
        parte = parte.strip()
        if not parte:
            continue
        cantidad = 1
        unidad = "u"
        mm = re.search(r'(\d+(?:\.\d+)?)\s*m(?:etros?)?\b', parte, re.I)
        mx = re.search(r'[xX]\s*(\d+)\s*$', parte)
        if mm:
            cantidad = float(mm.group(1))
            unidad = "m"
            parte = parte[:mm.start()].strip()
        elif mx:
            cantidad = int(mx.group(1))
            parte = parte[:mx.start()].strip()
        res = buscar_material(parte, precios)
        if not res:
            errores.append(parte)
            continue
        nombre, precio_base = res[0]
        if unidad == "m" and "100m" in nombre:
            precio_unit = precio_base / 100
        elif unidad == "m" and "25m" in nombre:
            precio_unit = precio_base / 25
        else:
            precio_unit = precio_base
        items.append({
            "nombre": nombre, "cantidad": cantidad, "unidad": unidad,
            "precio_unit": precio_unit, "subtotal": precio_unit * cantidad
        })
    return items, errores

def fmt(n):
    return f"${n:,.0f}".replace(",", ".")

def hacer_presupuesto(items, mo, cliente=""):
    sub = sum(i["subtotal"] for i in items)
    total = sub + mo
    L = ["⚡ *PRESUPUESTO ELÉCTRICO*"]
    if cliente:
        L.append(f"👤 {cliente}")
    L.append("─" * 26)
    for i in items:
        n = i["nombre"][:28].title()
        if i["unidad"] == "m":
            L.append(f"• {n}\n  {i['cantidad']:.0f}m × {fmt(i['precio_unit'])}/m = {fmt(i['subtotal'])}")
        elif i["cantidad"] > 1:
            L.append(f"• {n}\n  {int(i['cantidad'])} × {fmt(i['precio_unit'])} = {fmt(i['subtotal'])}")
        else:
            L.append(f"• {n}: {fmt(i['subtotal'])}")
    L += ["─" * 26, f"📦 *Materiales:* {fmt(sub)}",
          f"🔧 *Mano de obra:* {fmt(mo)}", f"💰 *TOTAL: {fmt(total)}*"]
    return "\n".join(L), sub, total

async def cmd_ayuda(update, context):
    await update.message.reply_text(
        "⚡ *ASISTENTE ELECTRICO*\n\n"
        "*NEGOCIO*\n/resumen /trabajos /deuda\n/cobrar /cerrar /nuevo\n\n"
        "*PRESUPUESTOS*\n/presupuesto [items]\n/calcular\n/precio [material]\n/materiales\n\n"
        "/cancelar — cancelar acción", parse_mode="Markdown")

async def cmd_resumen(update, context):
    activos = listar_trabajos("activos")
    deuda = listar_trabajos("deuda")
    total_deuda = 0
    for t in deuda:
        try:
            total_deuda += float(re.sub(r'[^\d.]', '', t.get("mano_de_obra", "0")))
        except:
            pass
    hoy = date.today().isoformat()
    hoy_t = [t for t in activos if t.get("fecha", "") == hoy]
    L = [f"📊 *RESUMEN — {hoy}*", "",
         f"🔄 Activos: *{len(activos)}*",
         f"💸 En la calle: *{fmt(total_deuda)}* ({len(deuda)})"]
    if hoy_t:
        L.append("\n📌 *HOY:*")
        for t in hoy_t:
            L.append(f"  • {t.get('cliente', t['_nombre'])} — {t.get('dirección', '')}")
    if activos:
        L.append("\n🔄 *PENDIENTES:*")
        for t in activos[:5]:
            ic = "🔵" if t.get("estado") == "en_curso" else "🟡"
            L.append(f"  {ic} {t.get('cliente', t['_nombre'])}")
    await update.message.reply_text("\n".join(L), parse_mode="Markdown")

async def cmd_deuda(update, context):
    deuda = listar_trabajos("deuda")
    if not deuda:
        await update.message.reply_text("✅ Todo cobrado.")
        return
    total = 0
    L = ["💸 *DINERO EN LA CALLE*\n"]
    for t in deuda:
        c = t.get("cliente", t["_nombre"]).replace("[[Cliente - ", "").replace("]]", "")
        try:
            m = float(re.sub(r'[^\d.]', '', t.get("mano_de_obra", "0")))
        except:
            m = 0
        total += m
        L.append(f"• *{c}*\n  {fmt(m)} — {t.get('fecha', '')}")
    L.append(f"\n💰 *Total: {fmt(total)}*")
    await update.message.reply_text("\n".join(L), parse_mode="Markdown")

async def cmd_trabajos(update, context):
    trabajos = listar_trabajos("activos")
    if not trabajos:
        await update.message.reply_text("No hay trabajos activos.")
        return
    L = [f"🔄 *ACTIVOS ({len(trabajos)})*\n"]
    for i, t in enumerate(trabajos, 1):
        c = t.get("cliente", t["_nombre"]).replace("[[Cliente - ", "").replace("]]", "")
        ic = "🔵" if t.get("estado") == "en_curso" else "🟡"
        try:
            m = fmt(float(re.sub(r'[^\d.]', '', t.get("mano_de_obra", "0"))))
        except:
            m = "—"
        L.append(f"{i}. {ic} *{c}*\n   📍 {t.get('dirección', '')}\n   🗓 {t.get('fecha', '')} | 💰 {m}")
    await update.message.reply_text("\n".join(L), parse_mode="Markdown")

async def cmd_cobrar(update, context):
    deuda = listar_trabajos("deuda")
    if not deuda:
        await update.message.reply_text("✅ Nada pendiente de cobro.")
        return ConversationHandler.END
    context.user_data["lista_cobrar"] = deuda
    L = ["💸 *¿Cuál cobraste?*\n"]
    for i, t in enumerate(deuda, 1):
        c = t.get("cliente", t["_nombre"]).replace("[[Cliente - ", "").replace("]]", "")
        try:
            m = fmt(float(re.sub(r'[^\d.]', '', t.get("mano_de_obra", "0"))))
        except:
            m = "?"
        L.append(f"{i}. {c} — {m}")
    L.append("\nRespondé con el número.")
    await update.message.reply_text("\n".join(L), parse_mode="Markdown")
    return COBRAR_ELEGIR

async def cobrar_elegir(update, context):
    lista = context.user_data.get("lista_cobrar", [])
    try:
        t = lista[int(update.message.text.strip()) - 1]
    except:
        await update.message.reply_text("Número inválido.")
        return COBRAR_ELEGIR
    c = t.get("cliente", t["_nombre"]).replace("[[Cliente - ", "").replace("]]", "")
    actualizar_campo(t["_archivo"], "pagado", "true")
    await update.message.reply_text(f"✅ *{c}* marcado como cobrado.", parse_mode="Markdown")
    context.user_data.clear()
    return ConversationHandler.END

async def cmd_cerrar(update, context):
    activos = listar_trabajos("activos")
    if not activos:
        await update.message.reply_text("No hay activos.")
        return ConversationHandler.END
    context.user_data["lista_cerrar"] = activos
    L = ["✅ *¿Cuál terminaste?*\n"]
    for i, t in enumerate(activos, 1):
        c = t.get("cliente", t["_nombre"]).replace("[[Cliente - ", "").replace("]]", "")
        L.append(f"{i}. {c}")
    L.append("\nRespondé con el número.")
    await update.message.reply_text("\n".join(L), parse_mode="Markdown")
    return CERRAR_ELEGIR

async def cerrar_elegir(update, context):
    lista = context.user_data.get("lista_cerrar", [])
    try:
        t = lista[int(update.message.text.strip()) - 1]
    except:
        await update.message.reply_text("Número inválido.")
        return CERRAR_ELEGIR
    c = t.get("cliente", t["_nombre"]).replace("[[Cliente - ", "").replace("]]", "")
    actualizar_campo(t["_archivo"], "estado", "terminado")
    actualizar_campo(t["_archivo"], "fecha_cierre", date.today().isoformat())
    await update.message.reply_text(
        f"✅ *{c}* cerrado.\nUsá /cobrar para marcarlo pagado.", parse_mode="Markdown")
    context.user_data.clear()
    return ConversationHandler.END

async def cmd_nuevo(update, context):
    await update.message.reply_text("📝 *Nuevo trabajo*\n\n¿Para qué cliente?", parse_mode="Markdown")
    return NUEVO_CLIENTE

async def nuevo_cliente(update, context):
    context.user_data["nc"] = update.message.text.strip()
    await update.message.reply_text("📍 ¿Dirección?")
    return NUEVO_DIR

async def nuevo_dir(update, context):
    context.user_data["nd"] = update.message.text.strip()
    await update.message.reply_text("🔧 ¿Qué trabajo es?")
    return NUEVO_DESC

async def nuevo_desc(update, context):
    context.user_data["ndesc"] = update.message.text.strip()
    await update.message.reply_text("💰 ¿Monto mano de obra? (0 si no sabés)")
    return NUEVO_MONTO

async def nuevo_monto(update, context):
    try:
        monto = int(re.sub(r'[^\d]', '', update.message.text.strip()))
    except:
        monto = 0
    cliente = context.user_data.get("nc", "Cliente")
    dire = context.user_data.get("nd", "")
    desc = context.user_data.get("ndesc", "Trabajo")
    hoy = date.today().isoformat()
    carpeta = f"{TRABAJOS_DIR}/{cliente}"
    os.makedirs(carpeta, exist_ok=True)
    nombre = re.sub(r'[^\w\s-]', '', desc)[:25].strip().replace(" ", "_")
    ruta = f"{carpeta}/{nombre}-{hoy}.md"
    contenido = f"""---
tipo: trabajo
cliente: "[[Cliente - {cliente}]]"
dirección: {dire}
prioridad: media
fecha: {hoy}
estado: pendiente
mano_de_obra: {monto}
costo_materiales: 0
pagado: false
---

# {desc}

## Tareas
- [ ] 

## Notas

"""
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
        await update.message.reply_text(
            f"✅ *Trabajo creado*\n👤 {cliente}\n📍 {dire}\n🔧 {desc}\n💰 {fmt(monto)}",
            parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")
    context.user_data.clear()
    return ConversationHandler.END

async def cmd_presupuesto(update, context):
    if not context.args:
        await update.message.reply_text(
            "Uso: `/presupuesto cable 15m, termica 20A x2`\nO usá /calcular",
            parse_mode="Markdown")
        return
    precios, _ = cargar_precios()
    items, errores = parsear_items(" ".join(context.args), precios)
    if errores:
        await update.message.reply_text(f"⚠️ No encontré: {', '.join(errores)}")
    if not items:
        await update.message.reply_text("No encontré materiales. Usá /materiales.")
        return
    context.user_data["items"] = items
    context.user_data["modo"] = "rapido"
    sub = sum(i["subtotal"] for i in items)
    res = "\n".join(f"• {i['nombre'][:25].title()}: {fmt(i['subtotal'])}" for i in items)
    await update.message.reply_text(
        f"✅ Materiales:\n{res}\n\n📦 Subtotal: *{fmt(sub)}*\n\n¿Mano de obra? (0 si solo materiales)",
        parse_mode="Markdown")
    return ESPERANDO_MO

async def cmd_calcular(update, context):
    precios, _ = cargar_precios()
    if not precios:
        await update.message.reply_text("❌ No pude leer precios.")
        return ConversationHandler.END
    context.user_data["items"] = []
    context.user_data["precios"] = precios
    context.user_data["modo"] = "guiado"
    await update.message.reply_text(
        "🧮 *Calculadora*\nDictame un material por vez:\n"
        "  `cable 2.5mm 15m`\n  `termica 20A x2`\n\nEscribí `listo` para terminar.",
        parse_mode="Markdown")
    return ESPERANDO_ITEM

async def recibir_item(update, context):
    texto = update.message.text.strip()
    if texto.lower() in ["listo", "fin", "ok", "ya"]:
        items = context.user_data.get("items", [])
        if not items:
            await update.message.reply_text("No agregaste nada.")
            return ConversationHandler.END
        sub = sum(i["subtotal"] for i in items)
        await update.message.reply_text(
            f"📦 Subtotal: *{fmt(sub)}*\n\n¿Mano de obra?", parse_mode="Markdown")
        return ESPERANDO_MO
    precios = context.user_data.get("precios", {})
    items, _ = parsear_items(texto, precios)
    if not items:
        res = buscar_material(texto, precios)
        if res:
            sug = "\n".join(f"  • {n}: {fmt(p)}" for n, p in res[:3])
            await update.message.reply_text(f"¿Quisiste decir?\n{sug}\n\nReescribí con cantidad.")
        else:
            await update.message.reply_text(f"No encontré '{texto}'. Usá /materiales.")
        return ESPERANDO_ITEM
    context.user_data["items"].extend(items)
    i = items[0]
    tot = sum(x["subtotal"] for x in context.user_data["items"])
    ct = f"{i['cantidad']:.0f}m" if i["unidad"] == "m" else f"×{int(i['cantidad'])}"
    await update.message.reply_text(
        f"✅ {i['nombre'][:25].title()} {ct} = *{fmt(i['subtotal'])}*\n"
        f"Parcial: {fmt(tot)}\n\nSiguiente o `listo`.", parse_mode="Markdown")
    return ESPERANDO_ITEM

async def recibir_mo(update, context):
    try:
        mo = int(re.sub(r'[^\d]', '', update.message.text.strip()))
    except:
        await update.message.reply_text("Solo el número. Ej: 50000")
        return ESPERANDO_MO
    context.user_data["mo"] = mo
    await update.message.reply_text("¿Para qué cliente? (`-` para saltar)")
    return ESPERANDO_NOMBRE

async def recibir_nombre(update, context):
    nombre = update.message.text.strip()
    if nombre == "-":
        nombre = ""
    items = context.user_data.get("items", [])
    mo = context.user_data.get("mo", 0)
    texto, sub, total = hacer_presupuesto(items, mo, nombre)
    await update.message.reply_text(texto, parse_mode="Markdown")
    plano = texto.replace("*", "").replace("_", "")
    await update.message.reply_text(f"📋 *Para WhatsApp:*\n\n`{plano}`", parse_mode="Markdown")
    context.user_data.clear()
    return ConversationHandler.END

async def cmd_precio(update, context):
    if not context.args:
        await update.message.reply_text("Usá: `/precio cable`", parse_mode="Markdown")
        return
    q = " ".join(context.args)
    precios, dolar = cargar_precios()
    res = buscar_material(q, precios)
    if not res:
        await update.message.reply_text(f"No encontré '{q}'. Usá /materiales.")
        return
    L = [f"🔍 *{q.title()}*\n"] + [f"• {n[:35].title()}: *{fmt(p)}*" for n, p in res]
    if dolar:
        L.append(f"\n💵 Dólar blue: ${dolar}")
    await update.message.reply_text("\n".join(L), parse_mode="Markdown")

async def cmd_materiales(update, context):
    precios, dolar = cargar_precios()
    if not precios:
        await update.message.reply_text("❌ No pude leer precios.")
        return
    grupos = {"🔌 Cables": [], "⚡ Térmicas": [], "🛡️ Diferenciales": [],
              "🔲 Tomas": [], "💡 LED": [], "🔧 Otros": []}
    for n, p in precios.items():
        l = f"  • {n[:28].title()}: {fmt(p)}"
        if "cable" in n: grupos["🔌 Cables"].append(l)
        elif any(x in n for x in ["term", "térm"]): grupos["⚡ Térmicas"].append(l)
        elif any(x in n for x in ["disyuntor", "diferencial"]): grupos["🛡️ Diferenciales"].append(l)
        elif any(x in n for x in ["toma", "interruptor", "set"]): grupos["🔲 Tomas"].append(l)
        elif any(x in n for x in ["tubo", "led"]): grupos["💡 LED"].append(l)
        else: grupos["🔧 Otros"].append(l)
    msg = "📋 *MATERIALES*\n"
    for g, items in grupos.items():
        if items:
            msg += f"\n{g}\n" + "\n".join(items) + "\n"
    if dolar:
        msg += f"\n💵 Dólar blue: ${dolar}"
    if len(msg) > 4000:
        c = msg.rfind("\n", 0, 3900)
        await update.message.reply_text(msg[:c], parse_mode="Markdown")
        await update.message.reply_text(msg[c:], parse_mode="Markdown")
    else:
        await update.message.reply_text(msg, parse_mode="Markdown")

async def cmd_cancelar(update, context):
    context.user_data.clear()
    await update.message.reply_text("❌ Cancelado.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()
    cp = ConversationHandler(
        entry_points=[CommandHandler("presupuesto", cmd_presupuesto), CommandHandler("calcular", cmd_calcular)],
        states={ESPERANDO_ITEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_item)],
                ESPERANDO_MO:   [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_mo)],
                ESPERANDO_NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_nombre)]},
        fallbacks=[CommandHandler("cancelar", cmd_cancelar)], per_user=True)
    cc = ConversationHandler(
        entry_points=[CommandHandler("cobrar", cmd_cobrar)],
        states={COBRAR_ELEGIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, cobrar_elegir)]},
        fallbacks=[CommandHandler("cancelar", cmd_cancelar)], per_user=True)
    ccerrar = ConversationHandler(
        entry_points=[CommandHandler("cerrar", cmd_cerrar)],
        states={CERRAR_ELEGIR: [MessageHandler(filters.TEXT & ~filters.COMMAND, cerrar_elegir)]},
        fallbacks=[CommandHandler("cancelar", cmd_cancelar)], per_user=True)
    cnuevo = ConversationHandler(
        entry_points=[CommandHandler("nuevo", cmd_nuevo)],
        states={NUEVO_CLIENTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, nuevo_cliente)],
                NUEVO_DIR:     [MessageHandler(filters.TEXT & ~filters.COMMAND, nuevo_dir)],
                NUEVO_DESC:    [MessageHandler(filters.TEXT & ~filters.COMMAND, nuevo_desc)],
                NUEVO_MONTO:   [MessageHandler(filters.TEXT & ~filters.COMMAND, nuevo_monto)]},
        fallbacks=[CommandHandler("cancelar", cmd_cancelar)], per_user=True)
    for h in [cp, cc, ccerrar, cnuevo]:
        app.add_handler(h)
    for cmd, fn in [("resumen", cmd_resumen), ("trabajos", cmd_trabajos), ("deuda", cmd_deuda),
                    ("precio", cmd_precio), ("materiales", cmd_materiales),
                    ("ayuda", cmd_ayuda), ("start", cmd_ayuda)]:
        app.add_handler(CommandHandler(cmd, fn))
    print("⚡ Asistente Electro Bot iniciado...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
