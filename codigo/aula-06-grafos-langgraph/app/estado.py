"""O estado compartilhado — o objeto que trafega por todos os nós do grafo.

É o `Dossie` da Aula 5, com dois campos a mais para o grafo se enxergar:
`caminho` (a sequência de nós visitados) e `passos` (a trava anti-loop da Aula 4).
Cada nó recebe o estado, faz a sua parte, devolve o estado.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Estado:
    id: str
    texto: str
    campos: dict | None = None
    classificacao: dict | None = None
    enriquecimento: list | None = None
    pendencias: list[str] = field(default_factory=list)
    revisado: bool = False
    tentativas_enriquecer: int = 0

    # instrumentação do grafo
    caminho: list[str] = field(default_factory=list)
    passos: int = 0

    def visitou(self, no: str) -> None:
        self.caminho.append(no)
        self.passos += 1

    def tem(self, campo: str) -> bool:
        return getattr(self, campo, None) not in (None, [], False)
