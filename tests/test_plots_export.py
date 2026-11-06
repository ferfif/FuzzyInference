import matplotlib

matplotlib.use("Agg")

from app.analysis import plots  # noqa: E402
from app.analysis.export import exportar  # noqa: E402
from app.fuzzy.engine import inferir  # noqa: E402
from app.fuzzy.vectorized import evaluar_malla  # noqa: E402


def _render(fig):
    fig.canvas.draw()


def test_figuras_se_generan_en_ambos_temas():
    r = inferir(70, 75)
    malla = evaluar_malla(range(0, 101, 10), range(0, 101, 10))
    for tema in ("claro", "oscuro"):
        for var in ("desempeno", "entrega", "beca"):
            _render(plots.figura_pertenencia(var, 40, tema))
        _render(plots.figura_agregada(r, tema))
        _render(plots.figura_superficie(malla, tema))


def test_grosores_minimalistas():
    fig = plots.figura_pertenencia("beca")
    assert all(l.get_linewidth() <= 1.5 for l in fig.axes[0].get_lines())


def test_exportacion_completa(tmp_path):
    out = exportar(tmp_path / "out")
    esperados = {"mf_desempeno.png", "mf_entrega.png", "mf_beca.png", "superficie.png",
                 "agregada_40_95.png", "agregada_90_30.png", "agregada_70_75.png",
                 "casos.csv", "casos.md", "reglas.md", "verificacion.txt"}
    assert esperados <= {p.name for p in out.iterdir()}
    assert "COMPLETA" in (out / "verificacion.txt").read_text(encoding="utf-8")
