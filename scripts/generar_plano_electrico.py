#!/usr/bin/env python3
"""
Generador de Planos Eléctricos para Darío Electricista
Crea diagramas SVG con símbolos eléctricos estándar.

Uso:
  python3 generar_plano_electrico.py --tipo instalacion --archivo salida.svg
  python3 generar_plano_electrico.py --tipo tablero --archivo tablero.svg
  python3 generar_plano_electrico.py --tipo acometida --archivo acometida.svg
"""
import svgwrite
import argparse
import os

# Colores estándar
COLORS = {
    'fondo': '#FFFFFF',
    'pared': '#333333',
    'cable_fase': '#FF0000',
    'cable_neutro': '#0000FF',
    'cable_tierra': '#00AA00',
    'equipo': '#666666',
    'texto': '#000000',
    'fondo_panel': '#F0F0F0'
}

def crear_plano_instalacion(archivo, titulo="Plano Eléctrico", direccion=""):
    """Crea un plano de instalación básica con tomas y circuitos"""
    dwg = svgwrite.Drawing(archivo, size=('210mm', '297mm'), viewBox='0 0 595 842')
    
    # Fondo
    dwg.add(dwg.rect(insert=(0,0), size=('100%','100%'), fill=COLORS['fondo']))
    
    # Título
    dwg.add(dwg.text(titulo, insert=(50, 40), font_size=16, font_weight='bold', fill=COLORS['texto']))
    if direccion:
        dwg.add(dwg.text(direccion, insert=(50, 60), font_size=10, fill=COLORS['texto']))
    
    # Tablero
    tablero_x, tablero_y = 100, 150
    dwg.add(dwg.rect(insert=(tablero_x, tablero_y), size=(60, 80), 
                     fill=COLORS['fondo_panel'], stroke=COLORS['pared'], stroke_width=2))
    dwg.add(dwg.text("TABLERO", insert=(tablero_x+5, tablero_y+20), font_size=8, fill=COLORS['texto']))
    
    # Disyuntor
    dwg.add(dwg.text("DISY.", insert=(tablero_x+5, tablero_y+40), font_size=6, fill=COLORS['equipo']))
    dwg.add(dwg.line(start=(tablero_x+30, tablero_y+35), end=(tablero_x+30, tablero_y+55),
                    stroke=COLORS['cable_fase'], stroke_width=2))
    
    # Térmicas
    for i, (nombre, y_offset) in enumerate([("CASA", 60), ("AA", 70)]):
        dwg.add(dwg.text(f"T-{nombre}", insert=(tablero_x+5, tablero_y+y_offset), font_size=6, fill=COLORS['equipo']))
        dwg.add(dwg.circle(center=(tablero_x+40, tablero_y+y_offset-3), r=3,
                          fill='none', stroke=COLORS['cable_fase'], stroke_width=1.5))
    
    # Cable principal (desde tablero hacia afuera)
    cable_y = tablero_y + 40
    dwg.add(dwg.line(start=(tablero_x+60, cable_y), end=(tablero_x+200, cable_y),
                    stroke=COLORS['cable_fase'], stroke_width=2, stroke_dasharray="5,2"))
    dwg.add(dwg.text("Cable 6mm² (10m)", insert=(tablero_x+80, cable_y-5), font_size=7, fill=COLORS['equipo']))
    
    # Toma para AA
    toma_x, toma_y = tablero_x + 250, cable_y
    dwg.add(dwg.circle(center=(toma_x, toma_y), r=8, fill='none', stroke=COLORS['cable_fase'], stroke_width=2))
    dwg.add(dwg.text("TOMA 20A", insert=(toma_x-15, toma_y+20), font_size=7, fill=COLORS['texto']))
    dwg.add(dwg.text("(AA)", insert=(toma_x-5, toma_y+30), font_size=6, fill=COLORS['equipo']))
    
    # Cable al AA
    dwg.add(dwg.line(start=(tablero_x+60, cable_y+20), end=(toma_x-10, cable_y+20),
                    stroke=COLORS['cable_fase'], stroke_width=1.5))
    dwg.add(dwg.text("Cable 4mm² (6m)", insert=(tablero_x+100, cable_y+18), font_size=6, fill=COLORS['equipo']))
    
    # Cable canal
    dwg.add(dwg.rect(insert=(tablero_x+60, cable_y+15), size=(180, 10), 
                     fill='none', stroke=COLORS['equipo'], stroke_width=1, stroke_dasharray="2,2"))
    dwg.add(dwg.text("Cable canal 20x10mm", insert=(tablero_x+100, cable_y+35), font_size=6, fill=COLORS['equipo']))
    
    # Leyenda
    leyenda_y = 700
    dwg.add(dwg.text("LEYENDA:", insert=(50, leyenda_y), font_size=10, font_weight='bold', fill=COLORS['texto']))
    dwg.add(dwg.line(start=(50, leyenda_y+10), end=(80, leyenda_y+10), stroke=COLORS['cable_fase'], stroke_width=2))
    dwg.add(dwg.text("Fase", insert=(85, leyenda_y+13), font_size=8, fill=COLORS['texto']))
    
    dwg.add(dwg.line(start=(150, leyenda_y+10), end=(180, leyenda_y+10), stroke=COLORS['cable_neutro'], stroke_width=2))
    dwg.add(dwg.text("Neutro", insert=(185, leyenda_y+13), font_size=8, fill=COLORS['texto']))
    
    dwg.add(dwg.line(start=(250, leyenda_y+10), end=(280, leyenda_y+10), stroke=COLORS['cable_tierra'], stroke_width=2))
    dwg.add(dwg.text("Tierra", insert=(285, leyenda_y+13), font_size=8, fill=COLORS['texto']))
    
    dwg.add(dwg.circle(center=(350, leyenda_y+10), r=5, fill='none', stroke=COLORS['cable_fase'], stroke_width=2))
    dwg.add(dwg.text("Toma", insert=(360, leyenda_y+13), font_size=8, fill=COLORS['texto']))
    
    dwg.save()
    print(f"✅ Plano generado: {archivo}")

def crear_plano_tablero(archivo, circuitos=None):
    """Crea un diagrama de tablero eléctrico"""
    if circuitos is None:
        circuitos = [
            {"nombre": "GENERAL", "tipo": "disyuntor", "amperaje": "25A"},
            {"nombre": "ILUMINACIÓN", "tipo": "térmica", "amperaje": "10A"},
            {"nombre": "ENCHUFES", "tipo": "térmica", "amperaje": "16A"},
            {"nombre": "AA", "tipo": "térmica", "amperaje": "20A"},
        ]
    
    dwg = svgwrite.Drawing(archivo, size=('210mm', '297mm'), viewBox='0 0 595 842')
    dwg.add(dwg.rect(insert=(0,0), size=('100%','100%'), fill=COLORS['fondo']))
    dwg.add(dwg.text("DIAGRAMA DE TABLERO", insert=(50, 40), font_size=16, font_weight='bold'))
    
    # Tablero base
    tablero_x, tablero_y = 150, 100
    tablero_w, tablero_h = 300, 400
    dwg.add(dwg.rect(insert=(tablero_x, tablero_y), size=(tablero_w, tablero_h),
                     fill=COLORS['fondo_panel'], stroke=COLORS['pared'], stroke_width=3))
    
    # Circuitos
    for i, circ in enumerate(circuitos):
        y = tablero_y + 50 + (i * 80)
        
        # Disyuntor/Térmica
        dwg.add(dwg.rect(insert=(tablero_x+20, y), size=(60, 40),
                        fill='white', stroke=COLORS['equipo'], stroke_width=2))
        dwg.add(dwg.text(circ['tipo'].upper()[:4], insert=(tablero_x+25, y+15), font_size=8, font_weight='bold'))
        dwg.add(dwg.text(circ['amperaje'], insert=(tablero_x+25, y+30), font_size=10, fill=COLORS['cable_fase']))
        
        # Línea de conexión
        dwg.add(dwg.line(start=(tablero_x+80, y+20), end=(tablero_x+120, y+20),
                        stroke=COLORS['cable_fase'], stroke_width=2))
        
        # Nombre del circuito
        dwg.add(dwg.text(circ['nombre'], insert=(tablero_x+130, y+25), font_size=10, fill=COLORS['texto']))
        
        # Línea de salida
        dwg.add(dwg.line(start=(tablero_x+tablero_w-20, y+20), end=(tablero_x+tablero_w, y+20),
                        stroke=COLORS['cable_fase'], stroke_width=2))
    
    # Línea principal de entrada
    dwg.add(dwg.line(start=(tablero_x+tablero_w/2, tablero_y), end=(tablero_x+tablero_w/2, tablero_y+50),
                    stroke=COLORS['cable_fase'], stroke_width=3))
    dwg.add(dwg.text("ENTRADA", insert=(tablero_x+tablero_w/2-20, tablero_y-10), font_size=8, fill=COLORS['equipo']))
    
    dwg.save()
    print(f"✅ Diagrama de tablero generado: {archivo}")

def crear_plano_acometida(archivo, distancia=10):
    """Crea un diagrama de acometida"""
    dwg = svgwrite.Drawing(archivo, size=('210mm', '297mm'), viewBox='0 0 595 842')
    dwg.add(dwg.rect(insert=(0,0), size=('100%','100%'), fill=COLORS['fondo']))
    dwg.add(dwg.text("ACOMETIDA ELÉCTRICA", insert=(50, 40), font_size=16, font_weight='bold'))
    dwg.add(dwg.text(f"Distancia: {distancia} metros", insert=(50, 60), font_size=10, fill=COLORS['equipo']))
    
    # Poste
    poste_x, poste_y = 100, 200
    dwg.add(dwg.rect(insert=(poste_x, poste_y), size=(20, 150), fill=COLORS['equipo']))
    dwg.add(dwg.text("POSTE", insert=(poste_x-10, poste_y+170), font_size=8, fill=COLORS['texto']))
    
    # Medidor
    medidor_x, medidor_y = poste_x + 30, poste_y + 20
    dwg.add(dwg.circle(center=(medidor_x, medidor_y), r=15, fill='white', stroke=COLORS['pared'], stroke_width=2))
    dwg.add(dwg.text("kWh", insert=(medidor_x-10, medidor_y+4), font_size=8, fill=COLORS['texto']))
    dwg.add(dwg.text("MEDIDOR", insert=(medidor_x-15, medidor_y+30), font_size=7, fill=COLORS['equipo']))
    
    # Cable preensamblado
    cable_y = medidor_y
    dwg.add(dwg.line(start=(medidor_x+15, cable_y), end=(medidor_x+200, cable_y),
                    stroke=COLORS['cable_fase'], stroke_width=3, stroke_dasharray="8,4"))
    dwg.add(dwg.text(f"Cable preensamblado 6mm² ({distancia}m)", 
                    insert=(medidor_x+50, cable_y-10), font_size=9, fill=COLORS['equipo']))
    
    # Casa
    casa_x, casa_y = medidor_x + 250, cable_y - 50
    dwg.add(dwg.rect(insert=(casa_x, casa_y), size=(100, 80), fill=COLORS['fondo_panel'], stroke=COLORS['pared'], stroke_width=2))
    dwg.add(dwg.text("CASA", insert=(casa_x+35, casa_y+45), font_size=12, font_weight='bold'))
    
    # Tablero en casa
    tablero_x, tablero_y = casa_x + 20, casa_y + 90
    dwg.add(dwg.rect(insert=(tablero_x, tablero_y), size=(60, 80), 
                     fill=COLORS['fondo_panel'], stroke=COLORS['pared'], stroke_width=2))
    dwg.add(dwg.text("TABLERO", insert=(tablero_x+5, tablero_y+20), font_size=8, fill=COLORS['texto']))
    
    # Conexión post → casa
    dwg.add(dwg.line(start=(medidor_x+15, cable_y), end=(casa_x, cable_y),
                    stroke=COLORS['cable_fase'], stroke_width=3))
    
    # Conexión casa → tablero
    dwg.add(dwg.line(start=(casa_x+50, casa_y+80), end=(tablero_x+30, tablero_y),
                    stroke=COLORS['cable_fase'], stroke_width=2))
    
    dwg.save()
    print(f"✅ Diagrama de acometida generado: {archivo}")

def main():
    parser = argparse.ArgumentParser(description='Generador de planos eléctricos')
    parser.add_argument('--tipo', choices=['instalacion', 'tablero', 'acometida'], 
                       default='instalacion', help='Tipo de plano')
    parser.add_argument('--archivo', default='plano_electrico.svg', help='Archivo de salida')
    parser.add_argument('--titulo', default='Plano Eléctrico', help='Título del plano')
    parser.add_argument('--direccion', default='', help='Dirección del trabajo')
    parser.add_argument('--distancia', type=int, default=10, help='Distancia de acometida (m)')
    
    args = parser.parse_args()
    
    if args.tipo == 'instalacion':
        crear_plano_instalacion(args.archivo, args.titulo, args.direccion)
    elif args.tipo == 'tablero':
        crear_plano_tablero(args.archivo)
    elif args.tipo == 'acometida':
        crear_plano_acometida(args.archivo, args.distancia)

if __name__ == "__main__":
    main()
