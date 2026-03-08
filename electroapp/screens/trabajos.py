from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.metrics import dp
from utils.vault import get_trabajos, crear_trabajo, actualizar_estado
from utils.styles import *

ESTADO_COLOR = {"pendiente":COLOR_NARANJA,"En curso":COLOR_AZUL,"terminado":COLOR_VERDE,"presupuesto":(0.72,0.53,0.96,1)}
ESTADO_EMOJI = {"pendiente":"⏳","En curso":"🔧","terminado":"✅","presupuesto":"📋"}

class TrabajosScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filtro = "todos"
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation="vertical")
        add_bg(root)
        header = BoxLayout(size_hint_y=None, height=dp(56), padding=[dp(12),0], spacing=dp(8))
        with header.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*COLOR_CARD)
            r = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i,v: setattr(r,"pos",v), size=lambda i,v: setattr(r,"size",v))
        t = Label(text="🛠 Trabajos", font_size=dp(18), color=COLOR_AZUL, bold=True, halign="left", size_hint_x=1)
        t.bind(size=t.setter("text_size"))
        btn_n = make_button("＋", height=dp(36), on_press=self.abrir_nuevo)
        btn_n.size_hint_x = None
        btn_n.width = dp(44)
        header.add_widget(t)
        header.add_widget(btn_n)
        root.add_widget(header)

        filtros = BoxLayout(size_hint_y=None, height=dp(44), padding=[dp(8),dp(4)], spacing=dp(6))
        with filtros.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.10,0.10,0.13,1)
            r2 = Rectangle(pos=filtros.pos, size=filtros.size)
        filtros.bind(pos=lambda i,v: setattr(r2,"pos",v), size=lambda i,v: setattr(r2,"size",v))
        self.fbtns = {}
        for nombre, label in [("todos","Todos"),("pendiente","⏳"),("En curso","🔧"),("terminado","✅")]:
            btn = Button(text=label, font_size=dp(13), background_normal="",
                         size_hint_x=None, width=dp(75),
                         background_color=COLOR_AZUL if nombre=="todos" else (0.2,0.2,0.25,1),
                         color=(0.05,0.05,0.07,1) if nombre=="todos" else COLOR_TEXTO)
            btn.bind(on_press=lambda x,n=nombre: self.set_filtro(n))
            filtros.add_widget(btn)
            self.fbtns[nombre] = btn
        root.add_widget(filtros)

        scroll = ScrollView()
        self.lista = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(8), size_hint_y=None)
        self.lista.bind(minimum_height=self.lista.setter("height"))
        scroll.add_widget(self.lista)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_enter(self):
        Clock.schedule_once(lambda dt: self.cargar(), 0.1)

    def set_filtro(self, f):
        self.filtro = f
        for n, btn in self.fbtns.items():
            btn.background_color = COLOR_AZUL if n==f else (0.2,0.2,0.25,1)
            btn.color = (0.05,0.05,0.07,1) if n==f else COLOR_TEXTO
        self.cargar()

    def cargar(self):
        self.lista.clear_widgets()
        trabajos = get_trabajos()
        if self.filtro != "todos":
            trabajos = [t for t in trabajos if t.get("estado")==self.filtro]
        for t in trabajos:
            self.lista.add_widget(self.make_card(t))

    def make_card(self, t):
        card = make_card(padding=dp(12))
        estado = t.get("estado","pendiente")
        color = ESTADO_COLOR.get(estado, COLOR_TEXTO_DIM)
        fila = BoxLayout(size_hint_y=None, height=dp(24))
        cl = Label(text=t.get("cliente","?"), font_size=dp(15), color=COLOR_TEXTO, bold=True, halign="left", size_hint_x=1)
        cl.bind(size=cl.setter("text_size"))
        el = Label(text=f"{ESTADO_EMOJI.get(estado,'')} {estado}", font_size=dp(12), color=color, size_hint_x=None, width=dp(95), halign="right")
        el.bind(size=el.setter("text_size"))
        fila.add_widget(cl)
        fila.add_widget(el)
        card.add_widget(fila)
        monto = int(t.get("mano_de_obra",0))
        card.add_widget(make_label(f"[color=#888]{t.get('fecha','')}[/color]   [b]${monto:,}[/b]".replace(",","."), size=dp(13), markup=True))
        btns = BoxLayout(size_hint_y=None, height=dp(34), spacing=dp(6))
        if estado != "terminado":
            b = make_button("✅ Terminar", color_bg=COLOR_VERDE, height=dp(32))
            b.bind(on_press=lambda x,r=t["_ruta"]: self.terminar(r))
            btns.add_widget(b)
        if estado=="terminado" and t.get("pagado")=="false":
            b2 = make_button("💰 Cobrar", color_bg=COLOR_NARANJA, height=dp(32))
            b2.bind(on_press=lambda x,r=t["_ruta"]: self.cobrar(r))
            btns.add_widget(b2)
        card.add_widget(btns)
        return card

    def terminar(self, ruta):
        actualizar_estado(ruta, "terminado")
        self.cargar()

    def cobrar(self, ruta):
        actualizar_estado(ruta, "terminado", pagado=True)
        self.cargar()

    def abrir_nuevo(self, *args):
        c = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(16))
        with c.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*COLOR_CARD)
            r = Rectangle(pos=c.pos, size=c.size)
        c.bind(pos=lambda i,v: setattr(r,"pos",v), size=lambda i,v: setattr(r,"size",v))
        c.add_widget(make_section_title("Nuevo Trabajo", COLOR_AZUL))
        campos = {}
        for hint in ["Cliente","Teléfono","Dirección","Descripción","Mano de obra $"]:
            inp = make_input(hint=hint)
            c.add_widget(inp)
            campos[hint] = inp
        sp = Spinner(text="pendiente", values=["pendiente","En curso","presupuesto"],
                     size_hint_y=None, height=dp(44), font_size=dp(14))
        c.add_widget(sp)
        def guardar(*a):
            try:
                crear_trabajo(campos["Cliente"].text.strip(),
                              campos["Teléfono"].text.strip(),
                              campos["Dirección"].text.strip(),
                              campos["Descripción"].text.strip(),
                              int(campos["Mano de obra $"].text.strip() or 0),
                              sp.text)
                popup.dismiss()
                self.cargar()
            except Exception as e:
                campos["Cliente"].hint_text = f"Error: {e}"
        c.add_widget(make_button("💾 Guardar", on_press=guardar))
        c.add_widget(make_button("Cancelar", color_bg=(0.3,0.3,0.35,1), on_press=lambda x: popup.dismiss()))
        popup = Popup(title="", content=c, size_hint=(0.95,0.85), separator_height=0, background="", background_color=(0,0,0,0))
        popup.open()
