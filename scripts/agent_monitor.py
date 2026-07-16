#!/usr/bin/env python3
"""
Agente Monitor - Reporte automático de todos los agentes
Corre cada pocas horas y genera un resumen completo.
"""

import os, json, requests
from datetime import datetime, timedelta

CLICKUP_TOKEN = os.environ.get("CLICKUP_TOKEN", "")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
GTASKS_TOKEN = None

# Load tokens from .dario_env
env_file = "/sdcard/Documents/.dario_env"
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

CLICKUP_TOKEN = os.environ.get("CLICKUP_TOKEN", "")
NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")

# Load Google Tasks token
gt_file = "/sdcard/Documents/gtasks_token.json"
if os.path.exists(gt_file):
    with open(gt_file) as f:
        GTASKS_TOKEN = json.load(f).get("access_token")

def cu(endpoint):
    r = requests.get(f"https://api.clickup.com/api/v2/{endpoint}", 
                     headers={"Authorization": CLICKUP_TOKEN})
    return r.json() if r.status_code == 200 else {}

def notion_query(db_id, filter_data=None):
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    data = json.dumps(filter_data or {}).encode()
    r = requests.post(f"https://api.notion.com/v1/databases/{db_id}/query", 
                     headers=headers, data=data)
    return r.json().get('results', []) if r.status_code == 200 else []

def generar_reporte():
    ahora = datetime.now()
    hoy = ahora.strftime("%Y-%m-%d")
    reporte = []
    
    reporte.append(f"📊 REPORTE DIARIO - {ahora.strftime('%d/%m/%Y %H:%M')}")
    reporte.append("=" * 50)
    
    # ═══ AGENTE DE TRABAJOS ═══
    reporte.append("\n📋 AGENTE DE TRABAJOS:")
    reporte.append("-" * 30)
    
    tasks_data = cu("list/901714935828/task?include_closed=false&page=0")
    tasks = tasks_data.get('tasks', [])
    
    pendientes = []
    vencidos = []
    proximos = []
    
    for t in tasks:
        name = t['name']
        status = t.get('status', {}).get('status', 'N/A')
        due = t.get('due_date')
        
        if due:
            due_dt = datetime.fromtimestamp(int(due)/1000)
            dias = (due_dt - ahora).days
            
            if dias < 0:
                vencidos.append((name, status, due_dt.strftime('%d/%m'), abs(dias)))
            elif dias <= 2:
                proximos.append((name, status, due_dt.strftime('%d/%m'), dias))
            else:
                pendientes.append((name, status, due_dt.strftime('%d/%m'), dias))
        else:
            pendientes.append((name, status, 'Sin fecha', -1))
    
    if vencidos:
        reporte.append(f"  ⚠️ VENCIDOS ({len(vencidos)}):")
        for name, status, due, dias in vencidos:
            reporte.append(f"    🔴 {name[:40]} (venció hace {dias} días)")
    
    if proximos:
        reporte.append(f"  📅 PRÓXIMOS ({len(proximos)}):")
        for name, status, due, dias in proximos:
            reporte.append(f"    🟡 {name[:40]} (vence {due})")
    
    reporte.append(f"  📋 Total activos: {len(tasks)}")
    
    # ═══ AGENTE DE COBROS ═══
    reporte.append("\n💵 AGENTE DE COBROS:")
    reporte.append("-" * 30)
    
    completados = cu("list/901714935828/task?include_closed=true&page=0")
    deudas = []
    for t in completados.get('tasks', []):
        name = t['name']
        desc = (t.get('description', '') or '').lower()
        if 'deuda' in name.lower() or 'debe' in desc or 'pendiente' in desc:
            deudas.append(name)
    
    if deudas:
        reporte.append(f"  💰 Deudas pendientes ({len(deudas)}):")
        for d in deudas:
            reporte.append(f"    🔴 {d[:50]}")
    else:
        reporte.append("  ✅ Sin deudas pendientes")
    
    # ═══ AGENTE DE CLIENTES ═══
    reporte.append("\n👤 AGENTE DE CLIENTES:")
    reporte.append("-" * 30)
    
    clientes_data = cu("list/901714936090/task?include_closed=false&page=0")
    clientes = clientes_data.get('tasks', [])
    reporte.append(f"  📊 Total clientes activos: {len(clientes)}")
    
    # ═══ AGENTE DE PRESUPUESTOS ═══
    reporte.append("\n💰 AGENTE DE PRESUPUESTOS:")
    reporte.append("-" * 30)
    
    presupuestos = notion_query("39dfaa44-15dc-814a-b8b5-d05d254988e8")
    pendientes_pres = []
    for p in presupuestos:
        props = p['properties']
        estado = props.get('Estado', {}).get('select', {}).get('name', 'N/A') if props.get('Estado') else 'N/A'
        if estado in ['📄 Borrador', '📨 Enviado']:
            title = props['Presupuesto']['title'][0]['plain_text'] if props['Presupuesto']['title'] else 'N/A'
            total = props.get('Total', {}).get('number', 0) if props.get('Total') else 0
            pendientes_pres.append((title, estado, total))
    
    if pendientes_pres:
        reporte.append(f"  📄 Pendientes ({len(pendientes_pres)}):")
        for title, estado, total in pendientes_pres:
            reporte.append(f"    📌 {title[:30]} - {estado} - ${total}")
    else:
        reporte.append("  ✅ Sin presupuestos pendientes")
    
    # ═══ AGENTE DE ANÁLISIS ═══
    reporte.append("\n📊 AGENTE DE ANÁLISIS:")
    reporte.append("-" * 30)
    
    total_cobrado = 0
    trabajos_completados = 0
    for t in completados.get('tasks', []):
        for cf in t.get('custom_fields', []):
            if cf.get('name') == 'Monto Cobrado' and cf.get('value'):
                try:
                    total_cobrado += float(cf['value'])
                    trabajos_completados += 1
                except:
                    pass
    
    reporte.append(f"  💰 Total cobrado (historial): ${total_cobrado:,.0f}")
    reporte.append(f"  ✅ Trabajos completados: {trabajos_completados}")
    reporte.append(f"  📋 Trabajos activos: {len(tasks)}")
    
    # ═══ RESUMEN ═══
    reporte.append("\n" + "=" * 50)
    reporte.append("📝 RESUMEN EJECUTIVO:")
    
    alertas = len(vencidos) + len(deudas) + len(pendientes_pres)
    if alertas > 0:
        reporte.append(f"  ⚠️ {alertas} alertas pendientes")
    else:
        reporte.append("  ✅ Todo en orden")
    
    if vencidos:
        reporte.append(f"  🔴 {len(vencidos)} trabajos vencidos — revisar")
    if proximos:
        reporte.append(f"  🟡 {len(proximos)} trabajos próximos a vencer")
    if deudas:
        reporte.append(f"  💰 {len(deudas)} cobros pendientes")
    
    reporte.append(f"\n  ⏰ Próximo reporte: en 4 horas")
    reporte.append("=" * 50)
    
    return "\n".join(reporte)


def guardar_reporte(reporte):
    ahora = datetime.now()
    fecha = ahora.strftime("%Y-%m-%d_%H%M")
    
    # Save to local
    local_dir = "/tmp/wa_resumenes"
    os.makedirs(local_dir, exist_ok=True)
    
    path = os.path.join(local_dir, f"Reporte_{fecha}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(reporte)
    
    # Sync to Android
    import subprocess
    destino = f"/sdcard/Documents/WhatsApp Resumenes/Reporte_{fecha}.md"
    subprocess.run(["shizuku", "sh", "-c", f'cp "{path}" "{destino}"'], 
                   capture_output=True, timeout=10)
    
    print(f"📄 Reporte guardado: Reporte_{fecha}.md")
    return reporte


if __name__ == "__main__":
    reporte = generar_reporte()
    print(reporte)
    guardar_reporte(reporte)
