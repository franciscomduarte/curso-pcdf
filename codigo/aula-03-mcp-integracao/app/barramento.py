"""Barramento mínimo — versão enxuta do da Aula 2, para fechar o circuito com o Auditor.

Na Aula 2 isto é `EnvelopeA2A` + `BarramentoLocal` completos. Aqui basta o
essencial: publicar eventos num tópico e um Auditor que registra tudo. Serve
para os exercícios que pedem "as consultas MCP chegam ao Auditor".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable


@dataclass
class Evento:
    topico: str
    remetente: str
    dados: dict
    em: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Barramento:
    def __init__(self) -> None:
        self._assinantes: list[tuple[str, Callable[[Evento], None]]] = []

    def assinar(self, filtro: str, callback: Callable[[Evento], None]) -> None:
        self._assinantes.append((filtro, callback))

    def publicar(self, topico: str, remetente: str, dados: dict) -> None:
        evento = Evento(topico=topico, remetente=remetente, dados=dados)
        for filtro, callback in self._assinantes:
            if filtro in ("#", "*") or filtro == topico or topico.startswith(filtro.rstrip("*")):
                callback(evento)


class Auditor:
    """Só acrescenta — trilha imutável (base da Aula 9)."""

    def __init__(self) -> None:
        self.trilha: list[Evento] = []

    def ao_receber(self, evento: Evento) -> None:
        self.trilha.append(evento)

    def resumo(self) -> str:
        return "\n".join(f"[{e.topico}] {e.remetente}: {e.dados}" for e in self.trilha)
