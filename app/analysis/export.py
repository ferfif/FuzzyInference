"""Exportación de evidencias para el reporte: figuras PNG, tablas CSV/Markdown y resúmenes."""
from __future__ import annotations

import csv
from pathlib import Path

from ..fuzzy import config as cfg
from ..fuzzy.engine import MotorBeca, ResultadoInferencia, formato_mxn
from ..fuzzy.rules import REGLAS, matriz
from . import plots
from .validation import Caso, ResultadoVerificacion, verificar_todo

CASOS_EXPLICADOS = [(40, 95), (90, 30), (70, 75)]
_ARCHIVO_VAR = {"desempeno": "mf_desempeno.png", "entrega": "mf_entrega.png", "beca": "mf_beca.png"}


def _guardar(fig, ruta: Path) -> None:
    fig.savefig(ruta, facecolor=fig.get_facecolor())


def explicar(r: ResultadoInferencia) -> str:
    """Explicación textual (Markdown) de una inferencia."""
    et = cfg.ETIQUETAS_TERMINO
    lineas = [f"### Desempeño = {r.desempeno:g}, entrega = {r.entrega:g}", ""]
    for var in cfg.ENTRADAS:
        grados = ", ".join(f"{et[t]} = {g:.2f}" for t, g in r.grados[var].items())
        lineas.append(f"- Pertenencias de {cfg.ETIQUETAS_VARIABLE[var].lower()}: {grados}")
    lineas.append("- Reglas activadas:")
    for regla in REGLAS:
        if r.fuerzas[regla.id] > 0:
            lineas.append(f"  - **{regla.id}** ({regla.texto}): fuerza = min("
                          f"{r.grados['desempeno'][regla.desempeno]:.2f}, "
                          f"{r.grados['entrega'][regla.entrega]:.2f}) = {r.fuerzas[regla.id]:.2f}")
    recortes = ", ".join(f"{et[t]} ≤ {c:.2f}" for t, c in r.cortes.items() if c > 0)
    lineas += [
        f"- Recortes de la salida (agregación por máximo): {recortes}",
        f"- Centroide de la salida agregada: **{r.porcentaje:.2f} %** → importe "
        f"= {r.porcentaje:.2f} / 100 × ${cfg.SALARIO_MINIMO:,.2f} = **{formato_mxn(r.importe)}**",
        "",
    ]
    return "\n".join(lineas)


def tabla_markdown(casos: list[Caso]) -> str:
    filas = ["| Tipo | Desempeño | Entrega | Reglas activas (fuerza) | Beca (%) | Importe |",
             "|---|---:|---:|---|---:|---:|"]
    for c in casos:
        f = c.fila()
        filas.append(f"| {f['tipo']} | {f['desempeno']:g} | {f['entrega']:g} | {f['reglas_activas']} "
                     f"| {f['beca_pct']:.2f} | {formato_mxn(f['importe_mxn'])} |")
    return "\n".join(filas)


def reglas_markdown() -> str:
    et = cfg.ETIQUETAS_TERMINO
    entregas = cfg.TERMINOS["entrega"]
    lineas = ["## Funciones de pertenencia", "",
              "| Variable | Conjunto | Función |", "|---|---|---|"]
    for var, terminos in cfg.FUNCIONES.items():
        for t, (tipo, params) in terminos.items():
            lineas.append(f"| {cfg.ETIQUETAS_VARIABLE[var]} | {et[t]} | {cfg.descripcion_funcion(tipo, params)} |")
    if cfg.AJUSTES:
        lineas += ["", "### Ajustes respecto a la práctica", ""]
        lineas += [f"- **{cfg.ETIQUETAS_VARIABLE[a.variable]} / {et[a.termino]}**: "
                   f"{a.original} → {a.nuevo}. {a.motivo}" for a in cfg.AJUSTES]
    lineas += ["", "## Matriz de reglas", "",
               "| Desempeño \\ Entrega | " + " | ".join(et[e] for e in entregas) + " |",
               "|---|" + "---|" * len(entregas)]
    for d, fila in zip(cfg.TERMINOS["desempeno"], matriz()):
        lineas.append(f"| {et[d]} | " + " | ".join(et[b] for b in fila) + " |")
    lineas += ["", "## Reglas y justificación", ""]
    lineas += [f"{r.id}. `{r.texto}` — {r.justificacion}" for r in REGLAS]
    return "\n".join(lineas) + "\n"


def exportar(destino: str | Path = "out", verificacion: ResultadoVerificacion | None = None) -> Path:
    """Genera todas las evidencias en ``destino`` y devuelve la ruta absoluta."""
    out = Path(destino).resolve()
    out.mkdir(parents=True, exist_ok=True)
    v = verificacion or verificar_todo(motor=MotorBeca())
    casos = v.casos or verificar_todo(motor=MotorBeca()).casos

    for var, archivo in _ARCHIVO_VAR.items():
        _guardar(plots.figura_pertenencia(var), out / archivo)
    _guardar(plots.figura_superficie(v.malla), out / "superficie.png")

    por_entrada = {(c.resultado.desempeno, c.resultado.entrega): c.resultado for c in casos}
    for d, e in CASOS_EXPLICADOS:
        _guardar(plots.figura_agregada(por_entrada[(d, e)]), out / f"agregada_{d}_{e}.png")

    with open(out / "casos.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(casos[0].fila()))
        w.writeheader()
        w.writerows(c.fila() for c in casos)

    md = ["# Casos de prueba", "", tabla_markdown(casos), "", "## Casos explicados", ""]
    md += [explicar(por_entrada[p]) for p in CASOS_EXPLICADOS]
    (out / "casos.md").write_text("\n".join(md), encoding="utf-8")
    (out / "reglas.md").write_text(reglas_markdown(), encoding="utf-8")
    (out / "verificacion.txt").write_text(v.resumen() + "\n", encoding="utf-8")
    return out
