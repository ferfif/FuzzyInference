"""Constructores de gráficas (matplotlib) reutilizados por la GUI y por la exportación.

Las clases dibujan una sola vez lo estático (funciones de pertenencia) y exponen
``actualizar`` para mover solo los artistas que cambian (marcadores, relleno,
centroide), lo que mantiene fluida la GUI al arrastrar los sliders.
"""
from __future__ import annotations

import numpy as np
from matplotlib.figure import Figure

from ..fuzzy import config as cfg
from ..fuzzy.engine import ResultadoInferencia
from ..fuzzy.vectorized import ResultadoMalla
from ..gui.theme import (
    LINEA, LINEA_FINA, Tema, colores, estilizar_ejes, estilizar_ejes_3d, tema as obtener_tema,
)

X = cfg.UNIVERSO


class GraficaPertenencia:
    """Funciones de pertenencia de una variable con una línea vertical para el valor actual."""

    def __init__(self, ax, variable: str, t: Tema):
        self.ax, self.variable = ax, variable
        self.lineas = {}
        for termino, mf in cfg.pertenencias(variable).items():
            (self.lineas[termino],) = ax.plot(X, mf, color=colores(variable)[termino], lw=LINEA,
                                              label=cfg.ETIQUETAS_TERMINO[termino])
        self.marcador = ax.axvline(0, ls=(0, (3, 3)), lw=LINEA_FINA * 1.5)
        self.texto = ax.text(0.0, -0.22, "", transform=ax.transAxes, fontsize=8)
        ax.set_xlim(0, 100)
        ax.set_ylim(-0.02, 1.05)
        ax.set_title(cfg.ETIQUETAS_VARIABLE[variable], loc="left")
        ax.legend(loc="lower left", bbox_to_anchor=(0, 1.08), ncol=len(self.lineas),
                  handlelength=1.2, columnspacing=1.0, borderaxespad=0)
        self.estilizar(t)

    def estilizar(self, t: Tema) -> None:
        estilizar_ejes(self.ax, t)
        self.marcador.set_color(t.acento)
        self.texto.set_color(t.acento)

    def dinamicos(self) -> list:
        return [self.marcador, self.texto]

    def actualizar(self, valor: float, etiqueta: str = "Entrada") -> None:
        self.marcador.set_xdata([valor, valor])
        self.texto.set_text(f"{etiqueta}: {valor:.2f}")


class GraficaAgregada:
    """Salida difusa agregada (área sombreada) y su centroide."""

    def __init__(self, ax, t: Tema):
        self.ax = ax
        for termino, mf in cfg.pertenencias(cfg.SALIDA).items():
            ax.plot(X, mf, color=colores(cfg.SALIDA)[termino], lw=LINEA_FINA, alpha=0.45,
                    label=cfg.ETIQUETAS_TERMINO[termino])
        self.relleno = None
        (self.contorno,) = ax.plot([], [], lw=LINEA)
        self.centroide = ax.axvline(0, ls=(0, (3, 3)), lw=LINEA_FINA * 1.5)
        self.texto = ax.text(0.0, -0.22, "", transform=ax.transAxes, fontsize=8)
        ax.set_xlim(0, 100)
        ax.set_ylim(-0.02, 1.05)
        ax.set_title("Salida agregada y centroide", loc="left")
        ax.legend(loc="lower left", bbox_to_anchor=(0, 1.08), ncol=5, handlelength=1.2,
                  columnspacing=0.8, borderaxespad=0)
        self.t = t
        self.estilizar(t)

    def estilizar(self, t: Tema) -> None:
        self.t = t
        estilizar_ejes(self.ax, t)
        self.contorno.set_color(t.acento)
        self.centroide.set_color(t.acento)
        self.texto.set_color(t.acento)
        if self.relleno is not None:
            self.relleno.set_facecolor(t.acento)

    def dinamicos(self) -> list:
        return [a for a in (self.relleno, self.contorno, self.centroide, self.texto) if a is not None]

    def actualizar(self, r: ResultadoInferencia) -> None:
        animado = self.contorno.get_animated()
        if self.relleno is not None:
            self.relleno.remove()
        self.relleno = self.ax.fill_between(r.universo_agregado, r.agregada, color=self.t.acento,
                                            alpha=0.22, lw=0)
        self.relleno.set_animated(animado)
        self.contorno.set_data(r.universo_agregado, r.agregada)
        self.centroide.set_xdata([r.porcentaje, r.porcentaje])
        self.texto.set_text(f"Centroide: {r.porcentaje:.2f} %")


class GraficaSuperficie:
    """Superficie 3D de la beca con el punto actual marcado."""

    def __init__(self, fig: Figure, ax, malla: ResultadoMalla, t: Tema, con_barra: bool = True):
        self.fig, self.ax = fig, ax
        D, E = np.meshgrid(malla.desempeno, malla.entrega, indexing="ij")
        self.superficie = ax.plot_surface(D, E, malla.beca, cmap="RdYlGn", vmin=0, vmax=100,
                                          rstride=2, cstride=2, linewidth=0, antialiased=True,
                                          alpha=0.95)
        ax.computed_zorder = False   # el punto actual siempre se dibuja sobre la superficie
        self.punto = ax.scatter([], [], [], s=60, depthshade=False, zorder=10, linewidths=1.2)
        ax.set_xlabel("Desempeño")
        ax.set_ylabel("Entrega")
        ax.set_zlabel("Beca (%)")
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.set_zlim(0, 100)
        ax.set_title("Superficie de inferencia Mamdani", loc="left")
        ax.view_init(elev=26, azim=-130)
        self.barra = None
        if con_barra:
            self.barra = fig.colorbar(self.superficie, ax=ax, shrink=0.6, pad=0.08)
            self.barra.set_label("Beca (%)")
            self.barra.outline.set_linewidth(LINEA_FINA)
        self.estilizar(t)

    def estilizar(self, t: Tema) -> None:
        estilizar_ejes_3d(self.ax, t)
        self.punto.set_facecolor(t.acento)
        self.punto.set_edgecolor(t.panel)
        if self.barra is not None:
            self.barra.ax.tick_params(colors=t.tenue, labelsize=7)
            self.barra.outline.set_edgecolor(t.borde)
            self.barra.ax.yaxis.label.set_color(t.tenue)

    def actualizar(self, r: ResultadoInferencia) -> None:
        self.punto._offsets3d = ([r.desempeno], [r.entrega], [r.porcentaje])


def estilizar_figura(fig: Figure, t: Tema) -> None:
    fig.set_facecolor(t.panel)


# --------------------------------------------------------------------------- figuras sueltas
def figura_pertenencia(variable: str, valor: float | None = None, nombre_tema: str = "claro") -> Figure:
    t = obtener_tema(nombre_tema)
    fig = Figure(figsize=(6, 3.2), layout="constrained")
    estilizar_figura(fig, t)
    g = GraficaPertenencia(fig.add_subplot(), variable, t)
    if valor is None:
        g.marcador.set_visible(False)
    else:
        g.actualizar(valor)
    g.ax.set_xlabel(cfg.ETIQUETAS_VARIABLE[variable])
    g.ax.set_ylabel("Pertenencia")
    return fig


def figura_agregada(r: ResultadoInferencia, nombre_tema: str = "claro") -> Figure:
    t = obtener_tema(nombre_tema)
    fig = Figure(figsize=(6, 3.2), layout="constrained")
    estilizar_figura(fig, t)
    g = GraficaAgregada(fig.add_subplot(), t)
    g.actualizar(r)
    g.ax.set_title(f"Salida agregada — desempeño {r.desempeno:g}, entrega {r.entrega:g}", loc="left")
    g.ax.set_xlabel("Beca (%)")
    return fig


def figura_superficie(malla: ResultadoMalla, nombre_tema: str = "claro") -> Figure:
    t = obtener_tema(nombre_tema)
    fig = Figure(figsize=(7, 5.5), layout="constrained")
    estilizar_figura(fig, t)
    g = GraficaSuperficie(fig, fig.add_subplot(projection="3d"), malla, t)
    g.punto.set_visible(False)
    return fig
