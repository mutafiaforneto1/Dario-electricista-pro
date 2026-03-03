
# Fugas de Corriente

## Problemática:

Detectar y solucionar fugas de corriente en instalaciones eléctricas.

## Causas Comunes:

*   Aislamiento dañado en cables.
*   Conexiones defectuosas o sueltas.
*   Humedad o agua en cajas de conexión o equipos.
*   Equipos eléctricos con fallos internos.
*   Instalaciones antiguas o no conformes a normativa.

## Procedimiento de Diagnóstico:

1.  **Verificación Visual:** Inspeccionar cables, enchufes, interruptores y equipos en busca de signos de daño, quemaduras o corrosión.
2.  **Uso de Megóhmetro (Telurómetro):**
    *   Medir la resistencia de aislamiento entre fases, fase y neutro, y fase/neutro contra tierra.
    *   Comparar los valores obtenidos con los de la normativa vigente (ej. UNE-HD 60364).
3.  **Prueba con Pinza Amperimétrica:**
    *   Utilizar una pinza de fuga para medir la corriente que retorna por el conductor de protección (tierra) sin carga. Un valor anómalo indica fuga.
    *   Realizar la prueba desconectando cargas una a una para aislar el circuito o equipo problemático.
4.  **Revisión de Interruptores Diferenciales (ID):**
    *   Verificar si el ID salta sin carga. Si es así, indica una fuga significativa.
    *   Comprobar el valor de la corriente diferencial residual con una pinza específica si se sospecha de un valor cercano al umbral del ID.

## Soluciones:

*   **Reparación/Reemplazo de Cables:** Sustituir tramos de cable con aislamiento dañado.
*   **Apretar Conexiones:** Asegurar todas las conexiones en cajas de empalme, bornes y terminales.
*   **Secado y Sellado:** En caso de humedad, secar la zona y aplicar selladores adecuados.
*   **Reemplazo de Equipos:** Sustituir equipos eléctricos que presenten fallos internos.
*   **Actualización de Instalación:** Si la instalación es muy antigua, considerar una renovación parcial o total.
*   **Optimización de Puesta a Tierra:** Asegurar una correcta y eficiente conexión a tierra.

## Consideraciones Adicionales:

*   Siempre trabajar con la instalación desenergizada al realizar reparaciones.
*   Utilizar equipos de protección personal (EPP) adecuados.
*   Documentar las mediciones y acciones tomadas.

## Dataview Example:
```dataview
TABLE WITHOUT ID
    file.link AS "Procedimiento",
    length(file.lists) AS "Pasos"
FROM "Procesos Electricista"
WHERE contains(file.name, "Fugas de Corriente")
```

## Templater Example:
```templer
---
creation_date: <% tp.date("dd-MM-YYYY HH:mm") %>
tags: [electricista, procedimiento, fuga_corriente]
---

# <%= tp.file.title %>

## Problemática:
Detectar y solucionar fugas de corriente en instalaciones eléctricas.

## Causas Comunes:
* Aislamiento dañado en cables.
* Conexiones defectuosas o sueltas.
* Humedad o agua en cajas de conexión o equipos.
* Equipos eléctricos con fallos internos.
* Instalaciones antiguas o no conformes a normativa.

## Procedimiento de Diagnóstico:
1. **Verificación Visual:** Inspeccionar cables, enchufes, interruptores y equipos en busca de signos de daño, quemaduras o corrosión.
2. **Uso de Megóhmetro (Telurómetro):**
    * Medir la resistencia de aislamiento entre fases, fase y neutro, y fase/neutro contra tierra.
    * Comparar los valores obtenidos con los de la normativa vigente (ej. UNE-HD 60364).
3. **Prueba con Pinza Amperimétrica:**
    * Utilizar una pinza de fuga para medir la corriente que retorna por el conductor de protección (tierra) sin carga. Un valor anómalo indica fuga.
    * Realizar la prueba desconectando cargas una a una para aislar el circuito o equipo problemático.
4. **Revisión de Interruptores Diferenciales (ID):**
    * Verificar si el ID salta sin carga. Si es así, indica una fuga significativa.
    * Comprobar el valor de la corriente diferencial residual con una pinza específica si se sospecha de un valor cercano al umbral del ID.

## Soluciones:
* **Reparación/Reemplazo de Cables:** Sustituir tramos de cable con aislamiento dañado.
* **Apretar Conexiones:** Asegurar todas las conexiones en cajas de empalme, bornes y terminales.
* **Secado y Sellado:** En caso de humedad, secar la zona y aplicar selladores adecuados.
* **Reemplazo de Equipos:** Sustituir equipos eléctricos que presenten fallos internos.
* **Actualización de Instalación:** Si la instalación es muy antigua, considerar una renovación parcial o total.
* **Optimización de Puesta a Tierra:** Asegurar una correcta y eficiente conexión a tierra.

## Consideraciones Adicionales:
* Siempre trabajar con la instalación desenergizada al realizar reparaciones.
* Utilizar equipos de protección personal (EPP) adecuados.
* Documentar las mediciones y acciones tomadas.

```
