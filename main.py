"""Punto de entrada.

    python main.py                 # interfaz gráfica
    python main.py --verify        # cobertura, monotonía y casos de prueba en consola
    python main.py --export out    # figuras y tablas para el reporte
"""
from __future__ import annotations

import argparse
import sys
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning, module="skfuzzy")


def _consola_utf8() -> None:
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sistema difuso de recomendación de becas (Mamdani).")
    parser.add_argument("--verify", action="store_true", help="ejecuta las verificaciones y casos de prueba")
    parser.add_argument("--export", metavar="DIR", nargs="?", const="out",
                        help="exporta figuras y tablas para el reporte (por defecto: out/)")
    args = parser.parse_args(argv)

    if not (args.verify or args.export):
        from app.gui.app_window import ejecutar
        ejecutar()
        return 0

    _consola_utf8()
    from app.analysis.export import tabla_markdown
    from app.analysis.validation import verificar_todo

    v = verificar_todo()
    if args.verify:
        print(v.resumen())
        print()
        print(tabla_markdown(v.casos))
    if args.export:
        from app.analysis.export import exportar
        print(f"\nEvidencias exportadas en: {exportar(args.export, v)}")
    return 0 if v.ok else 1


if __name__ == "__main__":
    sys.exit(main())
