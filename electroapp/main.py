import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.core.window import Window

from screens.dashboard import DashboardScreen
from screens.trabajos import TrabajosScreen
from screens.clientes import ClientesScreen
from screens.presupuesto import PresupuestoScreen
from screens.fotos import FotosScreen
from screens.calendario import CalendarioScreen
from utils.styles import COLOR_BG, COLOR_CARD, COLOR_AZUL, COLOR_TEXTO_DIM

TABS = [
    ("dashboard",   "🏠", "Inicio"),
    ("trabajos",    "🛠", "Trabajos"),
    ("clientes",    "👥", "Clientes"),
    ("presupuesto", "💰", "Presup."),
    ("fotos",       "📷", "Fotos"),
    ("calendario",  "📅", "Agenda"),
]

class ElectroApp(App):
    def build(self):
        Window.clearcolor = COLOR_BG
        root = BoxLayout(orientation="vertical")

        self.sm = ScreenManager(transition=NoTransition())
        self.sm.add_widget(DashboardScreen(name="dashboard"))
        self.sm.add_widget(TrabajosScreen(name="trabajos"))
        self.sm.add_widget(ClientesScreen(name="clientes"))
        self.sm.add_widget(PresupuestoScreen(name="presupuesto"))
        self.sm.add_widget(FotosScreen(name="fotos"))
        self.sm.add_widget(CalendarioScreen(name="calendario"))
        root.add_widget(self.sm)

        nav = BoxLayout(size_hint_y=None, height=dp(60))
        with nav.canvas.before:
            Color(*COLOR_CARD)
            r = Rectangle(pos=nav.pos, size=nav.size)
        nav.bind(pos=lambda i,v: setattr(r,"pos",v),
                 size=lambda i,v: setattr(r,"size",v))

        self.nav_btns = {}
        for name, emoji, label in TABS:
            btn = Button(
                text=f"{emoji}\n[size=9sp]{label}[/size]",
                markup=True, font_size=dp(20),
                background_normal="", background_color=(0,0,0,0),
                color=COLOR_AZUL if name=="dashboard" else COLOR_TEXTO_DIM,
            )
            btn.bind(on_press=lambda x, n=name: self.switch_tab(n))
            nav.add_widget(btn)
            self.nav_btns[name] = btn
        root.add_widget(nav)
        return root

    def switch_tab(self, name):
        self.sm.current = name
        for n, btn in self.nav_btns.items():
            btn.color = COLOR_AZUL if n==name else COLOR_TEXTO_DIM

if __name__ == "__main__":
    ElectroApp().run()
