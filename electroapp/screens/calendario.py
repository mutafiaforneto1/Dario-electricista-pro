from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.metrics import dp
from utils.vault import get_trabajos
from utils.styles import *

class CalendarioScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = BoxLayout(orientation="vertical")
        add_bg(root)
        header = BoxLayout(size_hint_y=None, height=dp(56), padding=[dp(12),0])
        with header.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*COLOR_CARD); r = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i,v: setattr(r,"pos",v), size=lambda i,v: setattr(r,"size",v))
        t = Label(text="📅 Calendario", font_size=dp(18), color=COLOR_AZUL, bold=True, halign="left")
        t.bind(size=t.setter("text_size")); header.add_widget(t); root.add_widget(header)
        scroll = ScrollView()
        self.content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8), size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))
        scroll.add_widget(self.content); root.add_widget(scroll); self.add_widget(root)

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.cargar(), 0.1)

    def cargar(self):
        self.content.clear_widgets()
        por_mes = {}
        for t in get_trabajos():
            mes = t.get("fecha","")[:7]
            if mes: por_mes.setdefault(mes,[]).append(t)
        for mes in sorted(por_mes.keys(), reverse=True):
            try: nombre_mes = datetime.strptime(mes,"%Y-%m").strftime("%B %Y").capitalize()
            except: nombre_mes = mes
            lbl = make_label(f"📅 {nombre_mes}", size=dp(15), color=COLOR_NARANJA, bold=True)
            lbl.size_hint_y = None; lbl.height = dp(32)
            self.content.add_widget(lbl)
            total = sum(int(t.get("mano_de_obra",0)) for t in por_mes[mes])
            for t in por_mes[mes]:
                dia = t.get("fecha","")[-2:] or "?"
                estado = t.get("estado","")
                pagado = t.get("pagado","false")
                color = COLOR_VERDE if estado=="terminado" else (COLOR_AZUL if estado=="En curso" else COLOR_NARANJA)
                card = make_card(orientation="horizontal", padding=dp(10))
                dl = Label(text=dia, font_size=dp(20), color=color, bold=True, size_hint_x=None, width=dp(40))
                info = BoxLayout(orientation="vertical", spacing=dp(2))
                info.add_widget(make_label(t.get("cliente","?"), size=dp(14), bold=True))
                info.add_widget(make_label(estado, size=dp(12), color=COLOR_TEXTO_DIM))
                monto = int(t.get("mano_de_obra",0))
                ml = Label(text=f"${monto:,}".replace(",","."), font_size=dp(13),
                           color=COLOR_VERDE if pagado=="true" else COLOR_ROJO,
                           bold=True, size_hint_x=None, width=dp(85), halign="right")
                card.add_widget(dl); card.add_widget(info); card.add_widget(ml)
                self.content.add_widget(card)
            tl = make_label(f"Total: ${total:,}".replace(",","."), size=dp(13), color=COLOR_VERDE, bold=True, halign="right")
            tl.size_hint_y = None; tl.height = dp(28)
            self.content.add_widget(tl)
