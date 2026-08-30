"""DEBATE — vários agentes discordam e refinam a resposta em rodadas.

Não substitui os outros padrões: é uma TÉCNICA para uma sub-decisão ambígua
(aqui: "Furto ou Roubo?"). Dois debatedores dão opinião + razão + confiança,
leem o argumento um do outro, revisam; um juiz decide.

Custo alto: (nº debatedores × nº rodadas) chamadas de LLM + 1 do juiz. Use
só onde a ambiguidade justifica.
"""

from __future__ import annotations

from ..llm import LLMOrquestrador
from ..metricas import Metricas


def orquestrar(pergunta: str, contexto: str, llm: LLMOrquestrador,
               debatedores: int = 2, rodadas: int = 2) -> tuple[dict, Metricas]:
    m = Metricas(padrao="debate")
    opinioes: list[dict | None] = [None] * debatedores
    por_rodada: list[list[dict]] = []

    for r in range(1, rodadas + 1):
        m.rodadas += 1
        novas: list[dict] = []
        for i in range(debatedores):
            outra = opinioes[1 - i] if debatedores == 2 else None
            op = llm.opinar(pergunta, contexto, r, outra, quem=i)
            m.registrar(llm=1, custo=2, latencia_ms=300)
            novas.append(op)
        opinioes = novas
        por_rodada.append(novas)

    veredito = llm.julgar(pergunta, [o for o in opinioes if o])
    m.registrar(llm=1, custo=1, latencia_ms=200)
    return {"pergunta": pergunta, "opinioes": opinioes,
            "por_rodada": por_rodada, "veredito": veredito}, m
