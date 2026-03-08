import os, subprocess
from datetime import date
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.metrics import dp
from utils.vault import TRABAJOS
from utils.styles import *

class FotosScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical")
        add_bg(root)
        header = BoxLayout(size_hint_y=None, height=dp(56), padding=[dp(12),0])
        with header.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*COLOR_CARD); r = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i,v: setattr(r,"pos",v), size=lambda i,v: setattr(r,"size",v))
        t = Label(text="📷 Fotos", font_size=dp(18), color=COLOR_AZUL, bold=True, halign="left")
        t.bind(size=t.setter("text_size")); header.add_widget(t); root.add_widget(header)
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        add_bg(content)
        content.add_widget(make_section_title("Cliente", COLOR_AZUL))
        carpetas = sorted([d for d in os.listdir(TRABAJOS) if os.path.isdir(os.path.join(TRABAJOS,d)) and not d.startswith(".")])
        self.spinner = Spinner(text=carpetas[0] if carpetas else "?", values=carpetas,
                               size_hint_y=None, height=dp(44), font_size=dp(14),
                               background_normal="", background_color=COLOR_CARD, color=COLOR_TEXTO)
        content.add_widget(self.spinner)
        content.add_widget(make_section_title("Descripción", COLOR_AZUL))
        self.desc = make_input(hint="ej: tablero, antes, despues")
        content.add_widget(self.desc)
        self.status = make_label("", color=COLOR_TEXTO_DIM)
        content.add_widget(self.status)
        content.add_widget(make_button("📷 Sacar foto", color_bg=COLOR_AZUL, on_press=self.sacar))
        root.add_widget(content); self.add_widget(root)

    def sacar(self, *args):
        cliente = self.spinner.text
        desc = self.desc.text.strip().replace(" ","_") or "foto"
        hoy = date.today().strftime("%Y-%m-%d")
        carpeta = os.path.join(TRABAJOS, cliente, "fotos")
        os.makedirs(carpeta, exist_ok=True)
        ruta = os.path.join(carpeta, f"{hoy}_{desc}.jpg")
        self.status.text = "📷 Abriendo camara..."
        subprocess.run(["termux-camera-photo","-c","0",ruta], capture_output=True)
        if os.path.exists(ruta) and os.path.getsize(ruta) > 0:
            self.status.text = f"✅ Guardada ({os.path.getsize(ruta)//1024} KB)"
            self.status.color = COLOR_VERDE
        else:
            self.status.text = "❌ No se pudo guardar"; self.status.color = COLOR_ROJO
