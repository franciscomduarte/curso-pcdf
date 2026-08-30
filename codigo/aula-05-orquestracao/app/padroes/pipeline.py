"""PIPELINE — saída de um especialista é entrada do próximo, ordem fixa.

    extrator -> classificador -> consultor -> revisor

Vantagem: simples, previsível, fácil de depurar. Desvantagem: não adapta —
roda o consultor mesmo quando a ocorrência é trivial; se um passo falha, o
resto herda o buraco.
"""

from __future__ import annotations

from ..especialistas import ORDEM_PIPELINE, REGISTRO, Dossie
from ..metricas import Metricas


def orquestrar(d: Dossie) -> tuple[Dossie, Metricas]:
    m = Metricas(padrao="pipeline")
    for nome in ORDEM_PIPELINE:
        d = REGISTRO[nome].funcao(d, m)
        m.rodadas += 1
    return d, m
