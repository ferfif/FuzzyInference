"""Empaqueta el proyecto para la entrega: python scripts/make_zip.py [destino.zip]"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
NOMBRE = "Practica08_Beca_Difusa"

INCLUIR = ["main.py", "README.md", "requirements.txt", "requirements-dev.txt", "pytest.ini",
           "app", "tests", "scripts"]
EXCLUIR_DIRS = {".venv", "__pycache__", ".pytest_cache", "out", "openspec", ".git", ".claude"}
EXCLUIR_SUFIJOS = {".pyc", ".pyo", ".zip"}


def archivos() -> list[Path]:
    salida = []
    for entrada in INCLUIR:
        ruta = RAIZ / entrada
        candidatos = [ruta] if ruta.is_file() else sorted(p for p in ruta.rglob("*") if p.is_file())
        for p in candidatos:
            rel = p.relative_to(RAIZ)
            if EXCLUIR_DIRS.intersection(rel.parts) or p.suffix in EXCLUIR_SUFIJOS:
                continue
            salida.append(p)
    return salida


def crear_zip(destino: Path | None = None) -> Path:
    destino = (destino or RAIZ / f"{NOMBRE}.zip").resolve()
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in archivos():
            zf.write(p, Path(NOMBRE) / p.relative_to(RAIZ))
    return destino


if __name__ == "__main__":
    ruta = crear_zip(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
    print(f"ZIP creado: {ruta}")
