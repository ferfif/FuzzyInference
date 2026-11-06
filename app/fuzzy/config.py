"""Única fuente de verdad del sistema difuso: universos, funciones de pertenencia y constantes.

Las claves internas son ASCII (``desempeno``, ``minima``…) y las etiquetas visibles
llevan acentos; así se evitan problemas de codificación con scikit-fuzzy y archivos exportados.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import skfuzzy as fuzz

SALARIO_MINIMO = 9582.47  # MXN, salario mínimo mensual de referencia

UNIVERSO = np.arange(0, 101, 1)  # 0..100 con paso 1, ambos extremos incluidos

# Variables -------------------------------------------------------------------
ENTRADAS = ("desempeno", "entrega")
SALIDA = "beca"

ETIQUETAS_VARIABLE = {
    "desempeno": "Desempeño",
    "entrega": "Entrega (%)",
    "beca": "Beca (%)",
}

# Orden lingüístico ascendente de cada variable (se usa en reglas, colores y monotonía)
TERMINOS = {
    "desempeno": ("bajo", "regular", "alto"),
    "entrega": ("baja", "regular", "alta"),
    "beca": ("minima", "baja", "regular", "alta", "excelencia"),
}

ETIQUETAS_TERMINO = {
    "bajo": "Bajo", "baja": "Baja", "regular": "Regular", "alto": "Alto",
    "alta": "Alta", "minima": "Mínima", "excelencia": "Excelencia",
}

# Funciones de pertenencia (tipo, parámetros): tabla de la práctica + los ajustes de AJUSTES.
FUNCIONES: dict[str, dict[str, tuple[str, tuple[float, ...]]]] = {
    "desempeno": {
        "bajo": ("trap", (0, 0, 25, 50)),      # práctica: (0, 0, 20, 50) — ver AJUSTES
        "regular": ("tri", (25, 50, 75)),
        "alto": ("trap", (50, 75, 100, 100)),  # práctica: (50, 80, 100, 100) — ver AJUSTES
    },
    "entrega": {
        "baja": ("trap", (0, 0, 25, 50)),      # práctica: (0, 0, 20, 50) — ver AJUSTES
        "regular": ("tri", (25, 50, 75)),
        "alta": ("trap", (50, 75, 100, 100)),  # práctica: (50, 80, 100, 100) — ver AJUSTES
    },
    "beca": {
        "minima": ("z", (0, 20)),
        "baja": ("tri", (10, 25, 40)),
        "regular": ("tri", (30, 50, 70)),
        "alta": ("tri", (60, 75, 90)),
        "excelencia": ("s", (80, 100)),
    },
}


@dataclass(frozen=True)
class Ajuste:
    """Registro de un cambio a las funciones de la práctica (p. ej. para lograr monotonía)."""

    variable: str
    termino: str
    original: tuple
    nuevo: tuple
    motivo: str


_MOTIVO_BAJO = (
    "Con (0,0,20,50) el conjunto bajo empieza a caer en 20 pero 'regular' (25,50,75) no sube "
    "hasta 25: entre 20 y 25 aumentar la entrada solo resta fuerza a las reglas que concluyen "
    "'baja' mientras 'mínima' se mantiene, y el centroide desciende hasta 0.0128 pp "
    "(p. ej. desempeño 24→25 con entrega 47). Ningún ajuste de la salida puede evitarlo. "
    "Alinear la caída en 25 forma una partición complementaria (bajo + regular = 1) y "
    "elimina todos los descensos."
)
_MOTIVO_ALTO = (
    "Simétrico al ajuste de 'bajo': 'regular' termina en 75 pero el conjunto alto solo empezaba "
    "a saturar en 80, provocando descensos entre 75 y 80. Con (50,75,100,100) regular + alto = 1."
)

# Registro de ajustes respecto a la tabla de la práctica (verificados con test_monotonia).
AJUSTES: list[Ajuste] = [
    Ajuste("desempeno", "bajo", (0, 0, 20, 50), (0, 0, 25, 50), _MOTIVO_BAJO),
    Ajuste("desempeno", "alto", (50, 80, 100, 100), (50, 75, 100, 100), _MOTIVO_ALTO),
    Ajuste("entrega", "baja", (0, 0, 20, 50), (0, 0, 25, 50), _MOTIVO_BAJO),
    Ajuste("entrega", "alta", (50, 80, 100, 100), (50, 75, 100, 100), _MOTIVO_ALTO),
]


def descripcion_funcion(tipo: str, params: tuple) -> str:
    nombres = {"trap": "Trapezoidal", "tri": "Triangular", "z": "Z", "s": "S"}
    return f"{nombres[tipo]}({', '.join(f'{p:g}' for p in params)})"


def evaluar_funcion(tipo: str, params: tuple, x: np.ndarray = UNIVERSO) -> np.ndarray:
    """Devuelve el arreglo de pertenencia de una función sobre el universo ``x``."""
    if tipo == "trap":
        return fuzz.trapmf(x, list(params))
    if tipo == "tri":
        return fuzz.trimf(x, list(params))
    if tipo == "z":
        return fuzz.zmf(x, *params)
    if tipo == "s":
        return fuzz.smf(x, *params)
    raise ValueError(f"Tipo de función desconocido: {tipo}")


def pertenencias(variable: str) -> dict[str, np.ndarray]:
    """Arreglos de pertenencia de todos los términos de ``variable`` (en orden lingüístico)."""
    return {t: evaluar_funcion(*FUNCIONES[variable][t]) for t in TERMINOS[variable]}
