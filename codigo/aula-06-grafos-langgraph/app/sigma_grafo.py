"""Monta o grafo de execução do SIGMA.

    START -> extrair -> classificar
    classificar --(confuso?)--> encaminhar_humano -> END
                --(senão)-----> consultar -> revisar
    revisar --(enriquecimento vazio e tentativas < 2?)--> consultar   (CICLO)
            --(senão)-----------------------------------> END
"""

from __future__ import annotations

from . import nos
from .grafo import END, START, Grafo


def construir() -> Grafo:
    g = Grafo()
    g.no("extrair", nos.extrair)
    g.no("classificar", nos.classificar)
    g.no("consultar", nos.consultar)
    g.no("revisar", nos.revisar)
    g.no("encaminhar_humano", nos.encaminhar_humano)

    g.aresta(START, "extrair")
    g.aresta("extrair", "classificar")
    g.aresta_condicional("classificar", nos.rota_pos_classificar)
    g.aresta("consultar", "revisar")
    g.aresta_condicional("revisar", nos.rota_pos_revisar)
    g.aresta("encaminhar_humano", END)
    return g
