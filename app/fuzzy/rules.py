"""Base de nueve reglas difusas (matriz desempeño × entrega) con su justificación."""
from __future__ import annotations

from dataclasses import dataclass

from .config import ETIQUETAS_TERMINO, TERMINOS


@dataclass(frozen=True)
class Regla:
    id: str
    desempeno: str
    entrega: str
    beca: str
    justificacion: str

    @property
    def texto(self) -> str:
        return (f"IF desempeño IS {ETIQUETAS_TERMINO[self.desempeno].lower()} "
                f"AND entrega IS {ETIQUETAS_TERMINO[self.entrega].lower()} "
                f"THEN beca IS {ETIQUETAS_TERMINO[self.beca].lower()}")


# Criterio general: ambos indicadores pesan igual. El nivel de beca es la suma de los
# niveles de las entradas (0=bajo, 1=regular, 2=alto) → 0..4 = mínima..excelencia.
# Así cada mejora de un nivel en cualquiera de las entradas sube un nivel la beca,
# lo que ordena la matriz de forma monótona.
REGLAS: tuple[Regla, ...] = (
    # Numeración igual a la del ejemplo de la práctica (ordenadas por nivel del consecuente).
    Regla("R1", "bajo", "baja", "minima",
          "Ningún indicador muestra compromiso académico; no hay mérito que respalde un apoyo "
          "más allá del mínimo."),
    Regla("R2", "regular", "baja", "baja",
          "Rendimiento aceptable con poca entrega: el conocimiento existe, pero la falta de "
          "constancia limita el apoyo a uno reducido."),
    Regla("R3", "bajo", "regular", "baja",
          "Cumplir con parte de las actividades muestra cierto esfuerzo pese a las evaluaciones "
          "bajas; se reconoce con un apoyo reducido. Simétrica a R2."),
    Regla("R4", "alto", "baja", "regular",
          "Caso cruzado: domina los contenidos pero casi no entrega actividades. Su capacidad "
          "justifica un apoyo intermedio; la falta de constancia impide uno alto. Recibe lo mismo "
          "que R6: un indicador sobresaliente compensa parcialmente al otro, pero no del todo."),
    Regla("R5", "regular", "regular", "regular",
          "Desempeño y entrega intermedios: estudiante promedio, apoyo intermedio."),
    Regla("R6", "bajo", "alta", "regular",
          "Caso cruzado: entrega casi todo pero no lo refleja en evaluaciones. El esfuerzo "
          "constante merece apoyo intermedio para que mejore su rendimiento, pero sin resultados "
          "no alcanza un apoyo alto. Es simétrica a R4 porque ambos indicadores pesan igual."),
    Regla("R7", "alto", "regular", "alta",
          "Evaluaciones altas con entrega aceptable: buen mérito académico, apoyo elevado."),
    Regla("R8", "regular", "alta", "alta",
          "Entrega sobresaliente con evaluaciones aceptables: compromiso alto que se premia "
          "con apoyo elevado. Simétrica a R7."),
    Regla("R9", "alto", "alta", "excelencia",
          "Ambos indicadores sobresalientes: perfil de excelencia, apoyo máximo."),
)


def matriz() -> list[list[str]]:
    """Consecuentes en forma de matriz [desempeño][entrega] (orden lingüístico)."""
    idx = {(r.desempeno, r.entrega): r.beca for r in REGLAS}
    return [[idx[(d, e)] for e in TERMINOS["entrega"]] for d in TERMINOS["desempeno"]]
