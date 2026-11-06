"""Pestaña Reglas: matriz 3×3, grados de pertenencia y lista R1–R9 con fuerza y justificación."""
from __future__ import annotations

import customtkinter as ctk

from ...fuzzy import config as cfg
from ...fuzzy.engine import ResultadoInferencia
from ...fuzzy.rules import REGLAS
from ..theme import Tema
from ..widgets import etiqueta, fuente, par, separador, tarjeta

ET = cfg.ETIQUETAS_TERMINO


class PanelReglas(ctk.CTkScrollableFrame):
    def __init__(self, master, t: Tema):
        super().__init__(master, fg_color=par("fondo"))
        self.grid_columnconfigure(0, weight=1)
        self.pendiente = True

        # --- grados de pertenencia
        self.lbl_grados = {}
        cab = tarjeta(self)
        cab.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 10))
        etiqueta(cab, "Grados de pertenencia", 13, peso="bold").pack(anchor="w", padx=14, pady=(10, 2))
        for var in cfg.ENTRADAS:
            self.lbl_grados[var] = etiqueta(cab, "", 12, "tenue", anchor="w", justify="left")
            self.lbl_grados[var].pack(anchor="w", padx=14, pady=(0, 2))
        etiqueta(cab, "", 4).pack(pady=(0, 4))

        # --- matriz
        mat = tarjeta(self)
        mat.grid(row=1, column=0, sticky="ew", padx=4, pady=(0, 10))
        etiqueta(mat, "Matriz de reglas (desempeño × entrega)", 13, peso="bold").grid(
            row=0, column=0, columnspan=4, sticky="w", padx=14, pady=(10, 6))
        etiqueta(mat, "Desempeño \\ Entrega", 11, "tenue").grid(row=1, column=0, padx=14, pady=4, sticky="w")
        for j, e in enumerate(cfg.TERMINOS["entrega"]):
            mat.grid_columnconfigure(j + 1, weight=1, uniform="m")
            etiqueta(mat, ET[e], 12, "tenue").grid(row=1, column=j + 1, pady=4)
        self.celdas: dict[str, tuple[ctk.CTkFrame, ctk.CTkLabel]] = {}
        por_par = {(r.desempeno, r.entrega): r for r in REGLAS}
        for i, d in enumerate(cfg.TERMINOS["desempeno"]):
            etiqueta(mat, ET[d], 12, "tenue").grid(row=i + 2, column=0, padx=14, pady=3, sticky="w")
            for j, e in enumerate(cfg.TERMINOS["entrega"]):
                r = por_par[(d, e)]
                celda = ctk.CTkFrame(mat, fg_color="transparent", border_width=1,
                                     border_color=par("borde"), corner_radius=6, height=46)
                celda.grid(row=i + 2, column=j + 1, sticky="ew", padx=4, pady=3)
                celda.grid_propagate(False)
                lbl = etiqueta(celda, "", 12)
                lbl.place(relx=0.5, rely=0.5, anchor="center")
                self.celdas[r.id] = (celda, lbl)
        etiqueta(mat, "", 4).grid(row=5, column=0, pady=(0, 6))

        # --- lista de reglas
        lista = tarjeta(self)
        lista.grid(row=2, column=0, sticky="ew", padx=4, pady=(0, 4))
        lista.grid_columnconfigure(1, weight=1)
        etiqueta(lista, "Reglas, fuerza de disparo y justificación", 13, peso="bold").grid(
            row=0, column=0, columnspan=3, sticky="w", padx=14, pady=(10, 6))
        self.filas: dict[str, dict] = {}
        for k, r in enumerate(REGLAS):
            fila = 1 + 2 * k
            if k:
                separador(lista).grid(row=fila - 1, column=0, columnspan=3, sticky="ew", padx=14)
            marco = ctk.CTkFrame(lista, fg_color="transparent", corner_radius=6)
            marco.grid(row=fila, column=0, columnspan=3, sticky="ew", padx=8, pady=2)
            marco.grid_columnconfigure(1, weight=1)
            rid = etiqueta(marco, r.id, 12, peso="bold", width=34)
            rid.grid(row=0, column=0, sticky="nw", padx=(6, 6), pady=(6, 0))
            txt = ctk.CTkLabel(marco, text=r.texto, font=ctk.CTkFont(family="Consolas", size=12),
                               anchor="w", justify="left", text_color=par("texto"))
            txt.grid(row=0, column=1, sticky="w", pady=(6, 0))
            fuerza = etiqueta(marco, "", 12, width=90, anchor="e")
            fuerza.grid(row=0, column=2, sticky="ne", padx=(6, 10), pady=(6, 0))
            just = etiqueta(marco, r.justificacion, 11, "tenue", anchor="w", justify="left", wraplength=760)
            just.grid(row=1, column=1, columnspan=2, sticky="w", pady=(0, 6))
            self.filas[r.id] = {"marco": marco, "id": rid, "texto": txt, "fuerza": fuerza}

    def aplicar_tema(self, t: Tema) -> None:  # los colores (claro, oscuro) los cambia customtkinter
        pass

    def actualizar(self, r: ResultadoInferencia) -> None:
        for var in cfg.ENTRADAS:
            g = " · ".join(f"{ET[t]} {v:.2f}" for t, v in r.grados[var].items())
            valor = r.desempeno if var == "desempeno" else r.entrega
            self.lbl_grados[var].configure(text=f"{cfg.ETIQUETAS_VARIABLE[var]} = {valor:g}:   {g}")
        for regla in REGLAS:
            f = r.fuerzas[regla.id]
            activa = f > 0
            celda, lbl = self.celdas[regla.id]
            celda.configure(fg_color=par("resaltado") if activa else "transparent",
                            border_color=par("acento") if activa else par("borde"))
            lbl.configure(text=f"{ET[regla.beca]}" + (f"  ·  {f:.2f}" if activa else ""),
                          text_color=par("texto") if activa else par("tenue"))
            fila = self.filas[regla.id]
            fila["marco"].configure(fg_color=par("resaltado") if activa else "transparent")
            color = par("texto") if activa else par("tenue")
            fila["id"].configure(text_color=par("acento") if activa else color)
            fila["texto"].configure(text_color=color)
            fila["fuerza"].configure(text=f"fuerza {f:.2f}", text_color=par("acento") if activa else color)
