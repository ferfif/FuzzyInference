"""Pestaña Verificación: cobertura, monotonía, casos de prueba y exportación (en segundo plano)."""
from __future__ import annotations

import threading
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from ...analysis.export import exportar
from ...analysis.validation import ResultadoVerificacion, verificar_todo
from ...fuzzy.engine import MotorBeca, formato_mxn
from ..theme import Tema
from ..widgets import boton, etiqueta, par, tarjeta


class PanelVerificacion(ctk.CTkFrame):
    def __init__(self, master, t: Tema):
        super().__init__(master, fg_color="transparent")
        self.pendiente = False
        self.verificacion: ResultadoVerificacion | None = None
        self._hilo: threading.Thread | None = None
        self._resultado = None

        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", padx=4, pady=(4, 8))
        self.btn_verificar = boton(barra, "Verificar", self.verificar, width=120)
        self.btn_verificar.pack(side="left")
        self.btn_exportar = boton(barra, "Exportar evidencias…", self.exportar, width=170)
        self.btn_exportar.pack(side="left", padx=8)
        self.progreso = ctk.CTkProgressBar(barra, mode="indeterminate", height=2, width=160,
                                           progress_color=par("acento"), fg_color=par("borde"))
        self.estado = etiqueta(barra, "Pulsa «Verificar» para evaluar la malla 101 × 101.", 12, "tenue")
        self.estado.pack(side="left", padx=8)

        indicadores = ctk.CTkFrame(self, fg_color="transparent")
        indicadores.pack(fill="x", padx=4, pady=(0, 8))
        indicadores.grid_columnconfigure((0, 1, 2), weight=1, uniform="i")
        self.ind = {}
        for col, (clave, titulo) in enumerate([("cobertura", "Cobertura"), ("monotonia", "Monotonía"),
                                               ("solape", "Solapamiento")]):
            c = tarjeta(indicadores)
            c.grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 4, 0 if col == 2 else 4))
            etiqueta(c, titulo, 11, "tenue").pack(anchor="w", padx=14, pady=(10, 0))
            valor = etiqueta(c, "—", 18)
            valor.pack(anchor="w", padx=14)
            detalle = etiqueta(c, "", 11, "tenue")
            detalle.pack(anchor="w", padx=14, pady=(0, 10))
            self.ind[clave] = (valor, detalle)

        self.texto = ctk.CTkTextbox(self, font=ctk.CTkFont(family="Consolas", size=12), wrap="none",
                                    fg_color=par("panel"), border_width=1, border_color=par("borde"),
                                    corner_radius=8, text_color=par("texto"))
        self.texto.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        self.texto.configure(state="disabled")

    def aplicar_tema(self, t: Tema) -> None:
        pass

    def actualizar(self, r) -> None:
        pass

    # ------------------------------------------------------------------ trabajo en segundo plano
    def _ocupado(self, mensaje: str) -> None:
        self.btn_verificar.configure(state="disabled")
        self.btn_exportar.configure(state="disabled")
        self.estado.configure(text=mensaje)
        self.progreso.pack(side="left", padx=(8, 0), before=self.estado)
        self.progreso.start()

    def _libre(self, mensaje: str) -> None:
        self.progreso.stop()
        self.progreso.pack_forget()
        self.btn_verificar.configure(state="normal")
        self.btn_exportar.configure(state="normal")
        self.estado.configure(text=mensaje)

    def _lanzar(self, tarea, al_terminar) -> None:
        self._resultado = None

        def trabajo():
            try:
                self._resultado = ("ok", tarea())
            except Exception as exc:  # se muestra en la GUI
                self._resultado = ("error", exc)

        self._hilo = threading.Thread(target=trabajo, daemon=True)
        self._hilo.start()
        self._esperar(al_terminar)

    def _esperar(self, al_terminar) -> None:
        if self._hilo is not None and self._hilo.is_alive():
            self.after(80, self._esperar, al_terminar)
            return
        estado, valor = self._resultado
        if estado == "error":
            self._libre(f"Error: {valor}")
        else:
            al_terminar(valor)

    # ------------------------------------------------------------------ acciones
    def verificar(self) -> None:
        self._ocupado("Verificando cobertura y monotonía…")
        self._lanzar(lambda: verificar_todo(motor=MotorBeca()), self._mostrar)

    def _mostrar(self, v: ResultadoVerificacion) -> None:
        self.verificacion = v
        c, m = v.cobertura, v.monotonia
        ok, mal = par("acento"), ("#c0392b", "#ef6b5b")
        self.ind["cobertura"][0].configure(text="Completa" if c.completa else "Incompleta",
                                           text_color=ok if c.completa else mal)
        self.ind["cobertura"][1].configure(text=f"{len(c.sin_cobertura)} de {c.puntos} puntos sin regla activa")
        self.ind["monotonia"][0].configure(text="Monótona" if m.monotono else "No monótona",
                                           text_color=ok if m.monotono else mal)
        self.ind["monotonia"][1].configure(text=f"{len(m.descensos)} descensos (tolerancia {m.tolerancia} pp)")
        smin = min(c.suma_minima.values())
        self.ind["solape"][0].configure(text="Correcto" if c.solapamiento_ok else "Con huecos",
                                        text_color=ok if c.solapamiento_ok else mal)
        self.ind["solape"][1].configure(text=f"Σ pertenencias mínima = {smin:.2f}")

        filas = ["", "CASOS DE PRUEBA", "=" * 44]
        filas.append(f"{'tipo':<13}{'desemp.':>8}{'entrega':>9}   {'beca %':>7}  {'importe':>16}   reglas activas")
        for caso in v.casos:
            f = caso.fila()
            filas.append(f"{f['tipo']:<13}{f['desempeno']:>8g}{f['entrega']:>9g}   {f['beca_pct']:>7.2f}  "
                         f"{formato_mxn(f['importe_mxn']):>16}   {f['reglas_activas']}")
        self._escribir(v.resumen() + "\n" + "\n".join(filas))
        self._libre("Verificación terminada." if v.ok else "Verificación con fallos.")

    def _escribir(self, texto: str) -> None:
        self.texto.configure(state="normal")
        self.texto.delete("1.0", "end")
        self.texto.insert("1.0", texto)
        self.texto.configure(state="disabled")

    def exportar(self) -> None:
        carpeta = filedialog.askdirectory(title="Carpeta de evidencias", initialdir=str(Path.cwd()),
                                          mustexist=False)
        if not carpeta:
            return
        v = self.verificacion
        self._ocupado("Exportando figuras y tablas…")
        self._lanzar(lambda: exportar(carpeta, v), lambda ruta: self._libre(f"Evidencias exportadas en: {ruta}"))

