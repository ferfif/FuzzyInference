import numpy as np
import pytest

from app.analysis.validation import (
    CASOS_OBLIGATORIOS, CASOS_SOLAPAMIENTO, casos_prueba, detectar_descensos,
    verificar_cobertura, verificar_monotonia,
)
from app.fuzzy.engine import inferir
from app.fuzzy.vectorized import evaluar_malla


@pytest.fixture(scope="module")
def malla():
    return evaluar_malla()


def test_cobertura_completa(malla):
    c = verificar_cobertura(malla)
    assert c.puntos == 101 * 101
    assert c.completa and c.sin_cobertura == []
    assert c.solapamiento_ok


def test_monotonia(malla):
    m = verificar_monotonia(malla)
    assert m.monotono, [str(d) for d in m.descensos[:5]]
    assert m.descensos == []


def test_detecta_descenso_inyectado():
    d = e = np.arange(5.0)
    beca = d[:, None] + e[None, :]
    beca[3, 2] -= 1.5           # (3,2)=3.5 queda por debajo de (2,2)=4 y de (3,1)=4
    m = detectar_descensos(beca, d, e)
    assert not m.monotono
    dirs = {(x.variable, x.desde, x.hasta, x.fijo) for x in m.descensos}
    assert ("desempeno", 2.0, 3.0, 2.0) in dirs
    assert ("entrega", 1.0, 2.0, 3.0) in dirs
    assert all(x.magnitud < -0.01 for x in m.descensos)


def test_tolerancia_ignora_ruido():
    d = e = np.arange(3.0)
    beca = d[:, None] + e[None, :]
    beca[2, 2] = beca[1, 2] - 0.005
    assert detectar_descensos(beca, d, e).monotono


def test_tabla_de_casos():
    casos = casos_prueba()
    assert len(casos) == len(CASOS_OBLIGATORIOS) + len(CASOS_SOLAPAMIENTO)
    for c in casos:
        f = c.fila()
        assert set(f) == {"tipo", "desempeno", "entrega", "reglas_activas", "beca_pct", "importe_mxn"}
        assert f["reglas_activas"]


def test_casos_cruzados_coherentes():
    bajo, alto = inferir(0, 0).porcentaje, inferir(100, 100).porcentaje
    for p in [(90, 30), (40, 95)]:
        assert bajo < inferir(*p).porcentaje < alto
