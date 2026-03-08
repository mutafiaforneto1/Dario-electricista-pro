import subprocess
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from utils.vault import get_precios, TARIFAS_MO
from utils.styles import *

class PresupuestoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mo = {}; self.mat = {}
        root = BoxLayout(orientation="vertical"); add_bg(root)
        header = BoxLayout(size_hint_y=None, height=dp(56), padding=[dp(12),0])
        with header.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*COLOR_CARD); r = Rectangle(pos=header.pos, size=header.size)
        header.bind(pos=lambda i,v: setattr(r,"pos",v), size=lambda i,v: setattr(r,"size",v))
        t = Label(text="💰 Presupuesto", font_size=dp(18), color=COLOR_AZUL, bold=True, halign="left")
        t.bind(size=t.setter("text_size")); header.add_widget(t); root.add_widget(header)
        scroll = ScrollView()
        c = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10), size_hint_y=None)
        c.bind(minimum_height=c.setter("height"))
        c.add_widget(make_section_title("Cliente", COLOR_AZUL))
        self.cli = make_input(hint="Nombre del cliente"); c.add_widget(self.cli)
        c.add_widget(make_section_title("🔧 Mano de Obra", COLOR_NARANJA))
        mo_card = make_card()
        for nombre, precio in TARIFAS_MO.items():
            row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(6))
            lbl = Label(text=nombre, font_size=dp(12), color=COLOR_TEXTO, halign="left", size_hint_x=1)
            lbl.bind(size=lbl.setter("text_size"))
            pl = Label(text=f"${precio:,}".replace(",","."), font_size=dp(11), color=COLOR_TEXTO_DIM, size_hint_x=None, width=dp(80), halign="right")
            inp = TextInput(hint_text="0", input_filter="int", font_size=dp(14), multiline=False,
                            foreground_color=COLOR_TEXTO, background_color=(0.18,0.18,0.22,1),
                            cursor_color=COLOR_AZUL, size_hint_x=None, width=dp(48),
                            size_hint_y=None, height=dp(36), padding=[dp(6),dp(8)])
            inp.bind(text=lambda x,v,n=nombre,p=precio: self.upd_mo(n,p,v))
            row.add_widget(lbl); row.add_widget(pl); row.add_widget(inp)
            mo_card.add_widget(row)
        c.add_widget(mo_card)
        c.add_widget(make_section_title("📦 Materiales", COLOR_VERDE))
        gr = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        gr.add_widget(make_label("% Ganancia:", size=dp(13)))
        self.gan = TextInput(hint_text="30", input_filter="int", font_size=dp(14), multiline=False,
                              foreground_color=COLOR_TEXTO, background_color=(0.18,0.18,0.22,1),
                              cursor_color=COLOR_AZUL, size_hint_x=None, width=dp(60),
                              size_hint_y=None, height=dp(36), padding=[dp(6),dp(8)])
        gr.add_widget(self.gan); c.add_widget(gr)
        mat_card = make_card()
        for nombre, precio in get_precios():
            row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(6))
            lbl = Label(text=nombre, font_size=dp(11), color=COLOR_TEXTO, halign="left", size_hint_x=1)
            lbl.bind(size=lbl.setter("text_size"))
            pl = Label(text=f"${precio:,}".replace(",","."), font_size=dp(10), color=COLOR_TEXTO_DIM, size_hint_x=None, width=dp(75), halign="right")
            inp = TextInput(hint_text="0", input_filter="float", font_size=dp(14), multiline=False,
                            foreground_color=COLOR_TEXTO, background_color=(0.18,0.18,0.22,1),
                            cursor_color=COLOR_AZUL, size_hint_x=None, width=dp(48),
                            size_hint_y=None, height=dp(36), padding=[dp(6),dp(8)])
            inp.bind(text=lambda x,v,n=nombre,p=precio: self.upd_mat(n,p,v))
            row.add_widget(lbl); row.add_widget(pl); row.add_widget(inp)
            mat_card.add_widget(row)
        c.add_widget(mat_card)
        tc = make_card()
        self.mo_lbl = make_label("MO: $0", size=dp(13), color=COLOR_TEXTO_DIM)
        self.mat_lbl = make_label("Mat: $0", size=dp(13), color=COLOR_TEXTO_DIM)
        self.tot_lbl = make_label("TOTAL: $0", size=dp(20), color=COLOR_VERDE, bold=True)
        tc.add_widget(self.mo_lbl); tc.add_widget(self.mat_lbl); tc.add_widget(self.tot_lbl)
        c.add_widget(tc)
        c.add_widget(make_button("📱 Copiar para WhatsApp", color_bg=COLOR_VERDE, on_press=self.generar))
        scroll.add_widget(c); root.add_widget(scroll); self.add_widget(root)

    def upd_mo(self,n,p,v):
        try: self.mo[n]=(int(v) if v else 0,p)
        except: pass
        self.recalc()

    def upd_mat(self,n,p,v):
        try: self.mat[n]=(float(v) if v else 0,p)
        except: pass
        self.recalc()

    def recalc(self):
        g=int(self.gan.text or 30)/100
        tmo=sum(c*p for c,p in self.mo.values() if c>0)
        tmat=sum(c*int(p*(1+g)) for c,p in self.mat.values() if c>0)
        self.mo_lbl.text=f"MO: ${tmo:,}".replace(",",".")
        self.mat_lbl.text=f"Mat: ${tmat:,}".replace(",",".")
        self.tot_lbl.text=f"TOTAL: ${tmo+tmat:,}".replace(",",".")

    def generar(self,*a):
        g=int(self.gan.text or 30)
        cli=self.cli.text.strip() or "Cliente"
        tmo=sum(c*p for c,p in self.mo.values() if c>0)
        tmat=sum(c*int(p*(1+g/100)) for c,p in self.mat.values() if c>0)
        lmo="".join(f"  • {n}: ${c*p:,}\n".replace(",",".") for n,(c,p) in self.mo.items() if c>0)
        lmat="".join(f"  • {n}: ${int(c*int(p*(1+g/100))):,}\n".replace(",",".") for n,(c,p) in self.mat.items() if c>0)
        msg=f"*⚡ Presupuesto Electrico*\n*Dario Electricista - La Plata*\n──────────────────────────\nHola *{cli}*, te paso el detalle:\n\n🔧 *Mano de obra:*\n{lmo}\n📦 *Materiales (+{g}%):*\n{lmat}\n──────────────────────────\n💰 *TOTAL: ${tmo+tmat:,}*\n\n✅ Valido por 48hs.".replace(",",".")
        try:
            p=subprocess.Popen(["termux-clipboard-set"],stdin=subprocess.PIPE)
            p.communicate(input=msg.encode("utf-8"))
            self.tot_lbl.text="✅ Copiado para WhatsApp"
        except:
            self.tot_lbl.text="Error al copiar"
