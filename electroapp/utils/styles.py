from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp

COLOR_BG =      (0.08, 0.08, 0.10, 1)
COLOR_CARD =    (0.13, 0.13, 0.16, 1)
COLOR_CARD2 =   (0.16, 0.16, 0.20, 1)
COLOR_AZUL =    (0.39, 0.71, 0.96, 1)
COLOR_NARANJA = (1.0,  0.72, 0.30, 1)
COLOR_VERDE =   (0.51, 0.78, 0.52, 1)
COLOR_ROJO =    (0.95, 0.40, 0.40, 1)
COLOR_TEXTO =   (0.92, 0.92, 0.92, 1)
COLOR_TEXTO_DIM=(0.55, 0.55, 0.60, 1)

def make_label(texto, size=None, color=None, bold=False, halign="left", markup=False):
    lbl = Label(text=texto, font_size=size or dp(14), color=color or COLOR_TEXTO,
                bold=bold, halign=halign, markup=markup, size_hint_y=None)
    lbl.bind(texture_size=lambda i,v: setattr(lbl,"height",v[1]+dp(8)))
    lbl.bind(size=lbl.setter("text_size"))
    return lbl

def make_card(orientation="vertical", padding=None, spacing=None):
    card = BoxLayout(orientation=orientation, padding=padding or dp(12),
                     spacing=spacing or dp(8), size_hint_y=None)
    card.bind(minimum_height=card.setter("height"))
    with card.canvas.before:
        Color(*COLOR_CARD)
        card._rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(8)])
    card.bind(pos=lambda i,v: setattr(card._rect,"pos",v),
              size=lambda i,v: setattr(card._rect,"size",v))
    return card

def make_button(texto, color_bg=None, color_text=None, on_press=None, height=None):
    btn = Button(text=texto, font_size=dp(14), bold=True,
                 color=color_text or (0.05,0.05,0.07,1),
                 background_normal="", background_color=color_bg or COLOR_AZUL,
                 size_hint_y=None, height=height or dp(44))
    if on_press:
        btn.bind(on_press=on_press)
    return btn

def make_input(hint="", multiline=False, height=None):
    from kivy.uix.textinput import TextInput
    return TextInput(hint_text=hint, multiline=multiline, font_size=dp(14),
                     foreground_color=COLOR_TEXTO, background_color=COLOR_CARD2,
                     cursor_color=COLOR_AZUL, hint_text_color=COLOR_TEXTO_DIM,
                     size_hint_y=None, height=height or dp(44), padding=[dp(10),dp(10)])

def make_section_title(texto, color=None):
    lbl = Label(text=texto, font_size=dp(13), color=color or COLOR_TEXTO_DIM,
                bold=True, halign="left", size_hint_y=None, height=dp(28))
    lbl.bind(size=lbl.setter("text_size"))
    return lbl

def add_bg(widget, color=None):
    with widget.canvas.before:
        Color(*(color or COLOR_BG))
        rect = Rectangle(pos=widget.pos, size=widget.size)
    widget.bind(pos=lambda i,v: setattr(rect,"pos",v),
                size=lambda i,v: setattr(rect,"size",v))
