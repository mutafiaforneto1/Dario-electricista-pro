import os, re
from datetime import date

VAULT = "/storage/emulated/0/Documents/Dario-electricista-pro/obsidian-vault"
TRABAJOS = f"{VAULT}/01_TRABAJOS"
CLIENTES = f"{VAULT}/02_CLIENTES"
PRECIOS_FILE = f"{VAULT}/08_PRECIOS/Lista de Precios DistriElectro.md"

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
    "Urgencia noche": 103191,
}

def parse_frontmatter(contenido):
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
                data = parse_frontmatter(contenido)
                if data.get("tipo") == "trabajo":
                    cliente = data.get("cliente", "")
                    if "/" in cliente:
                        cliente = cliente.split("/")[-1]
                    data["cliente"] = cliente
                    data["_ruta"] = os.path.join(root, archivo)
                    trabajos.append(data)
            except:
                pass
    trabajos.sort(key=lambda x: x.get("fecha", ""), reverse=True)
    return trabajos

def get_clientes():
    clientes = []
    for archivo in sorted(os.listdir(CLIENTES)):
        if not archivo.endswith(".md"):
            continue
        try:
            with open(os.path.join(CLIENTES, archivo), "r", encoding="utf-8") as f:
                contenido = f.read()
            data = parse_frontmatter(contenido)
            data["_nombre"] = archivo.replace(".md","").replace("Cliente ","")
            clientes.append(data)
        except:
            pass
    return clientes

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

def get_dolar():
    try:
        import urllib.request, json
        with urllib.request.urlopen("https://dolarapi.com/v1/dolares/blue", timeout=5) as r:
            return json.loads(r.read()).get("venta")
    except:
        return None

def get_precios():
    precios = []
    try:
        with open(PRECIOS_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                m = re.match(r"\|\s*(.+?)\s*\|\s*(\d+)\s*\|", linea)
                if m and m.group(1) != "Material":
                    precios.append((m.group(1).strip(), int(m.group(2))))
    except:
        pass
    return precios

def crear_trabajo(cliente, telefono, direccion, descripcion, monto, estado="pendiente"):
    hoy = date.today().strftime("%Y-%m-%d")
    carpeta = os.path.join(TRABAJOS, cliente)
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, f"{cliente} - {hoy}.md")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(f"""---
tipo: trabajo
cliente: "[[Cliente {cliente}]]"
telefono: {telefono}
direccion: {direccion}
fecha: {hoy}
estado: {estado}
mano_de_obra: {monto}
costo_materiales: 0
pagado: false
---

# {cliente}

## Descripcion
{descripcion}

## Tareas
- [ ] 

## Notas

""")
    return ruta

def actualizar_estado(ruta, estado, pagado=None):
    with open(ruta, "r", encoding="utf-8") as f:
        c = f.read()
    c = re.sub(r"^estado: .+", f"estado: {estado}", c, flags=re.MULTILINE)
    if pagado is not None:
        c = re.sub(r"^pagado: .+", f"pagado: {str(pagado).lower()}", c, flags=re.MULTILINE)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(c)
