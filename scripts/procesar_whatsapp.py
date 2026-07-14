#!/usr/bin/env python3
"""
Procesador de WhatsApp Business para Darío Electricista v4.0
============================================================
Lee el log de MacroDroid, resume con Groq, postea a Notion + ClickUp + Google Tasks
y guarda resúmenes visibles en /sdcard/Documents/WhatsApp Resumenes/

Arquitectura:
  MacroDroid → /sdcard/whatsapp_trabajos.log
    → Groq IA (resumen)
    → Notion (base de datos principal)
    → ClickUp (respaldo)
    → Google Tasks (recordatorios)
    → Carpeta visible /sdcard/Documents/WhatsApp Resumenes/ (archivos por contacto)

Uso:
  python3 procesar_whatsapp.py               # Modo normal
  python3 procesar_whatsapp.py --test        # Test sin guardar
  python3 procesar_whatsapp.py --watch       # Loop cada 60s
  python3 procesar_whatsapp.py --init        # Inicializar carpeta en Android
"""

import os, re, json, subprocess, sys, time, base64, urllib.request, urllib.parse
from datetime import datetime
from collections import defaultdict

# ═══ CONFIG ═══════════════════════════════════════════
CLICKUP_TOKEN = os.environ.get("CLICKUP_TOKEN", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")

# Notion Database IDs
NOTION_TRAJOS_DB = "71872a30-fc98-4938-b199-2acbef5c4a4f"
NOTION_CLIENTES_DB = "39dfaa44-15dc-81b8-8e27-c7c4f0c85e06"
NOTION_CALENDARIO_DB = "39dfaa44-15dc-8190-8f53-f529da913a04"
NOTION_PRESUPUESTOS_DB = "39dfaa44-15dc-814a-b8b5-d05d254988e8"
LOG_FILE = "/sdcard/whatsapp_trabajos.log"
MARCA_FILE = "/tmp/.wa_mark"
RESUMENES_DIR = "/sdcard/Documents/WhatsApp Resumenes"
LOCAL_DIR = "/tmp/wa_resumenes"
GOOGLE_TASKS_TOKEN_FILE = "/sdcard/Documents/gtasks_token.json"

# IDs de las listas en Google Tasks (se crean con el setup)
GOOGLE_TASKS_LISTS = {}
_gt_token_cache = None

# Mapeo: patrón → (list_id_clickup, categoria, emoji, nombre_archivo, google_tasks_list)
MAP = {
    "carolina":         ("901714997413", "personal", "❤️", "Carolina", "Familia"),
    "claudia":          ("901714936090", "cliente",  "👤", "Claudia", "Electricista"),
    "evita":            ("901714997484", "familia",  "👧", "Evita", "Familia"),
    "jess":             ("901714936090", "cliente",  "👤", "Jess", "Electricista"),
    "romina arias":     ("901714936090", "cliente",  "👤", "Romina Arias", "Electricista"),
    "francisco":        ("901714997484", "familia",  "👦", "Francisco", "Familia"),
    "media 26":         ("901714999529", "escuela",  "🏫", "Media 26 - 2do 1ra", "Familia"),
    "6° 5°":            ("901714999529", "escuela",  "🏫", "6° 5° - Familias", "Familia"),
    "2do 1ra":          ("901714999530", "escuela",  "🏫", "2do 1ra", "Familia"),
    "mica":             ("901714935828", "trabajo",  "👤", "Mica Hija Fabian", "Electricista"),
}

DEFAULT_ARCHIVO = "Clientes Varios"
DEFAULT_GTASKS = "Electricista"
SISTEMA = ("whatsapp business", "copia de seguridad", "no se pudo",
           "tu agente de ia", "mi num", "tú", "llamada")

# ═══ SHIZUKU ══════════════════════════════════════════
def sh(cmd):
    try:
        r = subprocess.run(["shizuku", "sh", "-c", cmd],
                           capture_output=True, text=True, timeout=15)
        out = r.stdout or ""
        if not out.strip():
            out = r.stderr or ""
        return out
    except:
        return ""

# ═══ GOOGLE TASKS ═════════════════════════════════════
def gt_token():
    global _gt_token_cache
    if _gt_token_cache:
        return _gt_token_cache
    try:
        with open(GOOGLE_TASKS_TOKEN_FILE) as f:
            data = json.load(f)
        _gt_token_cache = data.get("access_token")
        return _gt_token_cache
    except:
        return None

def gt_refresh_token():
    """Refresh the access token if expired"""
    global _gt_token_cache
    try:
        with open(GOOGLE_TASKS_TOKEN_FILE) as f:
            data = json.load(f)
        refresh = data.get("refresh_token")
        if not refresh:
            return False
        body = urllib.parse.urlencode({
            "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
            "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET", ""),
            "refresh_token": refresh,
            "grant_type": "refresh_token"
        }).encode()
        req = urllib.request.Request("https://oauth2.googleapis.com/token", data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"})
        resp = urllib.request.urlopen(req)
        new = json.loads(resp.read())
        data["access_token"] = new["access_token"]
        if "refresh_token" in new:
            data["refresh_token"] = new["refresh_token"]
        with open(GOOGLE_TASKS_TOKEN_FILE, "w") as f:
            json.dump(data, f)
        _gt_token_cache = new["access_token"]
        return True
    except:
        return False

def gt_call(method, url, data=None):
    """Make API call to Google Tasks"""
    token = gt_token()
    if not token:
        return None
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    d = json.dumps(data).encode() if data else None
    try:
        req = urllib.request.Request(url, data=d, headers=headers, method=method)
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 401:
            if gt_refresh_token():
                return gt_call(method, url, data)
        return None
    except:
        return None

def gt_ensure_list(list_name):
    """Find or create a Google Tasks list by name"""
    if list_name in GOOGLE_TASKS_LISTS:
        return GOOGLE_TASKS_LISTS[list_name]
    
    # List all existing task lists
    lists = gt_call("GET", "https://tasks.googleapis.com/tasks/v1/users/@me/lists")
    if lists and "items" in lists:
        for lst in lists["items"]:
            GOOGLE_TASKS_LISTS[lst["title"]] = lst["id"]
            if list_name == lst["title"]:
                return lst["id"]
    
    # Create new list
    result = gt_call("POST", "https://tasks.googleapis.com/tasks/v1/users/@me/lists",
                     {"title": list_name})
    if result and "id" in result:
        GOOGLE_TASKS_LISTS[list_name] = result["id"]
        return result["id"]
    return None

def gt_agregar_tarea(list_name, title, notes=""):
    """Add a task to a Google Tasks list, avoiding duplicates"""
    list_id = gt_ensure_list(list_name)
    if not list_id:
        print(f"  ⚠️ No se pudo crear/encontrar lista '{list_name}' en Google Tasks")
        return False
    
    # Check for duplicates in the last 100 tasks
    existing = gt_call("GET",
        f"https://tasks.googleapis.com/tasks/v1/lists/{list_id}/tasks?maxResults=100")
    if existing and "items" in existing:
        for task in existing["items"]:
            if task.get("title") == title and task.get("status") != "completed":
                # Already exists, update notes if needed
                if notes and task.get("notes") != notes:
                    gt_call("PATCH",
                        f"https://tasks.googleapis.com/tasks/v1/lists/{list_id}/tasks/{task['id']}",
                        {"notes": notes})
                return True
    
    # Create new task
    result = gt_call("POST",
        f"https://tasks.googleapis.com/tasks/v1/lists/{list_id}/tasks",
        {"title": title, "notes": notes})
    return result is not None

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
    return ("901714936090", "cliente", "👤", DEFAULT_ARCHIVO, DEFAULT_GTASKS)

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
    r = cu("POST", f"list/{list_id}/task", {
        "name": nombre[:497], "description": desc[:497]})
    return r

# ═══ CARPETA VISIBLE ══════════════════════════════════
def init_carpetas():
    for d in [LOCAL_DIR]:
        os.makedirs(d, exist_ok=True)

def leer_local(nombre_archivo):
    path = os.path.join(LOCAL_DIR, f"{nombre_archivo}.md")
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except:
        return None

def escribir_local(nombre_archivo, contenido):
    path = os.path.join(LOCAL_DIR, f"{nombre_archivo}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(contenido)

def sincronizar(nombre_archivo):
    destino = f"{RESUMENES_DIR}/{nombre_archivo}.md"
    sh(f'cp "{os.path.join(LOCAL_DIR, nombre_archivo + ".md")}" "{destino}" 2>/dev/null')
    sh(f'chmod 644 "{destino}" 2>/dev/null')

def guardar_en_carpeta(sender, emoji, nombre_archivo, resumen_plano):
    ahora = datetime.now()
    hoy = ahora.strftime("%Y-%m-%d")
    hora = ahora.strftime("%H:%M")
    
    actual = leer_local(nombre_archivo)
    if actual is None:
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
    sincronizar(nombre_archivo)
    print(f"  📁 {nombre_archivo}.md")

# ═══ NOTION ════════════════════════════════════════════
def notion(method, endpoint, data=None):
    """Call Notion API"""
    if not NOTION_TOKEN:
        return None
    url = f"https://api.notion.com/v1/{endpoint}"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    try:
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        if "conflict" in error_body.lower():
            return {"_conflict": True}
        print(f"  ⚠️ Notion error {e.code}: {error_body[:100]}")
        return None
    except Exception as e:
        print(f"  ⚠️ Notion exception: {e}")
        return None

def notion_create_or_update(db_id, search_key, title_field, properties, categoria):
    """Create or update a Notion page. Deduplicates by title."""
    # Search existing pages by title
    query = {
        "filter": {
            "property": title_field,
            "title": {"contains": search_key[:50]}
        }
    }
    existing = notion("POST", f"databases/{db_id}/query", query)
    
    if existing and existing.get("results"):
        page = existing["results"][0]
        page_id = page["id"]
        # Update the page
        result = notion("PATCH", f"pages/{page_id}", {"properties": properties})
        if result and not result.get("_conflict"):
            print(f"  📝 Notion: actualizado")
            return True
        return False
    else:
        # Create new page
        new_page = {
            "parent": {"type": "database_id", "database_id": db_id},
            "properties": properties
        }
        result = notion("POST", "pages", new_page)
        if result and result.get("id"):
            print(f"  📝 Notion: creado")
            return True
        return False

def notion_agregar_contacto(sender, resumen, categoria, emoji):
    """Add or update a contact in Notion Clientes DB"""
    props = {
        "Cliente": {"title": [{"text": {"content": sender[:2000]}}]},
        "Estado": {"select": {"name": "🟢 Activo"}},
        "Notas": {"rich_text": [{"text": {"content": resumen[:2000]}}]}
    }
    return notion_create_or_update(
        NOTION_CLIENTES_DB, sender, "Cliente", props, categoria
    )

def notion_agregar_trabajo(sender, resumen, categoria, emoji):
    """Add a work entry in Notion Trabajos DB"""
    ahora = datetime.now()
    props = {
        "Trabajo": {"title": [{"text": {"content": f"{emoji} {sender} - {ahora:%d/%m %H:%M}"[:2000]}}]},
        "Descripción del trabajo": {"rich_text": [{"text": {"content": resumen[:2000]}}]},
        "Estado": {"select": {"name": "Pendiente"}},
        "Categoría": {"select": {"name": "📋 Presupuesto" if "presup" in resumen.lower() else "⚡ Instalación"}}
    }
    return notion_create_or_update(
        NOTION_TRAJOS_DB, sender, "Trabajo", props, categoria
    )

def notion_agregar_calendario(sender, resumen, categoria, emoji):
    """Add a calendar event in Notion Calendar DB"""
    tipo_map = {
        "personal": "❤️ Personal",
        "familia": "👧 Hijos",
        "escuela": "🏫 Escuela",
        "trabajo": "⚡ Trabajo",
        "cliente": "⚡ Trabajo"
    }
    tipo = tipo_map.get(categoria, "⚡ Trabajo")
    props = {
        "Título": {"title": [{"text": {"content": f"{emoji} {sender} - {resumen[:100]}"[:2000]}}]},
        "Tipo": {"select": {"name": tipo}},
        "Notas": {"rich_text": [{"text": {"content": resumen[:2000]}}]},
        "Estado": {"select": {"name": "Pendiente"}}
    }
    return notion_create_or_update(
        NOTION_CALENDARIO_DB, sender, "Título", props, categoria
    )

def notion_procesar_mensaje(sender, resumen, categoria, emoji):
    """Route message to appropriate Notion databases"""
    if not NOTION_TOKEN:
        return
    
    if categoria == "cliente":
        notion_agregar_contacto(sender, resumen, categoria, emoji)
        notion_agregar_trabajo(sender, resumen, categoria, emoji)
    elif categoria == "trabajo":
        notion_agregar_trabajo(sender, resumen, categoria, emoji)
    else:
        notion_agregar_calendario(sender, resumen, categoria, emoji)

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
    print(f"📱 WhatsApp → Groq → ClickUp + Google Tasks + Carpeta")
    print(f"   {datetime.now():%Y-%m-%d %H:%M}")
    print(f"{'='*55}")
    
    raw = sh(f"tail -c 30000 {LOG_FILE}")
    if not raw:
        print("❌ No se pudo leer el log")
        return
    entries = parse(raw)
    print(f"📄 {len(entries)} entradas")
    
    # Check Google Tasks connectivity
    has_gt = gt_token() is not None
    if not has_gt:
        print("ℹ️ Google Tasks no configurado (sin token)")
    
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
        lid, cat, emoji, archivo, gt_list = clasificar(sender)
        textos = [m["msg"] for m in msgs[-3:] if m["msg"]]
        combined = " | ".join(textos)
        
        ahora = datetime.now()
        print(f"── {sender} ({len(msgs)}) {emoji} ──")
        
        print(f"  🤖 Groq...")
        summary = resumir(sender, combined, cat)
        print(f"  📝 {summary}")
        
        if not test:
            # Notion (base de datos principal)
            if NOTION_TOKEN:
                print(f"  📝 Notion...")
                notion_procesar_mensaje(sender, summary, cat, emoji)
            
            # ClickUp (respaldo)
            if lid:
                print(f"  📋 ClickUp...")
                tarea(lid, f"{emoji} {sender} - {ahora:%d/%m %H:%M}", summary)
            
            # Google Tasks (recordatorios)
            if has_gt:
                task_title = f"{emoji} {sender} - {summary[:60]}"
                if gt_agregar_tarea(gt_list, task_title, summary):
                    print(f"  ✅ Google Tasks ({gt_list})")
                else:
                    print(f"  ⚠️ Google Tasks falló")
            
            # Carpeta visible
            guardar_en_carpeta(sender, emoji, archivo, summary)
        
        with open("/tmp/.wa_hechos", "a") as f:
            for m in msgs:
                f.write(m["ts"] + "\n")
        total += len(msgs)
        time.sleep(0.5)  # Rate limiting
    
    if not test and pendientes:
        ultimo = max(e["ts"] for e in pendientes)
        guardar_marca(ultimo)
        print(f"\n✅ {total} msgs -> Notion + ClickUp + GTasks + Carpeta. Marca: {ultimo}")
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
    sh(f'mkdir -p "{RESUMENES_DIR}"')
    sh(f'touch "{RESUMENES_DIR}/.nomedia"')
    print(f"✅ Carpeta creada: {RESUMENES_DIR}")

# ═══ MAIN ═════════════════════════════════════════════
if __name__ == "__main__":
    import requests
    
    init_carpetas()
    
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
                print(f"  ✅ {t['name']}")
        print("--- Google Tasks ---")
        if gt_token():
            lists = gt_call("GET", "https://tasks.googleapis.com/tasks/v1/users/@me/lists")
            if lists and "items" in lists:
                for lst in lists["items"]:
                    print(f"  ✅ {lst['title']}")
        print("\n✅ Tests OK")
        sys.exit(0)
    
    if "--watch" in sys.argv:
        watch()
    elif "--test" in sys.argv:
        procesar(test=True)
    else:
        procesar()
