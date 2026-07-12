#!/usr/bin/env python3
"""
ClickUp Presupuesto Search
Busca presupuestos en ClickUp por cliente, monto o fecha.
Uso: python3 clickup_buscar_presupuestos.py [búsqueda]
Ejemplos:
  python3 clickup_buscar_presupuestos.py mica
  python3 clickup_buscar_presupuestos.py 336
  python3 clickup_buscar_presupuestos.py presupuesto
"""
import os, sys, requests, re
from datetime import datetime

TOKEN = os.environ.get("CLICKUP_TOKEN", "os.environ.get("CLICKUP_TOKEN", "")")
HEADERS = {"Authorization": TOKEN}
LISTA_TRABAJOS = "901714935828"

def search(query=""):
    r = requests.get(
        f"https://api.clickup.com/api/v2/list/{LISTA_TRABAJOS}/task",
        headers=HEADERS,
        params={"include_closed": "true"}
    )
    tasks = r.json().get("tasks", [])
    
    results = []
    for t in tasks:
        name = t["name"]
        desc = t.get("text_content", "") or t.get("description", "") or ""
        combined = f"{name} {desc}".lower()
        
        if not query or query.lower() in combined:
            results.append(t)
    
    if not results:
        print(f"No se encontraron resultados para '{query}'")
        return
    
    print(f"📋 {len(results)} resultado(s) para '{query}':\n")
    for t in results:
        status = "✅" if t.get("date_closed") else "🔵"
        due = ""
        if t.get("due_date"):
            due = f" | vence: {datetime.fromtimestamp(int(t['due_date'])/1000).strftime('%d/%m')}"
        
        # Buscar monto en el nombre o descripción
        desc = t.get("text_content", "") or ""
        monto_match = re.search(r'\$[\d.,]+', f"{t['name']} {desc}")
        monto = f" | {monto_match.group()}" if monto_match else ""
        
        print(f"{status} {t['name'][:60]}")
        print(f"   ID: {t['id']}{due}{monto}")
        print(f"   URL: {t.get('url', 'N/A')}")
        print()

if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    search(query)
