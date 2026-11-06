"""Motor de inferencia Mamdani con scikit-fuzzy y explicación de cada inferencia.

Operadores: AND = mínimo, implicación = mínimo (recorte), agregación = máximo,
defuzzificación = centroide. El porcentaje oficial lo calcula
``skfuzzy.control.ControlSystemSimulation``; la explicación (grados, fuerzas,
salida agregada) se calcula con el mismo algoritmo que usa skfuzzy internamente
para poder mostrarla y verificarla.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from functools import lru_cache

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

from . import config as cfg
from .rules import REGLAS


# --------------------------------------------------------------------------- utilidades
def validar_entrada(nombre: str, valor: float) -> float:
    try:
        v = float(valor)
    except (TypeError, ValueError):
        raise ValueError(f"{cfg.ETIQUETAS_VARIABLE[nombre]}: '{valor}' no es un número") from None
    if not np.isfinite(v) or v < 0 or v > 100:
        raise ValueError(f"{cfg.ETIQUETAS_VARIABLE[nombre]} = {valor} está fuera del rango [0, 100]")
    return v


def importe(porcentaje: float) -> float:
    """Importe en MXN redondeado a centavos (redondeo comercial)."""
    # El porcentaje se redondea a 6 decimales para descartar ruido de punto flotante
    # (p. ej. 49.99999999999999 → 50.000000).
    monto = Decimal(f"{float(porcentaje):.6f}") / Decimal(100) * Decimal(str(cfg.SALARIO_MINIMO))
    return float(monto.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def formato_mxn(monto: float) -> str:
    return f"${monto:,.2f} MXN"


def grados(variable: str, valor: float) -> dict[str, float]:
    """Grado de pertenencia de ``valor`` a cada término de ``variable``."""
    mfs = cfg.pertenencias(variable)
    return {t: float(fuzz.interp_membership(cfg.UNIVERSO, mf, valor)) for t, mf in mfs.items()}


def fuerzas(g_d: dict[str, float], g_e: dict[str, float]) -> dict[str, float]:
    """Fuerza de disparo de cada regla: min(μ_desempeño, μ_entrega)."""
    return {r.id: min(g_d[r.desempeno], g_e[r.entrega]) for r in REGLAS}


def cortes(f: dict[str, float]) -> dict[str, float]:
    """Nivel de recorte de cada término de salida: máximo de las reglas que lo concluyen."""
    c = {t: 0.0 for t in cfg.TERMINOS[cfg.SALIDA]}
    for r in REGLAS:
        c[r.beca] = max(c[r.beca], f[r.id])
    return c


@lru_cache(maxsize=1)
def _mfs_salida() -> tuple[np.ndarray, ...]:
    mfs = cfg.pertenencias(cfg.SALIDA)
    return tuple(mfs[t] for t in cfg.TERMINOS[cfg.SALIDA])


def agregar(c: dict[str, float] | tuple[float, ...]) -> tuple[np.ndarray, np.ndarray]:
    """Salida agregada (universo sobremuestreado, pertenencia) igual que skfuzzy.

    skfuzzy añade al universo los puntos donde cada función cruza su nivel de
    recorte, recorta (mínimo) y agrega (máximo).
    """
    niveles = tuple(c[t] for t in cfg.TERMINOS[cfg.SALIDA]) if isinstance(c, dict) else c
    x = cfg.UNIVERSO.astype(float)
    nuevos = [x]
    for mf, y in zip(_mfs_salida(), niveles):
        nuevos.append(np.asarray(fuzz.fuzzymath.fuzzy_ops._interp_universe_fast(x, mf, y), float))
    u = np.union1d(x, np.concatenate(nuevos))
    salida = np.zeros_like(u)
    for mf, y in zip(_mfs_salida(), niveles):
        np.maximum(salida, np.minimum(y, np.interp(u, x, mf)), out=salida)
    return u, salida


def centroide(x: np.ndarray, mf: np.ndarray) -> float:
    """Centroide exacto de una función lineal a tramos (misma fórmula que skfuzzy)."""
    x1, x2, y1, y2 = x[:-1], x[1:], mf[:-1], mf[1:]
    h = x2 - x1
    area = h * (y1 + y2) / 2.0
    momento = h / 6.0 * (x1 * (2 * y1 + y2) + x2 * (y1 + 2 * y2))
    total = area.sum()
    if total <= 0:
        raise ValueError("Salida agregada vacía: ninguna regla se activó")
    return float(momento.sum() / total)


# --------------------------------------------------------------------------- sistema skfuzzy
def construir_sistema() -> ctrl.ControlSystem:
    """Construye el ControlSystem Mamdani a partir de la configuración y las reglas."""
    variables = {
        "desempeno": ctrl.Antecedent(cfg.UNIVERSO, "desempeno"),
        "entrega": ctrl.Antecedent(cfg.UNIVERSO, "entrega"),
        "beca": ctrl.Consequent(cfg.UNIVERSO, "beca", defuzzify_method="centroid"),
    }
    for nombre, var in variables.items():
        for termino, mf in cfg.pertenencias(nombre).items():
            var[termino] = mf
    d, e, b = variables["desempeno"], variables["entrega"], variables["beca"]
    reglas = [ctrl.Rule(d[r.desempeno] & e[r.entrega], b[r.beca], label=r.id) for r in REGLAS]
    return ctrl.ControlSystem(reglas)


@dataclass
class ResultadoInferencia:
    desempeno: float
    entrega: float
    porcentaje: float
    importe: float
    grados: dict[str, dict[str, float]]
    fuerzas: dict[str, float]
    cortes: dict[str, float]
    universo_agregado: np.ndarray = field(repr=False)
    agregada: np.ndarray = field(repr=False)

    @property
    def activas(self) -> list[str]:
        return [rid for rid, f in self.fuerzas.items() if f > 0]

    @property
    def importe_texto(self) -> str:
        return formato_mxn(self.importe)


class MotorBeca:
    """Fachada del sistema: infiere y explica."""

    def __init__(self) -> None:
        self.sistema = construir_sistema()
        self._sim = ctrl.ControlSystemSimulation(self.sistema, cache=False)

    def inferir(self, desempeno: float, entrega: float) -> ResultadoInferencia:
        d = validar_entrada("desempeno", desempeno)
        e = validar_entrada("entrega", entrega)

        self._sim.reset()
        self._sim.input["desempeno"] = d
        self._sim.input["entrega"] = e
        self._sim.compute()
        pct = float(self._sim.output["beca"])

        g = {"desempeno": grados("desempeno", d), "entrega": grados("entrega", e)}
        f = fuerzas(g["desempeno"], g["entrega"])
        c = cortes(f)
        u, agg = agregar(c)
        return ResultadoInferencia(d, e, pct, importe(pct), g, f, c, u, agg)


_motor: MotorBeca | None = None


def motor() -> MotorBeca:
    """Instancia compartida (construir el ControlSystem cuesta algunos ms)."""
    global _motor
    if _motor is None:
        _motor = MotorBeca()
    return _motor


def inferir(desempeno: float, entrega: float) -> ResultadoInferencia:
    return motor().inferir(desempeno, entrega)
