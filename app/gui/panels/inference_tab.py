"""Pestaña Inferencia: funciones de pertenencia con marcadores y salida agregada (malla 2×2).

Las curvas de pertenencia son estáticas; solo los marcadores, el relleno de la salida
agregada y el centroide cambian. Se usa *blitting*: el fondo estático se guarda tras cada
dibujo completo (redimensionar, cambiar tema) y en cada cambio de entrada solo se pintan
los artistas dinámicos.
"""
from __future__ import annotations

from ...analysis.plots import GraficaAgregada, GraficaPertenencia
from ...fuzzy.engine import ResultadoInferencia
from ..theme import Tema
from ..widgets import PanelFigura


class PanelInferencia(PanelFigura):
    def __init__(self, master, t: Tema):
        super().__init__(master, figsize=(9, 6.4))
        ejes = self.fig.subplots(2, 2)
        self.fig.get_layout_engine().set(h_pad=0.12, w_pad=0.12, hspace=0.08, wspace=0.06)
        self.g_desempeno = GraficaPertenencia(ejes[0, 0], "desempeno", t)
        self.g_entrega = GraficaPertenencia(ejes[0, 1], "entrega", t)
        self.g_beca = GraficaPertenencia(ejes[1, 0], "beca", t)
        self.g_agregada = GraficaAgregada(ejes[1, 1], t)
        self.graficas = (self.g_desempeno, self.g_entrega, self.g_beca, self.g_agregada)
        for a in self._dinamicos():
            a.set_animated(True)
        self.fondo = None
        self.canvas.mpl_connect("draw_event", self._al_dibujar)
        self.aplicar_tema(t)

    def _dinamicos(self) -> list:
        return [a for g in self.graficas for a in g.dinamicos()]

    def _pintar_dinamicos(self) -> None:
        for a in self._dinamicos():
            a.axes.draw_artist(a)

    def _al_dibujar(self, _evento) -> None:
        self.fondo = self.canvas.copy_from_bbox(self.fig.bbox)
        self._pintar_dinamicos()

    def aplicar_tema(self, t: Tema) -> None:
        super().aplicar_tema(t)
        for g in self.graficas:
            g.estilizar(t)
        self.fondo = None

    def actualizar(self, r: ResultadoInferencia) -> None:
        self.g_desempeno.actualizar(r.desempeno)
        self.g_entrega.actualizar(r.entrega)
        self.g_beca.actualizar(r.porcentaje, "Centroide")
        self.g_agregada.actualizar(r)
        if self.fondo is None:
            self.canvas.draw_idle()       # dibujo completo; _al_dibujar captura el fondo
            return
        self.canvas.restore_region(self.fondo)
        self._pintar_dinamicos()
        self.canvas.blit(self.fig.bbox)
