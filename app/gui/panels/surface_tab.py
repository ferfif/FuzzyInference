"""Pestaña Superficie: superficie 3D rotable con el punto actual marcado."""
from __future__ import annotations

from ...analysis.plots import GraficaSuperficie
from ...fuzzy.engine import ResultadoInferencia
from ...fuzzy.vectorized import evaluar_malla
from ..theme import Tema
from ..widgets import PanelFigura


class PanelSuperficie(PanelFigura):
    def __init__(self, master, t: Tema):
        super().__init__(master, figsize=(9, 6.4))
        self.t = t
        self.grafica: GraficaSuperficie | None = None   # se construye al mostrarse por primera vez
        self.aplicar_tema(t)

    def _asegurar(self) -> None:
        if self.grafica is None:
            ax = self.fig.add_subplot(projection="3d")
            # la rotación con el ratón la maneja mplot3d sobre el canvas Tk
            self.grafica = GraficaSuperficie(self.fig, ax, evaluar_malla(), self.t)

    def aplicar_tema(self, t: Tema) -> None:
        self.t = t
        super().aplicar_tema(t)
        if self.grafica is not None:
            self.grafica.estilizar(t)

    def actualizar(self, r: ResultadoInferencia) -> None:
        self._asegurar()
        self.grafica.actualizar(r)
        self.dibujar()
