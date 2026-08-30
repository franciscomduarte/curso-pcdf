"""Contadores para comparar os padrões na mesma base.

`latencia_ms` é SIMULADA: cada especialista/chamada declara uma latência e o
padrão soma. Padrões que poderiam rodar em paralelo (blackboard, debate) somam
igual aqui — o código é single-thread — mas a aula aponta onde o paralelismo
economizaria tempo real.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Metricas:
    padrao: str
    especialistas: int = 0      # execuções de agente especialista
    llm: int = 0                # chamadas ao LLM (decisão/opinião)
    ferramentas: int = 0        # chamadas a ferramenta externa
    custo: int = 0              # soma dos custos (imita $/tokens)
    rodadas: int = 0            # voltas em padrões iterativos
    latencia_ms: int = 0

    def registrar(self, *, especialista=False, llm=0, ferramentas=0,
                  custo=0, latencia_ms=0) -> None:
        self.especialistas += int(especialista)
        self.llm += llm
        self.ferramentas += ferramentas
        self.custo += custo
        self.latencia_ms += latencia_ms

    def linha(self) -> str:
        return (f"{self.padrao:<12} esp={self.especialistas:<2} llm={self.llm:<2} "
                f"tools={self.ferramentas:<2} custo={self.custo:<3} "
                f"rodadas={self.rodadas:<2} latencia~{self.latencia_ms}ms")
