"""Verificaciones de cobertura y monotonía, y batería de casos de prueba."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ..fuzzy import config as cfg
from ..fuzzy.engine import MotorBeca, ResultadoInferencia, motor as motor_compartido
from ..fuzzy.vectorized import ResultadoMalla, evaluar_malla

TOLERANCIA = 0.01  # puntos porcentuales

CASOS_OBLIGATORIOS = [(0, 0), (100, 100), (40, 95), (90, 30), (70, 75)]
CASOS_SOLAPAMIENTO = [(35, 35), (50, 60), (65, 40), (30, 70)]


# --------------------------------------------------------------------------- cobertura
@dataclass
class ResultadoCobertura:
    completa: bool
    sin_cobertura: list[tuple[float, float]]
    suma_minima: dict[str, float]          # mínimo de Σ pertenencias por variable de entrada
    puntos: int

    @property
    def solapamiento_ok(self) -> bool:
        return all(v > 0 for v in self.suma_minima.values())


def verificar_cobertura(malla: ResultadoMalla | None = None) -> ResultadoCobertura:
    malla = malla or evaluar_malla()
    fmax = malla.fuerza_maxima
    idx = np.argwhere(fmax <= 0)
    sin = [(float(malla.desempeno[i]), float(malla.entrega[j])) for i, j in idx]
    sumas = {v: float(np.sum(list(cfg.pertenencias(v).values()), axis=0).min()) for v in cfg.ENTRADAS}
    return ResultadoCobertura(not sin, sin, sumas, int(fmax.size))


# --------------------------------------------------------------------------- monotonía
@dataclass(frozen=True)
class Descenso:
    variable: str          # variable que aumenta
    desde: float           # valor de la variable que aumenta
    hasta: float
    fijo: float            # valor de la otra variable
    magnitud: float        # diferencia negativa (pp)

    def __str__(self) -> str:
        otra = "entrega" if self.variable == "desempeno" else "desempeno"
        return (f"{cfg.ETIQUETAS_VARIABLE[self.variable]} {self.desde:g}→{self.hasta:g} "
                f"({otra} = {self.fijo:g}): {self.magnitud:+.4f} pp")


@dataclass
class ResultadoMonotonia:
    monotono: bool
    descensos: list[Descenso]
    peor_diferencia: dict[str, float]      # mínima diferencia consecutiva por dirección
    tolerancia: float = TOLERANCIA


def detectar_descensos(beca: np.ndarray, d: np.ndarray, e: np.ndarray,
                       tol: float = TOLERANCIA) -> ResultadoMonotonia:
    """``beca[i, j]`` = salida para (d[i], e[j]); ambos ejes en orden ascendente."""
    dd = np.diff(beca, axis=0)   # aumenta desempeño, entrega fija
    de = np.diff(beca, axis=1)   # aumenta entrega, desempeño fijo
    descensos = [Descenso("desempeno", float(d[i]), float(d[i + 1]), float(e[j]), float(dd[i, j]))
                 for i, j in np.argwhere(dd < -tol)]
    descensos += [Descenso("entrega", float(e[j]), float(e[j + 1]), float(d[i]), float(de[i, j]))
                  for i, j in np.argwhere(de < -tol)]
    peor = {"desempeno": float(np.nanmin(dd)) if dd.size else 0.0,
            "entrega": float(np.nanmin(de)) if de.size else 0.0}
    return ResultadoMonotonia(not descensos, descensos, peor, tol)


def verificar_monotonia(malla: ResultadoMalla | None = None,
                        tol: float = TOLERANCIA) -> ResultadoMonotonia:
    malla = malla or evaluar_malla()
    return detectar_descensos(malla.beca, malla.desempeno, malla.entrega, tol)


# --------------------------------------------------------------------------- casos de prueba
@dataclass
class Caso:
    tipo: str              # "obligatorio" | "solapamiento"
    resultado: ResultadoInferencia

    def fila(self) -> dict:
        r = self.resultado
        return {
            "tipo": self.tipo,
            "desempeno": r.desempeno,
            "entrega": r.entrega,
            "reglas_activas": ", ".join(f"{rid}={r.fuerzas[rid]:.2f}" for rid in r.activas),
            "beca_pct": round(r.porcentaje, 2),
            "importe_mxn": r.importe,
        }


def casos_prueba(motor: MotorBeca | None = None) -> list[Caso]:
    """``motor`` permite usar una instancia propia (p. ej. desde un hilo de fondo)."""
    m = motor or motor_compartido()
    return ([Caso("obligatorio", m.inferir(*p)) for p in CASOS_OBLIGATORIOS]
            + [Caso("solapamiento", m.inferir(*p)) for p in CASOS_SOLAPAMIENTO])


# --------------------------------------------------------------------------- todo junto
@dataclass
class ResultadoVerificacion:
    malla: ResultadoMalla
    cobertura: ResultadoCobertura
    monotonia: ResultadoMonotonia
    casos: list[Caso] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.cobertura.completa and self.cobertura.solapamiento_ok and self.monotonia.monotono

    def resumen(self) -> str:
        c, m = self.cobertura, self.monotonia
        lineas = [
            "VERIFICACIÓN DEL SISTEMA DIFUSO DE BECAS",
            "=" * 44,
            f"Malla: {self.malla.desempeno.size} × {self.malla.entrega.size} = {c.puntos} puntos",
            "",
            f"Cobertura: {'COMPLETA' if c.completa else 'INCOMPLETA'} "
            f"({len(c.sin_cobertura)} puntos sin regla activa)",
        ]
        lineas += [f"  Σ pertenencias mínima en {cfg.ETIQUETAS_VARIABLE[v]}: {s:.3f}"
                   for v, s in c.suma_minima.items()]
        lineas += [f"  sin cobertura: {p}" for p in c.sin_cobertura[:20]]
        lineas += [
            "",
            f"Monotonía (tolerancia {m.tolerancia} pp): {'MONÓTONA' if m.monotono else 'NO MONÓTONA'} "
            f"({len(m.descensos)} descensos)",
            f"  Peor diferencia al aumentar desempeño: {m.peor_diferencia['desempeno']:+.6f} pp",
            f"  Peor diferencia al aumentar entrega:   {m.peor_diferencia['entrega']:+.6f} pp",
        ]
        lineas += [f"  {d}" for d in m.descensos[:20]]
        if cfg.AJUSTES:
            lineas += ["", "Ajustes respecto a la práctica:"]
            lineas += [f"  {a.variable}.{a.termino}: {a.original} → {a.nuevo}" for a in cfg.AJUSTES]
        return "\n".join(lineas)


def verificar_todo(con_casos: bool = True, motor: MotorBeca | None = None) -> ResultadoVerificacion:
    malla = evaluar_malla()
    return ResultadoVerificacion(
        malla, verificar_cobertura(malla), verificar_monotonia(malla),
        casos_prueba(motor) if con_casos else [],
    )
