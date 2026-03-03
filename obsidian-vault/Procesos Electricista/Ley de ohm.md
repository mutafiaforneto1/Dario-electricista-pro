---
Tension_V: 200
Corriente_A: 10
resistencia: "15"
---


```dataview
TABLE
    choice(Voltaje_V, Voltaje_V, round(Corriente_A * Resistencia_ohm, 2)) + " V" AS "Voltaje",
    choice(Corriente_A, Corriente_A, round(Voltaje_V / Resistencia_ohm, 2)) + " A" AS "Corriente",
    choice(Resistencia_ohm, Resistencia_ohm, round(Voltaje_V / Corriente_A, 2)) + " Ω" AS "Resistencia",
    round(
        choice(Voltaje_V, Voltaje_V, Corriente_A * Resistencia_ohm) * choice(Corriente_A, Corriente_A, Voltaje_V / Resistencia_ohm), 2
    ) + " W" AS "Potencia Total"
WHERE file.name = this.file.name
```