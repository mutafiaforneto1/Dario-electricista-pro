#!/usr/bin/env python3
"""
Calculadora Eléctrica para Darío Electricista
==============================================
Cálculos rápidos para presupuestos y trabajos.

Uso:
  python3 calculadora_electrica.py cable 20 380 10     # Calibre por longitud
  python3 calculadora_electrica.py caida 2.5 20 16     # Caída de tensión
  python3 calculadora_electrica.py potencia 220 10     # Potencia máxima
  python3 calculadora_electrica.py toma 220 20         # Toma por amperaje
  python3 calculadora_electrica.py acometida 50 220    # Acometida por carga
  python3 calculadora_electrica.py tablero 3           # Tablero por circuitos
"""
import sys
import math

# ═══ CONSTANTES ═══════════════════════════════════════════════════════════════
# Conductividad del cobre (m/Ω·mm²)
CONDUCTIVIDAD_COBRE = 58.0

# Secciones de cable estándar (mm²)
SECCIONES = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240]

# Corrientes máximas por calibre (A) - instalación abierta
CORRIENTES_MAX = {
    1.5: 14, 2.5: 20, 4: 28, 6: 36, 10: 50,
    16: 68, 25: 89, 35: 110, 50: 135, 70: 170,
    95: 205, 120: 240, 150: 275, 185: 315, 240: 380
}

# Caída de tensión máxima permitida (%)
CAIDA_MAX_PCT = 3.0  # 3% para iluminación, 5% para fuerza

# ═══ FUNCIONES ════════════════════════════════════════════════════════════════

def calcular_calibre(corriente, longitud, voltaje=220, caida_max=3.0):
    """Calcula el calibre de cable necesario"""
    caida_tension = voltaje * (caida_max / 100)
    
    print(f"\n📐 CÁLCULO DE CALIBRE DE CABLE")
    print(f"{'='*50}")
    print(f"Corriente:      {corriente} A")
    print(f"Longitud:       {longitud} m")
    print(f"Voltaje:        {voltaje} V")
    print(f"Máx caída:      {caida_max}%")
    print(f"{'='*50}")
    
    # Calcular sección mínima por caída de tensión
    # R = V / I → R = ρL/S → S = ρLI/V
    seccion_min = (CONDUCTIVIDAD_COBRE * corriente * longitud) / (caida_tension * 1000)
    
    # Buscar sección estándar
    seccion_adecuada = None
    for s in SECCIONES:
        if s >= seccion_min and CORRIENTES_MAX.get(s, 0) >= corriente:
            seccion_adecuada = s
            break
    
    # Si no encontró, buscar la que cumpla corriente
    if not seccion_adecuada:
        for s in SECCIONES:
            if CORRIENTES_MAX.get(s, 0) >= corriente:
                seccion_adecuada = s
                break
    
    if seccion_adecuada:
        caida_real = (CONDUCTIVIDAD_COBRE * corriente * longitud) / (seccion_adecuada * voltaje * 1000) * 100
        corriente_max = CORRIENTES_MAX.get(seccion_adecuada, 0)
        
        print(f"\n✅ RESULTADO:")
        print(f"Sección mínima:  {seccion_min:.2f} mm²")
        print(f"Calibre sugerido:{seccion_adecuada} mm²")
        print(f"Corriente máx:   {corriente_max} A")
        print(f"Caída real:      {caida_real:.2f}%")
        
        if caida_real <= caida_max:
            print(f"Estado:          ✅ ACEPTABLE")
        else:
            print(f"Estado:          ⚠️ EXCEDE LÍMITE")
        
        # Precio estimado
        precio_metro = {1.5: 987, 2.5: 1500, 4: 2200, 6: 3000, 10: 5000}
        precio = precio_metro.get(seccion_adecuada, 0)
        if precio:
            print(f"Precio estimado: ${precio}/m (${precio * longitud:.0f} total)")
    else:
        print(f"\n❌ No se encontró calibre adecuado")
    
    return seccion_adecuada

def calcular_caida_tension(seccion, longitud, corriente, voltaje=220):
    """Calcula la caída de tensión"""
    print(f"\n📉 CAÍDA DE TENSIÓN")
    print(f"{'='*50}")
    print(f"Sección:        {seccion} mm²")
    print(f"Longitud:       {longitud} m")
    print(f"Corriente:      {corriente} A")
    print(f"Voltaje:        {voltaje} V")
    print(f"{'='*50}")
    
    # R = ρL/S (en ohmios por km)
    resistencia_km = longitud / (CONDUCTIVIDAD_COBRE * seccion)  # Ω/km
    resistencia_m = resistencia_km / 1000  # Ω/m
    
    # V = IR
    caida_v = corriente * resistencia_m * longitud
    caida_pct = (caida_v / voltaje) * 100
    
    print(f"\n✅ RESULTADO:")
    print(f"Resistencia:    {resistencia_km:.4f} Ω/km")
    print(f"Caída voltaje:  {caida_v:.2f} V")
    print(f"Caída %:        {caida_pct:.2f}%")
    
    if caida_pct <= CAIDA_MAX_PCT:
        print(f"Estado:         ✅ ACEPTABLE (≤{CAIDA_MAX_PCT}%)")
    elif caida_pct <= 5:
        print(f"Estado:         ⚠️ LÍMITE (≤5%)")
    else:
        print(f"Estado:         ❌ EXCEDE LÍMITE")
    
    # Voltaje en destino
    voltaje_destino = voltaje - caida_v
    print(f"Voltaje destino:{voltaje_destino:.2f} V")
    
    return caida_pct

def calcular_potencia(voltaje, corriente, fp=0.9):
    """Calcula potencia"""
    print(f"\n⚡ CÁLCULO DE POTENCIA")
    print(f"{'='*50}")
    print(f"Voltaje:        {voltaje} V")
    print(f"Corriente:      {corriente} A")
    print(f"FP:             {fp}")
    print(f"{'='*50}")
    
    potencia_w = voltaje * corriente * fp
    potencia_kw = potencia_w / 1000
    
    print(f"\n✅ RESULTADO:")
    print(f"Potencia activa:{potencia_w:.0f} W")
    print(f"                {potencia_kw:.2f} kW")
    print(f"                {potencia_kw * 1.36:.2f} CV")
    
    return potencia_w

def calcular_toma(voltaje, amperaje):
    """Calcula especificaciones de toma"""
    print(f"\n🔌 ESPECIFICACIONES DE TOMA")
    print(f"{'='*50}")
    print(f"Voltaje:        {voltaje} V")
    print(f"Amperaje:       {amperaje} A")
    print(f"{'='*50}")
    
    # Calibre mínimo
    for s, i in CORRIENTES_MAX.items():
        if i >= amperaje:
            calibre = s
            break
    
    # Potencia máxima
    potencia = voltaje * amperaje
    
    # Disyuntor sugerido
    disyuntor = amperaje * 1.25  # 25% más
    
    print(f"\n✅ RESULTADO:")
    print(f"Calibre mínimo: {calibre} mm²")
    print(f"Potencia máx:   {potencia} W")
    print(f"Disyuntor:      {disyuntor:.0f} A (sugerido)")
    print(f"Toma:           {amperaje}A {voltaje}V")
    
    return calibre

def calcular_acometida(carga_total, voltaje=220):
    """Calcula acometida necesaria"""
    print(f"\n🏠 CÁLCULO DE ACOMETIDA")
    print(f"{'='*50}")
    print(f"Carga total:    {carga_total} W")
    print(f"Voltaje:        {voltaje} V")
    print(f"{'='*50}")
    
    # Corriente total
    corriente = carga_total / voltaje
    
    # Calibre acometida
    for s, i in CORRIENTES_MAX.items():
        if i >= corriente * 1.25:  # 25% margen
            calibre = s
            break
    
    # Disyuntor general
    disyuntor = corriente * 1.25
    
    print(f"\n✅ RESULTADO:")
    print(f"Corriente:      {corriente:.1f} A")
    print(f"Calibre:        {calibre} mm²")
    print(f"Disyuntor:      {disyuntor:.0f} A")
    
    return calibre

def calcular_tablero(num_circuitos):
    """Calcula componentes del tablero"""
    print(f"\n🔌 CÁLCULO DE TABLERO")
    print(f"{'='*50}")
    print(f"Circuitos:      {num_circuitos}")
    print(f"{'='*50}")
    
    # Espacios necesarios (2 por disyuntor + 1 general)
    espacios = (num_circuitos * 2) + 2
    
    # Tamaño sugerido
    if espacios <= 8:
        tamano = "Pequeño (8 módulos)"
    elif espacios <= 12:
        tamano = "Mediano (12 módulos)"
    elif espacios <= 16:
        tamano = "Grande (16 módulos)"
    else:
        tamano = f"Industrial ({espacios} módulos)"
    
    print(f"\n✅ RESULTADO:")
    print(f"Espacios:       {espacios}")
    print(f"Disyuntor gen:  1 × 25A")
    print(f"Térmicas:       {num_circuitos} × 20A")
    print(f"Tamaño:         {tamano}")
    
    return tamano

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    comando = sys.argv[1].lower()
    
    if comando == "cable" and len(sys.argv) >= 5:
        corriente = float(sys.argv[2])
        longitud = float(sys.argv[3])
        voltaje = float(sys.argv[4]) if len(sys.argv) > 4 else 220
        calcular_calibre(corriente, longitud, voltaje)
    
    elif comando == "caida" and len(sys.argv) >= 5:
        seccion = float(sys.argv[2])
        longitud = float(sys.argv[3])
        corriente = float(sys.argv[4])
        voltaje = float(sys.argv[5]) if len(sys.argv) > 5 else 220
        calcular_caida_tension(seccion, longitud, corriente, voltaje)
    
    elif comando == "potencia" and len(sys.argv) >= 4:
        voltaje = float(sys.argv[2])
        corriente = float(sys.argv[3])
        calcular_potencia(voltaje, corriente)
    
    elif comando == "toma" and len(sys.argv) >= 4:
        voltaje = float(sys.argv[2])
        amperaje = float(sys.argv[3])
        calcular_toma(voltaje, amperaje)
    
    elif comando == "acometida" and len(sys.argv) >= 3:
        carga = float(sys.argv[2])
        voltaje = float(sys.argv[3]) if len(sys.argv) > 3 else 220
        calcular_acometida(carga, voltaje)
    
    elif comando == "tablero" and len(sys.argv) >= 3:
        num = int(sys.argv[2])
        calcular_tablero(num)
    
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
