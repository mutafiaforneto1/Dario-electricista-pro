#!/usr/bin/env python3
"""
ClickUp Duplicate Cleaner
Cierra tareas duplicadas, dejando solo la más reciente de cada grupo.
Uso: python3 clickup_limpiar_duplicados.py [--dry-run]
"""
import os, sys, requests
from collections import defaultdict

TOKEN = os.environ.get("CLICKUP_TOKEN", "os.environ.get("CLICKUP_TOKEN", "")")
HEADERS = {"Authorization": TOKEN, "Content-Type": "application/json"}
DRY_RUN = "--dry-run" in sys.argv

# Listas a revisar
LISTS = [
    "901714935828",  # 📋 Trabajos
    "901714936090",  # 👥 Clientes
]

def get_tasks(list_id):
    r = requests.get(f"https://api.clickup.com/api/v2/list/{list_id}/task", headers=HEADERS)
    return r.json().get("tasks", [])

def normalize(name):
    """Normaliza nombre para comparar duplicados"""
    import re
    n = name.lower().strip()
    # Quitar emojis y timestamps
    n = re.sub(r'[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B50]', '', n)
    n = re.sub(r'\d{2}/\d{2}\s*\d{2}:\d{2}', '', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n

def main():
    closed = 0
    for list_id in LISTS:
        tasks = get_tasks(list_id)
        open_tasks = [t for t in tasks if not t.get("date_closed") and not t.get("archived")]
        
        groups = defaultdict(list)
        for t in open_tasks:
            key = normalize(t["name"])
            groups[key].append(t)
        
        for key, group in groups.items():
            if len(group) <= 1:
                continue
            # Ordenar por fecha de creación, más reciente primero
            group.sort(key=lambda t: int(t.get("date_created", 0)), reverse=True)
            keep = group[0]
            duplicates = group[1:]
            
            print(f"\n📌 '{keep['name'][:50]}' (KEEP)")
            for dup in duplicates:
                print(f"   ❌ '{dup['name'][:50]}' (CLOSE)")
                if not DRY_RUN:
                    requests.put(
                        f"https://api.clickup.com/api/v2/task/{dup['id']}",
                        headers=HEADERS,
                        json={"status": "closed"}
                    )
                closed += 1
    
    print(f"\n{'[DRY RUN] ' if DRY_RUN else ''}Total cerradas: {closed}")

if __name__ == "__main__":
    main()
