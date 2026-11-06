"""Ventana principal (customtkinter): barra lateral de controles y pestañas de análisis."""
from __future__ import annotations

import tkinter as tk
import warnings

import customtkinter as ctk

from ..fuzzy import config as cfg
from ..fuzzy.engine import ResultadoInferencia, formato_mxn, motor
from .panels.inference_tab import PanelInferencia
from .panels.rules_tab import PanelReglas
from .panels.surface_tab import PanelSuperficie
from .panels.verify_tab import PanelVerificacion
from .widgets import boton, etiqueta, fuente, par, separador, tarjeta, tema_actual

warnings.filterwarnings("ignore", category=DeprecationWarning, module="skfuzzy")

VALOR_INICIAL = (50, 50)
EJEMPLO = (70, 75)
OPACIDAD_INICIAL = 0.95
OPACIDAD_MIN, OPACIDAD_MAX = 0.70, 1.00
DEBOUNCE_MS = 40


class ControlEntrada(ctk.CTkFrame):
    """Slider + campo numérico sincronizados (0–100, paso 1)."""

    def __init__(self, master, titulo: str, extremo_bajo: str, extremo_alto: str, al_cambiar, al_error):
        super().__init__(master, fg_color="transparent")
        self.al_cambiar, self.al_error = al_cambiar, al_error
        self.valor = 0
        self.grid_columnconfigure(0, weight=1)

        etiqueta(self, titulo, 12).grid(row=0, column=0, sticky="w")
        self.campo = ctk.CTkEntry(self, width=58, height=26, justify="right", border_width=1,
                                  border_color=par("borde"), fg_color="transparent",
                                  text_color=par("texto"), corner_radius=6, font=fuente(12))
        self.campo.grid(row=0, column=1, sticky="e")
        self.slider = ctk.CTkSlider(self, from_=0, to=100, number_of_steps=100, height=16,
                                    button_length=0, border_width=6, progress_color=par("acento"),
                                    button_color=par("acento"), button_hover_color=par("texto"),
                                    fg_color=par("borde"), command=self._desde_slider)
        self.slider.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 2))
        etiqueta(self, extremo_bajo, 10, "tenue").grid(row=2, column=0, sticky="w")
        etiqueta(self, extremo_alto, 10, "tenue").grid(row=2, column=1, sticky="e")

        self.campo.bind("<Return>", self._desde_campo)
        self.campo.bind("<FocusOut>", self._desde_campo)
        self.campo.bind("<KP_Enter>", self._desde_campo)

    def establecer(self, valor: int, notificar: bool = True) -> None:
        self.valor = int(valor)
        self.slider.set(self.valor)
        self.campo.delete(0, "end")
        self.campo.insert(0, str(self.valor))
        if notificar:
            self.al_cambiar()

    def _desde_slider(self, v: float) -> None:
        v = int(round(v))
        if v != self.valor:
            self.establecer(v)

    def _desde_campo(self, _evento=None) -> None:
        texto = self.campo.get().strip().replace(",", ".")
        try:
            v = float(texto)
            if not 0 <= v <= 100:
                raise ValueError
        except ValueError:
            self.al_error(f"«{texto}» no es válido: usa un número entre 0 y 100.")
            self.establecer(self.valor, notificar=False)
            return
        v = int(round(v))
        if v != self.valor:
            self.establecer(v)
        else:
            self.establecer(v, notificar=False)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Beca difusa · Fundamentos de IA")
        self.geometry("1400x860")
        self.minsize(1100, 700)
        self.configure(fg_color=par("fondo"))
        self._pendiente = None
        self._aviso_id = None
        self.resultado: ResultadoInferencia | None = None
        self.transparencia = self._probar_transparencia()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._barra_lateral()
        self._pestanas()

        self.desempeno.establecer(VALOR_INICIAL[0], notificar=False)
        self.entrega.establecer(VALOR_INICIAL[1], notificar=False)
        self.recalcular()

    # ------------------------------------------------------------------ transparencia
    def _probar_transparencia(self) -> bool:
        try:
            self.attributes("-alpha", OPACIDAD_INICIAL)
            return True
        except tk.TclError:
            return False

    def _cambiar_opacidad(self, v: float) -> None:
        self.lbl_opacidad.configure(text=f"{v * 100:.0f} %")
        if self.transparencia:
            try:
                self.attributes("-alpha", v)
            except tk.TclError:
                self.transparencia = False

    # ------------------------------------------------------------------ construcción
    def _barra_lateral(self) -> None:
        lado = ctk.CTkFrame(self, width=300, fg_color=par("panel"), corner_radius=0, border_width=0)
        lado.grid(row=0, column=0, sticky="nsw")
        lado.grid_propagate(False)
        lado.grid_columnconfigure(0, weight=1)
        ctk.CTkFrame(self, width=1, fg_color=par("borde"), corner_radius=0).grid(row=0, column=0, sticky="nse")

        pad = {"padx": 22}
        etiqueta(lado, "Beca difusa", 22, peso="bold").grid(row=0, column=0, sticky="w", pady=(24, 0), **pad)
        etiqueta(lado, "Mamdani · mín / máx · centroide", 11, "tenue").grid(row=1, column=0, sticky="w", **pad)
        separador(lado).grid(row=2, column=0, sticky="ew", pady=18, **pad)

        self.desempeno = ControlEntrada(lado, "Desempeño en evaluaciones", "0 · Bajo", "Alto · 100",
                                        self._programar, self._avisar)
        self.desempeno.grid(row=3, column=0, sticky="ew", **pad)
        self.entrega = ControlEntrada(lado, "Entrega de actividades (%)", "0 · Baja", "Alta · 100",
                                      self._programar, self._avisar)
        self.entrega.grid(row=4, column=0, sticky="ew", pady=(16, 0), **pad)

        res = tarjeta(lado)
        res.grid(row=5, column=0, sticky="ew", pady=(22, 0), **pad)
        etiqueta(res, "Beca recomendada", 11, "tenue").pack(anchor="w", padx=16, pady=(14, 0))
        self.lbl_pct = etiqueta(res, "—", 34, peso="bold")
        self.lbl_pct.pack(anchor="w", padx=16)
        self.lbl_importe = etiqueta(res, "", 15, "acento")
        self.lbl_importe.pack(anchor="w", padx=16)
        etiqueta(res, f"de un salario mínimo de ${cfg.SALARIO_MINIMO:,.2f} MXN", 10, "tenue").pack(
            anchor="w", padx=16, pady=(2, 14))

        self.lbl_aviso = etiqueta(lado, "", 11, wraplength=250, justify="left",
                                  text_color=("#c0392b", "#ef6b5b"))
        self.lbl_aviso.grid(row=6, column=0, sticky="w", pady=(8, 0), **pad)

        botones = ctk.CTkFrame(lado, fg_color="transparent")
        botones.grid(row=7, column=0, sticky="ew", pady=(6, 0), **pad)
        botones.grid_columnconfigure((0, 1), weight=1, uniform="b")
        boton(botones, f"Ejemplo {EJEMPLO[0]} / {EJEMPLO[1]}", lambda: self.cargar(*EJEMPLO)).grid(
            row=0, column=0, sticky="ew", padx=(0, 4))
        boton(botones, "Restablecer", lambda: self.cargar(*VALOR_INICIAL)).grid(
            row=0, column=1, sticky="ew", padx=(4, 0))

        lado.grid_rowconfigure(8, weight=1)

        # apariencia
        separador(lado).grid(row=9, column=0, sticky="ew", pady=(0, 14), **pad)
        etiqueta(lado, "Tema", 11, "tenue").grid(row=10, column=0, sticky="w", **pad)
        self.selector_tema = ctk.CTkSegmentedButton(
            lado, values=["Oscuro", "Claro"], command=self.cambiar_tema, height=26, font=fuente(11),
            corner_radius=6, border_width=1, fg_color=par("borde"), selected_color=par("acento"),
            selected_hover_color=par("acento"), unselected_color=par("panel"),
            unselected_hover_color=par("resaltado"), text_color=par("texto"))
        self.selector_tema.grid(row=11, column=0, sticky="ew", pady=(4, 12), **pad)
        self.selector_tema.set("Oscuro" if ctk.get_appearance_mode() == "Dark" else "Claro")

        fila = ctk.CTkFrame(lado, fg_color="transparent")
        fila.grid(row=12, column=0, sticky="ew", **pad)
        fila.grid_columnconfigure(0, weight=1)
        etiqueta(fila, "Opacidad de la ventana", 11, "tenue").grid(row=0, column=0, sticky="w")
        self.lbl_opacidad = etiqueta(fila, "", 11, "tenue")
        self.lbl_opacidad.grid(row=0, column=1, sticky="e")
        pasos = round((OPACIDAD_MAX - OPACIDAD_MIN) * 100)
        self.slider_opacidad = ctk.CTkSlider(
            lado, from_=OPACIDAD_MIN, to=OPACIDAD_MAX, number_of_steps=pasos, height=12,
            button_length=0, progress_color=par("tenue"), button_color=par("tenue"),
            button_hover_color=par("texto"), fg_color=par("borde"), command=self._cambiar_opacidad)
        self.slider_opacidad.grid(row=13, column=0, sticky="ew", pady=(4, 22), **pad)
        self.slider_opacidad.set(OPACIDAD_INICIAL if self.transparencia else 1.0)
        self.lbl_opacidad.configure(text=f"{self.slider_opacidad.get() * 100:.0f} %"
                                    if self.transparencia else "no soportada")
        if not self.transparencia:
            self.slider_opacidad.configure(state="disabled")

    def _pestanas(self) -> None:
        self.tabs = ctk.CTkTabview(
            self, fg_color="transparent", corner_radius=8, border_width=0, anchor="nw",
            segmented_button_fg_color=par("fondo"), segmented_button_selected_color=par("panel"),
            segmented_button_selected_hover_color=par("panel"),
            segmented_button_unselected_color=par("fondo"),
            segmented_button_unselected_hover_color=par("resaltado"), text_color=par("texto"),
            command=self._al_cambiar_pestana)
        self.tabs.grid(row=0, column=1, sticky="nsew", padx=(18, 18), pady=(10, 16))
        self.tabs._segmented_button.configure(font=fuente(12), border_width=1)
        t = tema_actual()
        self.paneles = {}
        for nombre, clase in [("Inferencia", PanelInferencia), ("Reglas", PanelReglas),
                              ("Superficie", PanelSuperficie), ("Verificación", PanelVerificacion)]:
            pestana = self.tabs.add(nombre)
            panel = clase(pestana, t)
            panel.pack(fill="both", expand=True)
            self.paneles[nombre] = panel
        self.tabs.set("Inferencia")

    # ------------------------------------------------------------------ comportamiento
    def cargar(self, d: int, e: int) -> None:
        self.desempeno.establecer(d, notificar=False)
        self.entrega.establecer(e, notificar=False)
        self.recalcular()

    def _programar(self) -> None:
        """Agrupa cambios rápidos del slider (debounce)."""
        if self._pendiente is not None:
            self.after_cancel(self._pendiente)
        self._pendiente = self.after(DEBOUNCE_MS, self.recalcular)

    def recalcular(self) -> None:
        self._pendiente = None
        r = motor().inferir(self.desempeno.valor, self.entrega.valor)
        self.resultado = r
        self.lbl_pct.configure(text=f"{r.porcentaje:.2f} %")
        self.lbl_importe.configure(text=formato_mxn(r.importe))
        for panel in self.paneles.values():
            panel.pendiente = True
        self._refrescar_visible()

    def _refrescar_visible(self) -> None:
        panel = self.paneles[self.tabs.get()]
        if panel.pendiente and self.resultado is not None:
            panel.actualizar(self.resultado)
            panel.pendiente = False

    def _al_cambiar_pestana(self) -> None:
        self.after(10, self._refrescar_visible)

    def _avisar(self, mensaje: str) -> None:
        self.lbl_aviso.configure(text=mensaje)
        if self._aviso_id is not None:
            self.after_cancel(self._aviso_id)
        self._aviso_id = self.after(3500, lambda: self.lbl_aviso.configure(text=""))

    def cambiar_tema(self, valor: str) -> None:
        ctk.set_appearance_mode("dark" if valor == "Oscuro" else "light")
        t = tema_actual()
        for panel in self.paneles.values():
            panel.aplicar_tema(t)
            if hasattr(panel, "canvas"):
                panel.canvas.draw_idle()


def ejecutar() -> None:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    App().mainloop()
