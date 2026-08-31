"""Guardrail de entrada — herdado sem mudança da Aula 9. O "portão" do
cluster: filtro de injeção de prompt (Aula 1) + limite de taxa por origem
(Aula 4/8), antes de qualquer Service."""

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
