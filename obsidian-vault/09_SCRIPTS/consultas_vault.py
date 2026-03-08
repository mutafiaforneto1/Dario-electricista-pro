import os, re, glob

VAULT = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault"
TRABAJOS = os.path.join(VAULT, "01_TRABAJOS")
PRECIOS_MD = os.path.join(VAULT, "08_PRECIOS/Lista de Precios DistriElectro.md")

# ── PRECIOS ──────────────────────────────────────────────────────────────────

def leer_catalogo():
    try:
        with open(PRECIOS_MD, encoding="utf-8") as f:
            lineas = f.readlines()
    except FileNotFoundError:
        return "❌ No se encontró Lista de Precios DistriElectro.md"

    items = []
    for linea in lineas:
        # Busca filas de tabla markdown: | texto | texto |
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if len(celdas) >= 2 and celdas[0] and not celdas[0].startswith("-"):
            items.append(celdas)

    if not items:
        return "⚠️ Catálogo vacío o formato no reconocido."

    # Saltar encabezado si existe
    inicio = 1 if len(items) > 1 else 0
    lineas_out = []
    for row in items[inicio:]:
        nombre = row[0]
        precio = row[1] if len(row) > 1 else "?"
        lineas_out.append(f"• {nombre}: ${precio}")

    return "📦 *Catálogo DistriElectro:*\n" + "\n".join(lineas_out)


# ── STATS ─────────────────────────────────────────────────────────────────────

def contar_trabajos():
    archivos = glob.glob(os.path.join(TRABAJOS, "*.md"))
    return f"📊 Total de trabajos registrados: *{len(archivos)}*"


# ── VENCIDOS / DEUDORES ───────────────────────────────────────────────────────

# Patrones que indican deuda pendiente (tolerante a variaciones)
_PATRONES_DEUDA = [
    re.compile(r"pagado\s*:\s*(false|no|pendiente)", re.I),   # YAML: pagado: false
    re.compile(r"pagado\s*:\s*\[\s*\]", re.I),                # YAML: pagado: []
    re.compile(r"- \[ \].*(?:pag|deu|cobr|debe)", re.I),      # Tarea: - [ ] pagar...
    re.compile(r"(?:debe|deudor|deudora|pendiente de pago)", re.I),  # Texto libre
    re.compile(r"cobrar\s*\$?\s*\d+", re.I),                  # cobrar $500
]

def _es_deudor(contenido):
    return any(p.search(contenido) for p in _PATRONES_DEUDA)

def _nombre_desde_archivo(ruta):
    base = os.path.basename(ruta).replace(".md", "")
    # Convierte "andrea_garcia" o "Andrea Garcia" → "Andrea Garcia"
    return base.replace("_", " ").replace("-", " ").title()

def _extraer_monto(contenido):
    # Busca el primer número que parezca un monto
    m = re.search(r"\$?\s*(\d[\d.,]+)", contenido)
    return m.group(0).strip() if m else None

def listar_vencidos():
    archivos = glob.glob(os.path.join(TRABAJOS, "*.md"))
    deudores = []

    for ruta in sorted(archivos):
        try:
            with open(ruta, encoding="utf-8") as f:
                contenido = f.read()
        except Exception:
            continue

        if _es_deudor(contenido):
            nombre = _nombre_desde_archivo(ruta)
            monto = _extraer_monto(contenido)
            linea = f"• {nombre}"
            if monto:
                linea += f" — {monto}"
            deudores.append(linea)

    if not deudores:
        return "✅ Sin deudores detectados."

    encabezado = f"⚠️ *Clientes con pagos pendientes ({len(deudores)}):*"
    return encabezado + "\n" + "\n".join(deudores)
