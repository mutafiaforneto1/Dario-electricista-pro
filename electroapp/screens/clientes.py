from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.metrics import dp
from utils.vault import get_clientes, get_trabajos
from utils.styles import *

class ClientesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical")
        add_bg(root)
        header = BoxLayout(size_hint_y=None, height=dp(56), padding=[dp(12),0])
        with header.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*COLOR_CARD)
            r = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i,v: setattr(r,"pos",v), size=lambda i,v: setattr(r,"size",v))
        t = Label(text="👥 Clientes", font_size=dp(18), color=COLOR_AZUL, bold=True, halign="left")
        t.bind(size=t.setter("text_size"))
        header.add_widget(t)
        root.add_widget(header)
        scroll = ScrollView()
        self.lista = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8), size_hint_y=None)
        self.lista.bind(minimum_height=self.lista.setter("height"))
        scroll.add_widget(self.lista)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.cargar(), 0.1)

    def cargar(self):
        self.lista.clear_widgets()
        for c in get_clientes():
            nombre = c.get("_nombre","?")
            tw = [t for t in get_trabajos() if nombre.lower() in t.get("cliente","").lower()]
            total = sum(int(t.get("mano_de_obra",0)) for t in tw)
            activos = sum(1 for t in tw if t.get("estado") in ["En curso","pendiente"])
            card = make_card(orientation="horizontal", padding=dp(12))
            info = BoxLayout(orientation="vertical", spacing=dp(4))
            info.add_widget(make_label(nombre, size=dp(15), bold=True))
            if c.get("telefono"):
                info.add_widget(make_label(c["telefono"], size=dp(12), color=COLOR_TEXTO_DIM))
            stats = BoxLayout(orientation="vertical", size_hint_x=None, width=dp(95))
            stats.add_widget(make_label(f"{len(tw)} trabajos", size=dp(12), color=COLOR_TEXTO_DIM, halign="right"))
            stats.add_widget(make_label(f"${total:,}".replace(",","."), size=dp(13), color=COLOR_VERDE, bold=True, halign="right"))
            if activos:
                stats.add_widget(make_label(f"{activos} activos", size=dp(12), color=COLOR_NARANJA, halign="right"))
            card.add_widget(info); card.add_widget(stats)
            self.lista.add_widget(card)
