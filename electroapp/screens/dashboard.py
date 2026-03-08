from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.metrics import dp
from utils.vault import get_stats, get_dolar
from utils.styles import *

class DashboardScreen(Screen):
    def build_ui(self):
        root = BoxLayout(orientation="vertical")
        add_bg(root)
        header = BoxLayout(size_hint_y=None, height=dp(56), padding=[dp(12),0])
        with header.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*COLOR_CARD)
            r = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i,v: setattr(r,"pos",v), size=lambda i,v: setattr(r,"size",v))
        t = Label(text="⚡ Dario Electricista", font_size=dp(18), color=COLOR_AZUL, bold=True, halign="left")
        t.bind(size=t.setter("text_size"))
        header.add_widget(t)
        root.add_widget(header)

        scroll = ScrollView()
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(12), size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))

        self.stats_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(200))
        content.add_widget(self.stats_grid)

        self.dolar_card = make_card()
        self.dolar_lbl = make_label("💵 Cargando dólar...", size=dp(15))
        self.dolar_card.add_widget(self.dolar_lbl)
        content.add_widget(self.dolar_card)

        content.add_widget(make_label("🛠 Trabajos activos", size=dp(15), color=COLOR_NARANJA, bold=True))
        self.activos_box = BoxLayout(orientation="vertical", spacing=dp(6), size_hint_y=None)
        self.activos_box.bind(minimum_height=self.activos_box.setter("height"))
        content.add_widget(self.activos_box)

        content.add_widget(make_label("💰 Sin cobrar", size=dp(15), color=COLOR_ROJO, bold=True))
        self.cobrar_box = BoxLayout(orientation="vertical", spacing=dp(6), size_hint_y=None)
        self.cobrar_box.bind(minimum_height=self.cobrar_box.setter("height"))
        content.add_widget(self.cobrar_box)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.cargar(), 0.1)

    def cargar(self):
        stats = get_stats()
        self.stats_grid.clear_widgets()
        for emoji, titulo, valor, color in [
            ("🛠","Activos",str(stats["activos"]),COLOR_AZUL),
            ("💰","Sin cobrar",str(stats["sin_cobrar"]),COLOR_ROJO),
            ("📊","Este mes",f"${stats['total_mes']:,}".replace(",","."),COLOR_VERDE),
            ("⏳","Pendiente",f"${stats['total_pendiente']:,}".replace(",","."),COLOR_NARANJA),
        ]:
            card = make_card(padding=dp(12))
            box = BoxLayout(orientation="vertical", spacing=dp(4))
            box.add_widget(make_label(f"{emoji} {titulo}", size=dp(12), color=COLOR_TEXTO_DIM))
            box.add_widget(make_label(valor, size=dp(20), color=color, bold=True))
            card.add_widget(box)
            self.stats_grid.add_widget(card)

        dolar = get_dolar()
        self.dolar_lbl.text = f"💵 Dólar blue: ${dolar:,}".replace(",",".") if dolar else "💵 Dólar blue: sin conexión"

        self.activos_box.clear_widgets()
        for t in stats["trabajos_activos"][:8]:
            card = make_card(orientation="horizontal", padding=dp(10))
            lbl = make_label(f"[b]{t.get('cliente','?')}[/b]  [size=12sp][color=#888]{t.get('estado')}[/color][/size]", markup=True)
            monto = make_label(f"${int(t.get('mano_de_obra',0)):,}".replace(",","."), color=COLOR_AZUL, bold=True)
            monto.size_hint_x = None
            monto.width = dp(90)
            card.add_widget(lbl)
            card.add_widget(monto)
            self.activos_box.add_widget(card)

        self.cobrar_box.clear_widgets()
        for t in stats["trabajos_sin_cobrar"][:8]:
            card = make_card(orientation="horizontal", padding=dp(10))
            lbl = make_label(f"[b]{t.get('cliente','?')}[/b]", markup=True)
            monto = make_label(f"${int(t.get('mano_de_obra',0)):,}".replace(",","."), color=COLOR_ROJO, bold=True)
            monto.size_hint_x = None
            monto.width = dp(90)
            card.add_widget(lbl)
            card.add_widget(monto)
            self.cobrar_box.add_widget(card)
