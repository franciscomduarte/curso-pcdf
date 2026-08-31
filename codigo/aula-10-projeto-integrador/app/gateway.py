"""O Gateway — herdado sem mudança da Aula 9: guardrail + fluxo, num só
ponto de entrada. Quem chama o SIGMA fala com o Gateway, nunca direto com
o Fluxo ou com um Service."""

from __future__ import annotations

from .fluxo import Fluxo
from .guardrail import Guardrail, gate
from .memoria import Estado


class Gateway:
    def __init__(self, fluxo: Fluxo, guardrail: Guardrail) -> None:
        self.fluxo = fluxo
        self.guardrail = guardrail

    def processar(self, oc_id: str, texto: str, origem: str = "desconhecida"):
        gate(self.guardrail, origem, texto)   # EntradaRejeitada / TaxaExcedida se barrar
        return self.fluxo.iniciar(Estado(id=oc_id, texto=texto))
