"""Tema visual compartido por la GUI y las gráficas: paleta, grosores y tipografía."""
from __future__ import annotations

from dataclasses import dataclass

import matplotlib as mpl

from ..fuzzy import config as cfg

# Un color por conjunto lingüístico, en orden ascendente (rojo → verde), igual en todas las gráficas.
_ESCALA_5 = ("#d1495b", "#ec7d3a", "#e3b43a", "#8cbf4a", "#2e8b57")
_ESCALA_3 = ("#d1495b", "#d9a032", "#2e8b57")

LINEA = 1.2          # grosor de las curvas de pertenencia
LINEA_FINA = 0.6     # ejes, marcadores secundarios
LINEA_REJILLA = 0.3
FUENTES = ["Segoe UI", "Inter", "Helvetica Neue", "Arial", "DejaVu Sans"]


@dataclass(frozen=True)
class Tema:
    nombre: str
    fondo: str        # fondo de la ventana
    panel: str        # tarjetas y fondo de figuras
    texto: str
    tenue: str        # texto secundario
    borde: str        # bordes de 1 px
    rejilla: str
    acento: str       # marcadores, centroide, salida agregada
    resaltado: str    # filas de reglas activas


CLARO = Tema("claro", "#f4f5f7", "#ffffff", "#1f2328", "#6b7280", "#d9dce1", "#eceef1", "#2f6fd6", "#e6effc")
OSCURO = Tema("oscuro", "#121316", "#1a1b1f", "#e6e7ea", "#9aa0a8", "#2e3036", "#25272c", "#5b9cf0", "#1f2b3d")


def tema(nombre: str) -> Tema:
    return OSCURO if nombre.lower() in ("dark", "oscuro") else CLARO


def colores(variable: str) -> dict[str, str]:
    terminos = cfg.TERMINOS[variable]
    escala = _ESCALA_5 if len(terminos) == 5 else _ESCALA_3
    return dict(zip(terminos, escala))


def configurar_matplotlib() -> None:
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": FUENTES,
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.titleweight": "normal",
        "axes.linewidth": LINEA_FINA,
        "lines.linewidth": LINEA,
        "grid.linewidth": LINEA_REJILLA,
        "xtick.major.width": LINEA_FINA,
        "ytick.major.width": LINEA_FINA,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "legend.frameon": False,
        "legend.fontsize": 8,
        "figure.dpi": 100,
        "savefig.dpi": 160,
    })


def _color_titulos(ax, color: str) -> None:
    # set_title(loc="left") usa un objeto de texto distinto de ax.title
    for nombre in ("title", "_left_title", "_right_title"):
        txt = getattr(ax, nombre, None)
        if txt is not None:
            txt.set_color(color)


def estilizar_ejes(ax, t: Tema) -> None:
    """Ejes 2D minimalistas: sin marco superior/derecho, rejilla tenue."""
    ax.set_facecolor(t.panel)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(t.borde)
        ax.spines[lado].set_linewidth(LINEA_FINA)
    ax.tick_params(colors=t.tenue, labelsize=8)
    _color_titulos(ax, t.texto)
    ax.xaxis.label.set_color(t.tenue)
    ax.yaxis.label.set_color(t.tenue)
    ax.grid(True, color=t.rejilla, linewidth=LINEA_REJILLA)
    ax.set_axisbelow(True)
    leyenda = ax.get_legend()
    if leyenda:
        for txt in leyenda.get_texts():
            txt.set_color(t.texto)


def estilizar_ejes_3d(ax, t: Tema) -> None:
    ax.set_facecolor(t.panel)
    for eje in (ax.xaxis, ax.yaxis, ax.zaxis):
        eje.pane.fill = False
        eje.pane.set_facecolor(t.panel)
        eje.pane.set_edgecolor(t.borde)
        eje.line.set_color(t.borde)
        eje.line.set_linewidth(LINEA_FINA)
        eje.label.set_color(t.tenue)
        try:  # atributo interno de mplot3d; si cambia, solo se pierde el estilo de rejilla
            eje._axinfo["grid"].update(color=t.rejilla, linewidth=LINEA_REJILLA)
        except (AttributeError, KeyError):
            pass
    ax.tick_params(colors=t.tenue, labelsize=7)
    _color_titulos(ax, t.texto)


configurar_matplotlib()
