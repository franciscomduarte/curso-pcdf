"""O Gateway: guardrail + fluxo, num só ponto de entrada.

Quem chama o SIGMA não fala com o Fluxo diretamente — fala com o Gateway,
que aplica o guardrail primeiro. Separar assim (em vez de meter a checagem
dentro do `Fluxo`) mantém o Fluxo focado no HITL/persistência e o Gateway
focado em barrar entradas ruins — a mesma separação de responsabilidades
da Aula 7, agora entre "camada de borda" e "lógica de negócio".
"""

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
