"""Inferencia Mamdani sobre mallas completas (cobertura, monotonía y superficie).

Las pertenencias y fuerzas de disparo se calculan vectorizadas con numpy. La
defuzzificación replica el algoritmo de skfuzzy (sobremuestreo + centroide lineal a
tramos) y se memoiza por niveles de recorte, porque muchos puntos de la malla
comparten la misma combinación.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import config as cfg
from .engine import agregar, centroide
from .rules import REGLAS


@dataclass
class ResultadoMalla:
    desempeno: np.ndarray          # (n,)
    entrega: np.ndarray            # (m,)
    fuerzas: np.ndarray            # (9, n, m) en el orden de REGLAS
    beca: np.ndarray               # (n, m) porcentaje defuzzificado; NaN si no hay cobertura

    @property
    def fuerza_maxima(self) -> np.ndarray:
        return self.fuerzas.max(axis=0)


def _grados(variable: str, valores: np.ndarray) -> dict[str, np.ndarray]:
    x = cfg.UNIVERSO.astype(float)
    return {t: np.interp(valores, x, mf) for t, mf in cfg.pertenencias(variable).items()}


def evaluar_malla(desempeno=None, entrega=None) -> ResultadoMalla:
    """Evalúa el sistema en el producto cartesiano ``desempeno × entrega`` (0..100 por defecto)."""
    d = np.asarray(cfg.UNIVERSO if desempeno is None else desempeno, float)
    e = np.asarray(cfg.UNIVERSO if entrega is None else entrega, float)
    gd, ge = _grados("desempeno", d), _grados("entrega", e)

    f = np.stack([np.minimum(gd[r.desempeno][:, None], ge[r.entrega][None, :]) for r in REGLAS])

    terminos = cfg.TERMINOS[cfg.SALIDA]
    niveles = np.zeros((len(terminos), d.size, e.size))
    for k, r in enumerate(REGLAS):
        i = terminos.index(r.beca)
        np.maximum(niveles[i], f[k], out=niveles[i])

    beca = np.full((d.size, e.size), np.nan)
    memo: dict[tuple, float] = {}
    for i in range(d.size):
        for j in range(e.size):
            clave = tuple(niveles[:, i, j].tolist())
            if not any(clave):
                continue
            if clave not in memo:
                memo[clave] = centroide(*agregar(clave))
            beca[i, j] = memo[clave]
    return ResultadoMalla(d, e, f, beca)
