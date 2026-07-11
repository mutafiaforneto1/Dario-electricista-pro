#!/usr/bin/env python3
"""
Procesador de WhatsApp Business para Darío Electricista v2.2
============================================================
Lee el log de MacroDroid, resume con Groq, postea a ClickUp
y guarda resúmenes visibles en /sdcard/Documents/WhatsApp Resumenes/

Arquitectura:
  MacroDroid → /sdcard/whatsapp_trabajos.log
    → Groq IA (resumen)
    → ClickUp (tareas por contacto)
    → Carpeta visible /sdcard/Documents/WhatsApp Resumenes/ (archivos por contacto)

Uso:
  python3 procesar_whatsapp.py               # Modo normal
  python3 procesar_whatsapp.py --test        # Test sin guardar
  python3 procesar_whatsapp.py --watch       # Loop cada 60s
  python3 procesar_whatsapp.py --init        # Inicializar carpeta en Android
"""

import os, re, json, subprocess, sys, time, base64
from datetime import datetime
from collections import defaultdict

# ═══ CONFIG ═══════════════════════════════════════════
CLICKUP_TOKEN = os.environ.get("CLICKUP_TOKEN", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
LOG_FILE = "/sdcard/whatsapp_trabajos.log"
MARCA_FILE = "/tmp/.wa_mark"
RESUMENES_DIR = "/sdcard/Documents/WhatsApp Resumenes"
LOCAL_DIR = "/tmp/wa_resumenes"

# Mapeo: patrón → (list_id_clickup, categoria, emoji, nombre_archivo)
MAP = {
    "carolina":         ("901714997413", "personal", "❤️", "Carolina"),
    "claudia":          ("901714936090", "cliente",  "👤", "Claudia"),
    "evita":            ("901714997484", "familia",  "👧", "Evita"),
    "jess":             ("901714936090", "cliente",  "👤", "Jess"),
    "romina arias":     ("901714936090", "cliente",  "👤", "Romina Arias"),
    "francisco":        ("901714997484", "familia",  "👦", "Francisco"),
    "media 26":         ("901714999529", "escuela",  "🏫", "Media 26 - 2do 1ra"),
    "6° 5°":            ("901714999529", "escuela",  "🏫", "6° 5° - Familias"),
    "2do 1ra":          ("901714999530", "escuela",  "🏫", "2do 1ra"),
}

DEFAULT_ARCHIVO = "Clientes Varios"
SISTEMA = ("whatsapp business", "copia de seguridad", "no se pudo",
           "tu agente de ia", "mi num", "tú", "llamada")

# ═══ SHIZUKU ══════════════════════════════════════════
def sh(cmd):
    try:
        r = subprocess.run(["shizuku", "sh", "-c", cmd],
                           capture_output=True, text=True, timeout=30)
        return (r.stdout + r.stderr)
    except:
        return ""

# ═══ PARSER ═══════════════════════════════════════════
def parse(raw):
    entries = []
    text = raw.replace("\n", " ")
    for part in re.split(r'(?=\d{10}\|)', text):
        m = re.match(r'(\d{10})\|([^|]*)\|(.*)', part.strip())
        if m and m.group(2).strip():
            entries.append({"ts": m.group(1),
                           "sender": m.group(2).strip(),
                           "msg": m.group(3).strip()})
    return entries

def es_sistema(sender):
    return any(x in sender.lower() for x in SISTEMA)

def clasificar(sender):
    s = sender.lower()
    for pat, vals in MAP.items():
        if pat in s:
            return vals
    return ("901714936090", "cliente", "👤", DEFAULT_ARCHIVO)

# ═══ GROQ ═════════════════════════════════════════════
_cache = {}
def resumir(sender, msg, categoria):
    key = f"{sender}|{msg[:50]}"
    if key in _cache:
        return _cache[key]
    prompt = f"""Resumí este WhatsApp en 1-2 líneas:
- Quién escribe, qué pide
- Dirección si hay
- Urgencia

Remitente: {sender}
Categoría: {categoria}
Mensaje: {msg[:500]}"""
    try:
        import groq
        r = groq.Groq(api_key=GROQ_API_KEY).chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3, max_tokens=200)
        result = r.choices[0].message.content.strip()
    except:
        result = f"{sender}: {msg[:100]}..."
    _cache[key] = result
    return result

# ═══ CLICKUP ══════════════════════════════════════════
def cu(method, endpoint, data=None):
    import requests
    h = {"Authorization": CLICKUP_TOKEN, "Content-Type": "application/json"}
    url = f"https://api.clickup.com/api/v2/{endpoint}"
    try:
        if method == "GET":
            return requests.get(url, headers=h, timeout=15).json()
        return requests.post(url, headers=h, json=data, timeout=15).json()
    except:
        return None

def tarea(list_id, nombre, desc):
    r = cu("POST", f"list/{list_id}/task",
           {"name": nombre[:250], "description": desc[:5000], "not_all": True})
    if r and "id" in r:
        print(f"  ✅ ClickUp: {r['id']}")
        return r["id"]
    return None

# ═══ CARPETA VISIBLE ══════════════════════════════════
def leer_local(nombre_archivo):
    """Lee archivo desde cache local"""
    path = f"{LOCAL_DIR}/{nombre_archivo}.md"
    try:
        with open(path, "r") as f:
            return f.read()
    except:
        return ""

def escribir_local(nombre_archivo, contenido):
    """Escribe a cache local"""
    os.makedirs(LOCAL_DIR, exist_ok=True)
    path = f"{LOCAL_DIR}/{nombre_archivo}.md"
    with open(path, "w") as f:
        f.write(contenido)

def sync_a_android(nombre_archivo):
    """Sincroniza un archivo del cache local a Android via base64"""
    path_local = f"{LOCAL_DIR}/{nombre_archivo}.md"
    path_and = f"{RESUMENES_DIR}/{nombre_archivo}.md"
    try:
        with open(path_local, "r") as f:
            contenido = f.read()
        encoded = base64.b64encode(contenido.encode()).decode()
        sh(f'mkdir -p "{RESUMENES_DIR}"')
        sh(f'echo "{encoded}" | base64 -d > "{path_and}"')
    except:
        pass

def guardar_en_carpeta(sender, emoji, nombre_archivo, resumen):
    """Agrega resumen al archivo del contacto"""
    ahora = datetime.now()
    hoy = ahora.strftime("%d/%m/%Y")
    hora = ahora.strftime("%H:%M")
    
    # Aplanar resumen a una línea
    resumen_plano = resumen.replace("\n", " | ").strip()
    
    # Leer actual
    actual = leer_local(nombre_archivo)
    
    if not actual.strip():
        # Archivo nuevo
        nuevo = f"# {emoji} {sender}\n\n"
        nuevo += f"## {hoy}\n"
        nuevo += f"- **{hora}** - {resumen_plano}\n"
    else:
        nuevo = actual.rstrip() + "\n"
        if f"## {hoy}" in actual:
            nuevo += f"- **{hora}** - {resumen_plano}\n"
        else:
            nuevo += f"\n## {hoy}\n"
            nuevo += f"- **{hora}** - {resumen_plano}\n"
    
    escribir_local(nombre_archivo, nuevo)
    sync_a_android(nombre_archivo)
    print(f"  📁 {nombre_archivo}.md")

# ═══ MARCA ════════════════════════════════════════════
def leer_marca():
    try:
        with open(MARCA_FILE) as f:
            return f.read().strip()
    except:
        return "0"

def guardar_marca(ts):
    with open(MARCA_FILE, "w") as f:
        f.write(str(ts))

# ═══ PROCESAR ═════════════════════════════════════════
def procesar(test=False):
    print(f"\n{'='*55}")
    print(f"📱 WhatsApp → Groq → ClickUp + Carpeta Visible")
    print(f"   {datetime.now():%Y-%m-%d %H:%M}")
    print(f"{'='*55}")
    
    raw = sh(f"tail -c 30000 {LOG_FILE}")
    if not raw:
        print("❌ No se pudo leer el log")
        return
    entries = parse(raw)
    print(f"📄 {len(entries)} entradas")
    
    if test:
        cols = [e for e in entries if not es_sistema(e["sender"]) and e["msg"]]
        pendientes = cols[-5:]
        print(f"🧪 Test: {len(pendientes)} msgs\n")
    else:
        marca = leer_marca()
        print(f"🏷️ Marca: {marca}")
        pendientes = [e for e in entries
                      if e["ts"] > marca and not es_sistema(e["sender"]) and e["msg"]]
        try:
            with open("/tmp/.wa_hechos") as f:
                hechos = set(f.read().split())
        except:
            hechos = set()
        pendientes = [e for e in pendientes if e["ts"] not in hechos]
        print(f"🆕 {len(pendientes)} nuevos\n")
    
    if not pendientes:
        print("ℹ️ Nada que procesar")
        return
    
    grupos = defaultdict(list)
    for e in pendientes:
        grupos[e["sender"]].append(e)
    
    total = 0
    for sender, msgs in sorted(grupos.items()):
        lid, cat, emoji, archivo = clasificar(sender)
        textos = [m["msg"] for m in msgs[-3:] if m["msg"]]
        combined = " | ".join(textos)
        
        ahora = datetime.now()
        print(f"── {sender} ({len(msgs)}) {emoji} ──")
        
        print(f"  🤖 Groq...")
        summary = resumir(sender, combined, cat)
        print(f"  📝 {summary}")
        
        if not test:
            if lid:
                print(f"  📋 ClickUp...")
                tarea(lid, f"{emoji} {sender} - {ahora:%d/%m %H:%M}", summary)
            guardar_en_carpeta(sender, emoji, archivo, summary)
        
        with open("/tmp/.wa_hechos", "a") as f:
            for m in msgs:
                f.write(m["ts"] + "\n")
        total += len(msgs)
        time.sleep(0.3)
    
    if not test and pendientes:
        ultimo = max(e["ts"] for e in pendientes)
        guardar_marca(ultimo)
        print(f"\n✅ {total} msgs → ClickUp + Carpeta. Marca: {ultimo}")
    else:
        print(f"\n✅ Test: {total} msgs")

# ═══ WATCH ════════════════════════════════════════════
def watch():
    print("🔄 Watch (60s)\n")
    try:
        while True:
            procesar()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Detenido")

# ═══ INIT ═════════════════════════════════════════════
def init_android():
    """Inicializa carpeta en Android"""
    sh(f'mkdir -p "{RESUMENES_DIR}"')
    sh(f'touch "{RESUMENES_DIR}/.nomedia"')  # Evita que aparezcan en galería
    print(f"✅ Carpeta creada: {RESUMENES_DIR}")
    print("   Los resúmenes aparecerán ahí automáticamente")

# ═══ MAIN ═════════════════════════════════════════════
if __name__ == "__main__":
    import requests
    
    if "--init" in sys.argv:
        init_android()
        sys.exit(0)
    
    if "--api-test" in sys.argv:
        print("🔍 API Test\n")
        print("--- Groq ---")
        r = resumir("Test", "Hola, necesito presupuesto", "cliente")
        print(f"  {r}\n")
        print("--- ClickUp ---")
        teams = cu("GET", "team")
        if teams and "teams" in teams:
            for t in teams["teams"]:
                print(f"  ✅ {t['name']} (ID: {t['id']})")
        print("\n✅ Tests OK")
        sys.exit(0)
    
    if "--watch" in sys.argv:
        watch()
    elif "--test" in sys.argv:
        procesar(test=True)
    else:
        procesar()
