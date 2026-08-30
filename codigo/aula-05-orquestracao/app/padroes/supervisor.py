"""SUPERVISOR — um agente decide, a cada passo, qual especialista chamar.

É o loop ReAct da Aula 4, onde as "ferramentas" são os especialistas. Adapta:
pode pular o consultor numa ocorrência trivial. Custo: +1 chamada de LLM por
decisão. Ponto único de decisão -> ponto único de falha.
"""

from __future__ import annotations

from ..especialistas import REGISTRO, Dossie
from ..llm import LLMOrquestrador
from ..metricas import Metricas


def orquestrar(d: Dossie, llm: LLMOrquestrador, max_rodadas: int = 8) -> tuple[Dossie, Metricas]:
    m = Metricas(padrao="supervisor")
    for _ in range(max_rodadas):
        m.rodadas += 1
        proximo = llm.decidir(d)
        m.registrar(llm=1, custo=1, latencia_ms=150)   # a decisão do supervisor
        if proximo == "concluir":
            break
        spec = REGISTRO.get(proximo)
        if spec is None:
            d.pendencias.append(f"supervisor pediu especialista inexistente: {proximo}")
            break
        d = spec.funcao(d, m)
    return d, m
