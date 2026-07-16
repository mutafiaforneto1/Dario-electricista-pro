#!/usr/bin/env python3
"""
Agente Monitor v2 - Reporte automático + Notificaciones + Análisis de rentabilidad
"""

import os, json, requests, subprocess
from datetime import datetime, timedelta

# Load tokens
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
GTASKS_TOKEN = None
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


def shizuku(cmd):
    try:
        r = subprocess.run(["shizuku", "sh", "-c", cmd], capture_output=True, text=True, timeout=15)
        return r.stdout
    except:
        return ""


def mandar_whatsapp(mensaje):
    """Send message via WhatsApp Business using MacroDroid's notification reply"""
    # Save to a file that can be read
    path = "/tmp/wa_send_queue.txt"
    with open(path, "a") as f:
        f.write(mensaje + "\n---\n")
    
    # Also try to send via termux-notification-reply if available
    try:
        subprocess.run(["termux-notification", "--title", "🤖 Agent Monitor", 
                       "--content", mensaje[:200]], capture_output=True, timeout=5)
    except:
        pass
    
    print(f"  📱 Mensaje encolado: {mensaje[:50]}...")


def notificar_urgente(alertas):
    """Send urgent notification via WhatsApp"""
    if not alertas:
        return
    
    msg = f"🤖 *ALERTA AGENTE MONITOR* - {datetime.now().strftime('%d/%m %H:%M')}\n\n"
    for alerta in alertas[:5]:
        msg += f"{alerta}\n"
    
    msg += f"\n📊 Resumen: {len(alertas)} alertas pendientes"
    msg += "\nRevisá la app para más detalles."
    
    mandar_whatsapp(msg)


def analisis_rentabilidad(completados):
    """Analyze profitability per job"""
    analisis = []
    
    for t in completados.get('tasks', []):
        name = t['name']
        monto_cobrado = 0
        for cf in t.get('custom_fields', []):
            if cf.get('name') == 'Monto Cobrado' and cf.get('value'):
                try:
                    monto_cobrado = float(cf['value'])
                except:
                    pass
        
        if monto_cobrado > 0:
            analisis.append({
                'nombre': name,
                'cobrado': monto_cobrado
            })
    
    return sorted(analisis, key=lambda x: x['cobrado'], reverse=True)


def generar_reporte():
    ahora = datetime.now()
    reporte = []
    alertas = []
    
    reporte.append(f"📊 REPORTE DIARIO - {ahora.strftime('%d/%m/%Y %H:%M')}")
    reporte.append("=" * 50)
    
    # ═══ AGENTE DE TRABAJOS ═══
    reporte.append("\n📋 AGENTE DE TRABAJOS:")
    reporte.append("-" * 30)
    
    tasks_data = cu("list/901714935828/task?include_closed=false&page=0")
    tasks = tasks_data.get('tasks', [])
    
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
                alertas.append(f"🔴 VENCIDO: {name[:40]} (hace {abs(dias)} días)")
            elif dias <= 2:
                proximos.append((name, status, due_dt.strftime('%d/%m'), dias))
                alertas.append(f"🟡 PRÓXIMO: {name[:40]} (vence {due_dt.strftime('%d/%m')})")
    
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
        if 'deuda' in name.lower() or 'debe' in desc:
            deudas.append(name)
            alertas.append(f"💰 DEUDA: {name[:40]}")
    
    if deudas:
        reporte.append(f"  💰 Deudas pendientes ({len(deudas)}):")
        for d in deudas:
            reporte.append(f"    🔴 {d[:50]}")
    else:
        reporte.append("  ✅ Sin deudas pendientes")
    
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
            alertas.append(f"📄 PRESUPUESTO: {title[:30]} - {estado}")
    
    if pendientes_pres:
        reporte.append(f"  📄 Pendientes ({len(pendientes_pres)}):")
        for title, estado, total in pendientes_pres:
            reporte.append(f"    📌 {title[:30]} - {estado} - ${total:,.0f}")
    else:
        reporte.append("  ✅ Sin presupuestos pendientes")
    
    # ═══ ANÁLISIS DE RENTABILIDAD ═══
    reporte.append("\n📈 ANÁLISIS DE RENTABILIDAD:")
    reporte.append("-" * 30)
    
    rentabilidad = analisis_rentabilidad(completados)
    total_cobrado = sum(r['cobrado'] for r in rentabilidad)
    
    if rentabilidad:
        reporte.append(f"  💰 Total facturado: ${total_cobrado:,.0f}")
        reporte.append(f"  📊 Promedio por trabajo: ${total_cobrado/len(rentabilidad):,.0f}")
        reporte.append(f"\n  Top 5 trabajos:")
        for r in rentabilidad[:5]:
            reporte.append(f"    💵 {r['nombre'][:35]} - ${r['cobrado']:,.0f}")
    else:
        reporte.append("  📊 Sin datos de rentabilidad")
    
    # ═══ AGENTE DE CLIENTES ═══
    reporte.append("\n👤 AGENTE DE CLIENTES:")
    reporte.append("-" * 30)
    
    clientes_data = cu("list/901714936090/task?include_closed=false&page=0")
    clientes = clientes_data.get('tasks', [])
    reporte.append(f"  📊 Total clientes activos: {len(clientes)}")
    
    # ═══ RESUMEN ═══
    reporte.append("\n" + "=" * 50)
    reporte.append("📝 RESUMEN EJECUTIVO:")
    
    if alertas:
        reporte.append(f"  ⚠️ {len(alertas)} alertas pendientes")
    else:
        reporte.append("  ✅ Todo en orden")
    
    if vencidos:
        reporte.append(f"  🔴 {len(vencidos)} trabajos vencidos")
    if proximos:
        reporte.append(f"  🟡 {len(proximos)} trabajos próximos a vencer")
    if deudas:
        reporte.append(f"  💰 {len(deudas)} cobros pendientes")
    
    reporte.append("=" * 50)
    
    # Send urgent notifications if there are critical alerts
    if alertas:
        notificar_urgente(alertas)
    
    return "\n".join(reporte), alertas


def guardar_reporte(reporte):
    ahora = datetime.now()
    fecha = ahora.strftime("%Y-%m-%d_%H%M")
    
    local_dir = "/tmp/wa_resumenes"
    os.makedirs(local_dir, exist_ok=True)
    
    path = os.path.join(local_dir, f"Reporte_{fecha}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(reporte)
    
    destino = f"/sdcard/Documents/WhatsApp Resumenes/Reporte_{fecha}.md"
    subprocess.run(["shizuku", "sh", "-c", f'cp "{path}" "{destino}"'], 
                   capture_output=True, timeout=10)
    
    # Also save as "latest"
    latest_path = os.path.join(local_dir, "Reporte_LATEST.md")
    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(reporte)
    subprocess.run(["shizuku", "sh", "-c", f'cp "{latest_path}" "/sdcard/Documents/WhatsApp Resumenes/Reporte_LATEST.md"'], 
                   capture_output=True, timeout=10)
    
    print(f"📄 Reporte guardado: Reporte_{fecha}.md")
    return reporte


if __name__ == "__main__":
    reporte, alertas = generar_reporte()
    print(reporte)
    guardar_reporte(reporte)
    
    if alertas:
        print(f"\n🚨 {len(alertas)} ALERTAS ENVIADAS")
    else:
        print("\n✅ Sin alertas")
