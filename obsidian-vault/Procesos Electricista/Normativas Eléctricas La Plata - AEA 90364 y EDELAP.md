
# Normativas Eléctricas La Plata (AEA 90364, Ley Prov. 10.502, EDELAP)

Este documento resume los requisitos normativos clave para instalaciones eléctricas en La Plata, Buenos Aires, exigidos por la AEA 90364, la Ley Provincial 10.502 y la distribuidora EDELAP.

## 1. Reglamento AEA 90364 (Ejecución de Trabajos en Inmuebles)

La norma base para la seguridad y correcta ejecución de instalaciones eléctricas. Cumple con los siguientes puntos esenciales:

*   **Protección contra Choques Eléctricos:**
    *   **Interruptor Diferencial (ID):** Uso obligatorio de un ID de 30 mA para proteger contra contactos indirectos (fugas a tierra). Se recomienda su uso también para contactos directos en ciertas condiciones.
    *   **Interruptores Termomagnéticos:** Protección contra sobrecargas y cortocircuitos, dimensionados correctamente según la carga y la sección del cableado.

*   **Protección contra Efectos Térmicos:**
    *   **Sección de Conductores:** Utilización de cables con la sección adecuada para la corriente nominal del circuito, evitando sobrecalentamientos.

*   **Puesta a Tierra:**
    *   **Instalación de Jabalina:** Obligatoriedad de contar con una jabalina de puesta a tierra.
    *   **Resistencia de Puesta a Tierra:** La resistencia del sistema de puesta a tierra debe cumplir con los valores especificados por la AEA 90364 (generalmente <10 Ohms, pero puede variar según la aplicación).

*   **Continuidad de las Masa:** Asegurar la conexión equipotencial de todas las partes conductoras expuestas.

## 2. Requisitos Locales (Ley Provincial 10.502 y EDELAP)

Además de la AEA 90364, para la habilitación de suministros y cumplimiento general, se deben considerar:

*   **Certificación Profesional:** Todo trabajo de instalación, modificación o reparación eléctrica debe ser certificado por un **electricista matriculado** ante el Colegio de Técnicos o el Colegio de Ingenieros de la Provincia de Buenos Aires. La certificación garantiza que la instalación cumple con las normativas vigentes.

*   **Materiales Certificados:** Todos los materiales eléctricos (cables, interruptores, tomas, cajas, etc.) deben contar con la **certificación IRAM** o de organismos de certificación reconocidos, garantizando su calidad y seguridad.

*   **Habilitación de Suministro (EDELAP):** Para nuevos suministros o modificaciones, EDELAP requiere la presentación de un plano de instalación eléctrica firmado por un profesional matriculado y el cumplimiento de los puntos anteriores. La inspección de EDELAP verificará la correcta ejecución y seguridad de la instalación.

## Consideraciones Adicionales:

*   **Documentación:** Mantener un registro de las certificaciones, planos y memorias técnicas de las instalaciones.
*   **Actualización:** Estar al tanto de las actualizaciones de la normativa AEA y las directivas de EDELAP y el OCEBA.

### Ejemplo de Dataview para esta nota:
```dataview
TABLE WITHOUT ID
    file.link AS "Normativa",
    length(file.lists) AS "Puntos Clave"
FROM "Procesos Electricista"
WHERE contains(file.name, "Normativas Eléctricas La Plata")
```

### Ejemplo de Templater para esta nota:
```templater
---
creation_date: <% tp.date("dd-MM-YYYY HH:mm") %>
tags: [normativa, LaPlata, AEA90364, EDELAP, OCEBA, matriculacion]
---

# <%= tp.file.title %>

## 1. Reglamento AEA 90364 (Ejecución de Trabajos en Inmuebles)

La norma base para la seguridad y correcta ejecución de instalaciones eléctricas. Cumple con los siguientes puntos esenciales:

*   **Protección contra Choques Eléctricos:**
    *   **Interruptor Diferencial (ID):** Uso obligatorio de un ID de 30 mA para proteger contra contactos indirectos (fugas a tierra). Se recomienda su uso también para contactos directos en ciertas condiciones.
    *   **Interruptores Termomagnéticos:** Protección contra sobrecargas y cortocircuitos, dimensionados correctamente según la carga y la sección del cableado.

*   **Protección contra Efectos Térmicos:**
    *   **Sección de Conductores:** Utilización de cables con la sección adecuada para la corriente nominal del circuito, evitando sobrecalentamientos.

*   **Puesta a Tierra:**
    *   **Instalación de Jabalina:** Obligatoriedad de contar con una jabalina de puesta a tierra.
    *   **Resistencia de Puesta a Tierra:** La resistencia del sistema de puesta a tierra debe cumplir con los valores especificados por la AEA 90364 (generalmente <10 Ohms, pero puede variar según la aplicación).

*   **Continuidad de las Masa:** Asegurar la conexión equipotencial de todas las partes conductoras expuestas.

## 2. Requisitos Locales (Ley Provincial 10.502 y EDELAP)

Además de la AEA 90364, para la habilitación de suministros y cumplimiento general, se deben considerar:

*   **Certificación Profesional:** Todo trabajo de instalación, modificación o reparación eléctrica debe ser certificado por un **electricista matriculado** ante el Colegio de Técnicos o el Colegio de Ingenieros de la Provincia de Buenos Aires. La certificación garantiza que la instalación cumple con las normativas vigentes.

*   **Materiales Certificados:** Todos los materiales eléctricos (cables, interruptores, tomas, cajas, etc.) deben contar con la **certificación IRAM** o de organismos de certificación reconocidos, garantizando su calidad y seguridad.

*   **Habilitación de Suministro (EDELAP):** Para nuevos suministros o modificaciones, EDELAP requiere la presentación de un plano de instalación eléctrica firmado por un profesional matriculado y el cumplimiento de los puntos anteriores. La inspección de EDELAP verificará la correcta ejecución y seguridad de la instalación.

## Consideraciones Adicionales:

*   **Documentación:** Mantener un registro de las certificaciones, planos y memorias técnicas de las instalaciones.
*   **Actualización:** Estar al tanto de las actualizaciones de la normativa AEA y las directivas de EDELAP y el OCEBA.

```
