---
name: dario-electricista
description: >
  Sistema de gestión para Darío, electricista en La Plata.
  Procesa notificaciones de WhatsApp Business (vía MacroDroid + Groq IA),
  gestiona clientes y trabajos en ClickUp, genera presupuestos,
  y administra contactos. Usar cuando Darío pregunte sobre:
  clientes, presupuestos, trabajos, mensajes de WhatsApp, tareas de ClickUp,
  precios/tarifas, o gestión del negocio eléctrico.
---

# Darío Electricista - Sistema de Gestión

## Contexto
- **Nombre:** Darío Díaz Gonzalez
- **Rubro:** Electricista en La Plata, Buenos Aires
- **Novia:** Carolina (contacto personal ❤️)
- **Hijos:** Evita<3, Francisco (school contacts 🏫)
- **Idioma:** Español argentino, tono casual/amistoso

## Arquitectura del Sistema

```
MacroDroid → /sdcard/whatsapp_trabajos.log
  → Groq IA (resumen)
  → ClickUp (tareas por contacto)
  → /sdcard/Documents/WhatsApp Resumenes/ (archivos por contacto)
```

## ClickUp Workspace

- **Team Space ID:** 90175555536
- **Folder:** ⚡ Electricista La Plata (90179652315)

### Listas Principales
| Lista | ID | Uso |
|-------|-----|-----|
| 📋 Trabajos | 901714935828 | Trabajos activos y presupuestos |
| 👥 Clientes | 901714936090 | Registro de clientes |
| 💰 Tarifas de Referencia | 901714936121 | Precios de materiales y servicios |
| ✅ Trabajos Completados | 901714936124 | Historial de trabajos |
| ❤️ Carolina | 901714997413 | Contacto personal |
| 🏫 Escuela (Eva y Fran) | 901714997484 | Grupos escolares |
| 🏫 6° 5° - Familias | 901714999529 | Grupo escolar |
| 🏫 2do 1ra | 901714999530 | Grupo escolar |

### Campos Customizados
| Campo | ID | Tipo |
|-------|-----|------|
| Dirección | 3fd8fe05-7a43-4b22-abf2-c1a2e21c5fdf | short_text |
| Monto Cobrado | 724140ff-981b-4da7-8cde-3c9900196220 | currency (ARS) |
| Teléfono | 74257df9-3d0f-438b-bd73-15a2f15e5cf1 | phone |
| 🏞️ Zona | 0e343b1a-0f44-4b4b-9156-460dc37b542e | dropdown |

## Mapeo de Contactos WhatsApp → ClickUp

| Patrón | Lista | Categoría | Emoji |
|--------|-------|-----------|-------|
| carolina | ❤️ Carolina | personal | ❤️ |
| claudia | 👥 Clientes | cliente | 👤 |
| evita | 🏫 Escuela | familia | 👧 |
| francisco | 🏫 Escuela | familia | 👦 |
| jess | 👥 Clientes | cliente | 👤 |
| romina arias | 👥 Clientes | cliente | 👤 |
| media 26 | 🏫 6° 5° | escuela | 🏫 |
| 6° 5° | 🏫 6° 5° | escuela | 🏫 |
| 2do 1ra | 🏫 2do 1ra | escuela | 🏫 |

**Ignorar:** whatsapp business, copia de seguridad, tú, llamadas, sistema

## Tarifas de Referencia (actualizado 04/07)

### Servicios
| Servicio | Precio |
|----------|--------|
| Boca eléctrica (térmica o disyuntor) | $90.000 |
| Visita para presupuesto | $20.000 (se descuenta si se concreta) |
| Media jornada | Desde $45.000 |
| Jornada completa | Desde $90.000 |
| Instalación grande (1-2 días) | Desde $80.000 |
| Urgencia | $80.000 |

### Materiales (referencia)
| Material | Precio |
|----------|--------|
| Cable unipolar 2.5mm x metro | ~$987 |
| Cable canal 20x10mm c/adhesivo x metro | ~$1.720 |
| Bastidor oculto rectangular | ~$412 |
| Tapa rectangular blanca | ~$451 |
| Módulo 2 tomas + tierra | ~$2.220 |
| Caja rectangular cable canal | ~$1.586 |

## Generación de Presupuestos

Cuando Darío pida armar un presupuesto:

1. **Buscar datos del cliente** en ClickUp (lista 👥 Clientes)
2. **Consultar tarifas** en lista 💰 Tarifas de Referencia
3. **Armar presupuesto** con estructura:
   - Datos del cliente (nombre, teléfono, dirección)
   - Descripción del trabajo (detallada)
   - Materiales (con cantidades y precios)
   - Mano de obra (detallada por concepto)
   - Resumen total con descuento de visita si aplica
   - Condiciones (validez, pago, plazo)
   - Aceptación del cliente
4. **Crear tarea en ClickUp** (lista 📋 Trabajos)
5. **Generar mensaje WhatsApp** listo para enviar

### Plantilla de Presupuesto
Ver `assets/presupuesto_template.md`

## API Keys (NO committing a repos)

Las keys están en variables de entorno o en el dispositivo:
- **ClickUp:** `YOUR_CLICKUP_TOKEN`
- **Groq:** `YOUR_GROQ_TOKEN`
- **Telegram Bot:** `YOUR_TELEGRAM_TOKEN`
- **Gemini:** `YOUR_GEMINI_TOKEN`
- **OpenRouter:** `YOUR_OPENROUTER_TOKEN`

## Scripts

### Procesador de WhatsApp
`scripts/procesar_whatsapp.py` - Lee el log de MacroDroid, resume con Groq, postea a ClickUp y guarda resúmenes visibles.

Uso:
```bash
python3 scripts/procesar_whatsapp.py          # Modo normal
python3 scripts/procesar_whatsapp.py --test   # Test sin guardar
python3 scripts/procesar_whatsapp.py --watch  # Loop cada 60s
```

## GitHub Backup
- **Repo:** `https://github.com/mutafiaforneto1/Dario-electricista-pro` (privado)
- Contiene: scripts, .env.example, README

## Scripts Adicionales

### Limpiar Duplicados de ClickUp
`scripts/clickup_limpiar_duplicados.py` - Cierra tareas duplicadas, dejando solo la más reciente.

```bash
python3 scripts/clickup_limpiar_duplicados.py --dry-run  # Ver qué se cerraría
python3 scripts/clickup_limpiar_duplicados.py             # Ejecutar limpieza
```

### Buscar Presupuestos
`scripts/clickup_buscar_presupuestos.py` - Busca presupuestos por cliente, monto o fecha.

```bash
python3 scripts/clickup_buscar_presupuestos.py mica       # Por cliente
python3 scripts/clickup_buscar_presupuestos.py 336        # Por monto
python3 scripts/clickup_buscar_presupuestos.py            # Listar todos
```
