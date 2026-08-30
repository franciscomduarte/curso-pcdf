"""Orçamento e critérios de parada do loop.

Um agente sem trava roda para sempre (e gasta dinheiro). Aqui juntamos, num
lugar só, TODOS os limites que fazem o loop terminar:

  - passos          : quantas voltas do ciclo P-P-D-A-O
  - chamadas        : quantas execuções de ferramenta
  - custo           : soma dos `custo` das ferramentas usadas (imita $/tokens)
  - tempo           : relógio de parede, em segundos
  - repeticao       : mesma ação+args duas vezes seguidas -> aborta
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class MotivoParada(str, Enum):
    RESPOSTA_FINAL = "resposta_final"
    LIMITE_PASSOS = "limite_passos"
    LIMITE_CHAMADAS = "limite_chamadas"
    LIMITE_CUSTO = "limite_custo"
    LIMITE_TEMPO = "limite_tempo"
    ACAO_REPETIDA = "acao_repetida"
    NAO_CONFIRMADO = "acao_nao_confirmada"


@dataclass
class Orcamento:
    max_passos: int = 6
    max_chamadas: int = 8
    custo_max: int = 20
    tempo_max_s: float = 10.0

    passos: int = 0
    chamadas: int = 0
    custo: int = 0
    _inicio: float = field(default_factory=time.monotonic)

    def iniciar(self) -> None:
        self._inicio = time.monotonic()

    def excedido(self) -> MotivoParada | None:
        if self.passos >= self.max_passos:
            return MotivoParada.LIMITE_PASSOS
        if self.chamadas >= self.max_chamadas:
            return MotivoParada.LIMITE_CHAMADAS
        if self.custo >= self.custo_max:
            return MotivoParada.LIMITE_CUSTO
        if time.monotonic() - self._inicio >= self.tempo_max_s:
            return MotivoParada.LIMITE_TEMPO
        return None

    def resumo(self) -> str:
        return (f"passos={self.passos}/{self.max_passos} "
                f"chamadas={self.chamadas}/{self.max_chamadas} "
                f"custo={self.custo}/{self.custo_max}")
