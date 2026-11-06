import numpy as np
import pytest

from app.fuzzy import config as cfg
from app.fuzzy.engine import importe, inferir
from app.fuzzy.rules import REGLAS, matriz
from app.fuzzy.vectorized import evaluar_malla


# ---------------------------------------------------------------- 2.1 configuración
def test_universos_completos():
    assert cfg.UNIVERSO.size == 101
    assert cfg.UNIVERSO[0] == 0 and cfg.UNIVERSO[-1] == 100
    assert np.all(np.diff(cfg.UNIVERSO) == 1)


def test_extremos_con_pertenencia_maxima():
    d, e, b = (cfg.pertenencias(v) for v in ("desempeno", "entrega", "beca"))
    assert d["bajo"][0] == 1.0 and d["alto"][-1] == 1.0
    assert e["baja"][0] == 1.0 and e["alta"][-1] == 1.0
    assert b["minima"][0] == 1.0 and b["excelencia"][-1] == 1.0


def test_pico_conjuntos_centrales():
    assert cfg.pertenencias("desempeno")["regular"][50] == 1.0
    assert cfg.pertenencias("entrega")["regular"][50] == 1.0


def test_ajustes_documentados_coinciden_con_config():
    for a in cfg.AJUSTES:
        assert cfg.FUNCIONES[a.variable][a.termino][1] == a.nuevo
        assert a.motivo


# ---------------------------------------------------------------- 2.2 reglas
def test_nueve_reglas_y_matriz_de_la_practica():
    assert len(REGLAS) == 9
    assert [r.id for r in REGLAS] == [f"R{i}" for i in range(1, 10)]
    assert len({(r.desempeno, r.entrega) for r in REGLAS}) == 9
    assert matriz() == [
        ["minima", "baja", "regular"],
        ["baja", "regular", "alta"],
        ["regular", "alta", "excelencia"],
    ]
    assert all(r.justificacion for r in REGLAS)
    assert REGLAS[0].texto == "IF desempeño IS bajo AND entrega IS baja THEN beca IS mínima"


def test_justificacion_casos_cruzados():
    cruzados = [r for r in REGLAS if {r.desempeno, r.entrega} in ({"alto", "baja"}, {"bajo", "alta"})]
    assert len(cruzados) == 2
    assert all("cruzado" in r.justificacion.lower() for r in cruzados)


# ---------------------------------------------------------------- 2.3 inferencia
def test_ambas_entradas_minimas():
    r = inferir(0, 0)
    assert r.activas == ["R1"]
    assert 5 <= r.porcentaje <= 7


def test_ambas_entradas_maximas():
    r = inferir(100, 100)
    assert r.activas == ["R9"]
    assert 93 <= r.porcentaje <= 95


@pytest.mark.parametrize("d,e,var", [(120, 50, "Desempeño"), (50, -5, "Entrega"), ("x", 50, "Desempeño")])
def test_entrada_fuera_de_rango(d, e, var):
    with pytest.raises(ValueError, match=var):
        inferir(d, e)


def test_importe():
    assert importe(50.0) == 4791.24
    assert importe(49.99999999999999) == 4791.24
    assert inferir(0, 0).importe == importe(inferir(0, 0).porcentaje)


def test_explicacion_70_75():
    r = inferir(70, 75)
    assert r.grados["desempeno"]["regular"] == pytest.approx(0.20)
    assert r.grados["desempeno"]["alto"] == pytest.approx(0.80)
    assert r.grados["entrega"]["alta"] == pytest.approx(1.00)
    assert r.activas == ["R8", "R9"]
    assert r.fuerzas["R8"] == pytest.approx(0.20)
    assert r.fuerzas["R9"] == pytest.approx(0.80)


def test_salida_agregada_y_centroide_coinciden_con_skfuzzy():
    from app.fuzzy.engine import centroide
    for p in [(0, 0), (35, 35), (70, 75), (90, 30)]:
        r = inferir(*p)
        assert centroide(r.universo_agregado, r.agregada) == pytest.approx(r.porcentaje, abs=1e-9)


# ---------------------------------------------------------------- 2.4 ruta vectorizada
def test_vectorizada_coincide_con_skfuzzy():
    paso = np.arange(0, 101, 10)
    m = evaluar_malla(paso, paso)
    for i, d in enumerate(paso):
        for j, e in enumerate(paso):
            assert abs(m.beca[i, j] - inferir(d, e).porcentaje) < 1e-6
    for d, e in [(40, 95), (90, 30), (70, 75)]:
        assert abs(evaluar_malla([d], [e]).beca[0, 0] - inferir(d, e).porcentaje) < 1e-6
