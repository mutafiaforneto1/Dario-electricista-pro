
# Sobrecarga de Circuitos

## Problemática:

Identificar y solucionar causas de sobrecarga en circuitos eléctricos.

## Causas Comunes:

*   Conexión de demasiados aparatos a un mismo circuito.
*   Uso de aparatos de alta potencia simultáneamente.
*   Cables de sección insuficiente para la carga.
*   Cortocircuitos parciales.
*   Mal funcionamiento de interruptores automáticos.

## Procedimiento de Diagnóstico:

1.  **Análisis de Cargas Conectadas:**
    *   Identificar todos los aparatos conectados al circuito en cuestión.
    *   Verificar la potencia nominal de cada aparato.
    *   Sumar la potencia total y compararla con la capacidad del circuito (disyuntor y cableado).
2.  **Revisión del Disyuntor:**
    *   Comprobar el calibre del disyuntor (ej. 10A, 16A, 20A) y compararlo con la carga total esperada y la sección del cable.
    *   Observar si el disyuntor se dispara frecuentemente, especialmente al encender ciertos aparatos.
3.  **Medición de Corriente:**
    *   Utilizar una pinza amperimétrica para medir la corriente real que circula por el circuito bajo carga.
    *   Comparar la corriente medida con el calibre del disyuntor y la capacidad admisible del cable.
4.  **Inspección del Cableado:**
    *   Verificar la sección del cableado para asegurar que sea adecuada para la corriente que debe transportar.
    *   Buscar signos de sobrecalentamiento en el cableado, empalmes o terminales.

## Soluciones:

*   **Redistribución de Cargas:** Mover algunos aparatos a otros circuitos menos cargados.
*   **Instalación de Circuitos Adicionales:** Si es necesario, instalar nuevos circuitos para cargas de alta potencia o para repartir la carga de forma más equitativa.
*   **Reemplazo de Cables:** Utilizar cables de mayor sección si los actuales son insuficientes.
*   **Reemplazo del Disyuntor:** Instalar un disyuntor con el calibre adecuado (nunca uno de mayor calibre que el cableado admita).
*   **Reparación de Cortocircuitos:** Localizar y reparar cualquier cortocircuito parcial.

## Consideraciones Adicionales:

*   Explicar al cliente las razones de la sobrecarga y las soluciones recomendadas.
*   Asegurar el cumplimiento de la normativa eléctrica vigente.

## Dataview Example:
```dataview
TABLE WITHOUT ID
    file.link AS "Procedimiento",
    length(file.lists) AS "Pasos"
FROM "Procesos Electricista"
WHERE contains(file.name, "Sobrecarga de Circuitos")
```

## Templater Example:
```templer
---
creation_date: <% tp.date("dd-MM-YYYY HH:mm") %>
tags: [electricista, procedimiento, sobrecarga]
---

# <%= tp.file.title %>

## Problemática:
Identificar y solucionar causas de sobrecarga en circuitos eléctricos.

## Causas Comunes:
* Conexión de demasiados aparatos a un mismo circuito.
* Uso de aparatos de alta potencia simultáneamente.
* Cables de sección insuficiente para la carga.
* Cortocircuitos parciales.
* Mal funcionamiento de interruptores automáticos.

## Procedimiento de Diagnóstico:
1. **Análisis de Cargas Conectadas:**
    * Identificar todos los aparatos conectados al circuito en cuestión.
    * Verificar la potencia nominal de cada aparato.
    * Sumar la potencia total y compararla con la capacidad del circuito (disyuntor y cableado).
2. **Revisión del Disyuntor:**
    * Comprobar el calibre del disyuntor (ej. 10A, 16A, 20A) y compararlo con la carga total esperada y la sección del cable.
    * Observar si el disyuntor se dispara frecuentemente, especialmente al encender ciertos aparatos.
3. **Medición de Corriente:**
    * Utilizar una pinza amperimétrica para medir la corriente real que circula por el circuito bajo carga.
    * Comparar la corriente medida con el calibre del disyuntor y la capacidad admisible del cable.
4. **Inspección del Cableado:**
    * Verificar la sección del cableado para asegurar que sea adecuada para la corriente que debe transportar.
    * Buscar signos de sobrecalentamiento en el cableado, empalmes o terminales.

## Soluciones:
* **Redistribución de Cargas:** Mover algunos aparatos a otros circuitos menos cargados.
* **Instalación de Circuitos Adicionales:** Si es necesario, instalar nuevos circuitos para cargas de alta potencia o para repartir la carga de forma más equitativa.
* **Reemplazo de Cables:** Utilizar cables de mayor sección si los actuales son insuficientes.
* **Reemplazo del Disyuntor:** Instalar un disyuntor con el calibre adecuado (nunca uno de mayor calibre que el cableado admita).
* **Reparación de Cortocircuitos:** Localizar y reparar cualquier cortocircuito parcial.

## Consideraciones Adicionales:
* Explicar al cliente las razones de la sobrecarga y las soluciones recomendadas.
* Asegurar el cumplimiento de la normativa eléctrica vigente.

```
