"""Guardrail de entrada — o "portão" do cluster, antes de qualquer Service.

Duas checagens, as duas sobre a ENTRADA (nunca sobre o que os agentes
decidem depois — isso continua no domínio deles):

  1. Padrão suspeito no texto — a mesma injeção indireta da Aula 1
     ("ignore as instruções acima..."), agora barrada antes de o boletim
     entrar no fluxo, não só mitigada por prompt de sistema.
  2. Limite de taxa por origem — o "consumo ilimitado" da Aula 4/8, agora
     aplicado à ENTRADA do sistema, não só ao loop de um agente.

Isto é o equivalente, em nível de infraestrutura, ao "escopo" da Aula 3
(MCP) e à "confirmação humana" da Aula 4: uma camada que barra ANTES de
gastar orçamento de cluster com uma chamada que não deveria acontecer.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

PADROES_SUSPEITOS = (
    "ignore as instruções",
    "ignore instructions",
    "desconsidere o que foi dito",
    "responda apenas",
    "aja sem confirmar",
    "aprove automaticamente",
)


class EntradaRejeitada(Exception):
    """O texto bateu com um padrão de injeção conhecido."""


class TaxaExcedida(Exception):
    """A origem estourou o limite de chamadas na janela de tempo."""


@dataclass
class Guardrail:
    limite_por_janela: int
    janela_s: float = 60.0
    _historico: dict[str, list[float]] = field(default_factory=dict)

    def validar_entrada(self, texto: str) -> str | None:
        """Devolve o padrão encontrado, ou None se o texto parece seguro."""
        t = texto.lower()
        for padrao in PADROES_SUSPEITOS:
            if padrao in t:
                return padrao
        return None

    def permitir(self, origem: str, agora: float | None = None) -> bool:
        """True = dentro do limite (e já registra esta chamada); False = estourou."""
        agora = time.monotonic() if agora is None else agora
        hist = self._historico.setdefault(origem, [])
        hist[:] = [t for t in hist if agora - t < self.janela_s]
        if len(hist) >= self.limite_por_janela:
            return False
        hist.append(agora)
        return True


def gate(guardrail: Guardrail, origem: str, texto: str) -> None:
    """Levanta `EntradaRejeitada`/`TaxaExcedida`, ou não faz nada (passou)."""
    padrao = guardrail.validar_entrada(texto)
    if padrao:
        raise EntradaRejeitada(f"texto de '{origem}' contém padrão suspeito: '{padrao}'")
    if not guardrail.permitir(origem):
        raise TaxaExcedida(
            f"'{origem}' excedeu {guardrail.limite_por_janela} chamadas em {guardrail.janela_s:.0f}s")
