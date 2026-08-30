"""BLACKBOARD — um quadro compartilhado; cada especialista contribui quando pode.

O `Dossie` é o quadro. A cada rodada, todo especialista cujas pré-condições
(`precisa`) estão no quadro e cuja contribuição (`produz`) ainda falta é
executado. Para quando uma rodada inteira não muda nada.

Vantagem: ordem emergente, fácil acrescentar especialista (é só declarar
`precisa`/`produz`). Desvantagem: difícil prever/depurar; sem um controlador,
dois especialistas podem escrever no mesmo campo.
"""

from __future__ import annotations

from ..especialistas import REGISTRO, Dossie
from ..metricas import Metricas


def orquestrar(d: Dossie, max_rodadas: int = 6) -> tuple[Dossie, Metricas]:
    m = Metricas(padrao="blackboard")
    for _ in range(max_rodadas):
        m.rodadas += 1
        mudou = False
        for nome in sorted(REGISTRO):                 # ordem estável -> determinístico
            spec = REGISTRO[nome]
            precondicoes_ok = all(d.tem(c) for c in spec.precisa)
            ja_contribuiu = d.tem(spec.produz)
            if precondicoes_ok and not ja_contribuiu:
                d = spec.funcao(d, m)
                mudou = True
        if not mudou:
            break
    return d, m
