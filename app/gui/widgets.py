"""Widgets y estilos customtkinter compartidos (minimalistas: bordes de 1 px, sin relleno)."""
from __future__ import annotations

from typing import Callable

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from ..analysis.plots import estilizar_figura
from .theme import CLARO, OSCURO, Tema, tema

FAMILIA = "Segoe UI"


def par(atributo: str) -> tuple[str, str]:
    """Color (claro, oscuro) para widgets customtkinter."""
    return getattr(CLARO, atributo), getattr(OSCURO, atributo)


def fuente(tam: int = 13, peso: str = "normal") -> ctk.CTkFont:
    return ctk.CTkFont(family=FAMILIA, size=tam, weight=peso)


def tema_actual() -> Tema:
    return tema(ctk.get_appearance_mode())


def tarjeta(master, **kw) -> ctk.CTkFrame:
    return ctk.CTkFrame(master, fg_color=par("panel"), border_width=1, border_color=par("borde"),
                        corner_radius=8, **kw)


def separador(master) -> ctk.CTkFrame:
    return ctk.CTkFrame(master, height=1, fg_color=par("borde"), corner_radius=0)


def boton(master, texto: str, comando: Callable, **kw) -> ctk.CTkButton:
    return ctk.CTkButton(master, text=texto, command=comando, fg_color="transparent", border_width=1,
                         border_color=par("borde"), text_color=par("texto"), hover_color=par("resaltado"),
                         corner_radius=6, height=30, font=fuente(12), **kw)


def etiqueta(master, texto: str = "", tam: int = 12, color: str = "texto", peso: str = "normal",
             **kw) -> ctk.CTkLabel:
    kw.setdefault("text_color", par(color))
    return ctk.CTkLabel(master, text=texto, font=fuente(tam, peso), **kw)


class PanelFigura(ctk.CTkFrame):
    """Marco con una figura de matplotlib incrustada que sigue el tema activo."""

    def __init__(self, master, figsize=(8, 6), **kw):
        super().__init__(master, fg_color="transparent", **kw)
        self.fig = Figure(figsize=figsize, layout="constrained")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas.get_tk_widget().configure(highlightthickness=0, borderwidth=0)
        self.pendiente = True     # hay datos nuevos sin dibujar

    def aplicar_tema(self, t: Tema) -> None:
        estilizar_figura(self.fig, t)
        self.canvas.get_tk_widget().configure(bg=t.panel)

    def dibujar(self) -> None:
        self.canvas.draw_idle()
