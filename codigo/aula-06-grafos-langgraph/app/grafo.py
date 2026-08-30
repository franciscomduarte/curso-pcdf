"""O motor de grafo mínimo.

Vocabulário:
  - NÓ      : uma etapa — uma função `no(estado) -> estado`
  - ARESTA  : uma transição possível de um nó para outro
      · estática     : sempre vai para o mesmo destino
      · condicional  : um roteador `fn(estado) -> nome_do_proximo` decide
  - START / END : nós sentinela (não executam nada)
  - CICLO   : uma aresta que volta para um nó já visitado — precisa de
              condição de saída E de uma trava de passos (a da Aula 4)

O LangGraph faz muito mais (estado tipado, merge de updates, execução
paralela de ramos, checkpointing), mas o núcleo é isto.
"""

from __future__ import annotations

from typing import Callable

from .estado import Estado

START = "__start__"
END = "__end__"

No = Callable[[Estado], Estado]
Roteador = Callable[[Estado], str]


class GrafoInvalido(Exception):
    pass


class Grafo:
    def __init__(self) -> None:
        self._nos: dict[str, No] = {}
        self._arestas: dict[str, str] = {}                 # origem -> destino fixo
        self._condicionais: dict[str, Roteador] = {}       # origem -> roteador
        self._entrada: str | None = None

    # -- construção -------------------------------------------------------
    def no(self, nome: str, funcao: No) -> "Grafo":
        if nome in (START, END):
            raise GrafoInvalido(f"'{nome}' é reservado")
        self._nos[nome] = funcao
        return self

    def aresta(self, origem: str, destino: str) -> "Grafo":
        if origem == START:
            self._entrada = destino
        else:
            self._arestas[origem] = destino
        return self

    def aresta_condicional(self, origem: str, roteador: Roteador) -> "Grafo":
        """O roteador devolve o nome do próximo nó, ou END."""
        self._condicionais[origem] = roteador
        return self

    # -- validação -------------------------------------------------------
    def validar(self) -> None:
        if self._entrada is None:
            raise GrafoInvalido("falta uma aresta a partir de START")
        for nome in self._nos:
            if nome not in self._arestas and nome not in self._condicionais:
                raise GrafoInvalido(f"nó '{nome}' não tem aresta de saída")
        alvos = set(self._arestas.values()) | {self._entrada}
        for alvo in alvos:
            if alvo not in self._nos and alvo != END:
                raise GrafoInvalido(f"aresta aponta para nó inexistente: '{alvo}'")

    def tem_ciclo(self) -> bool:
        """Detecta ciclo só nas arestas estáticas (as condicionais dependem do estado)."""
        visto, pilha = set(), set()

        def dfs(n: str) -> bool:
            if n == END or n not in self._arestas:
                return False
            visto.add(n); pilha.add(n)
            prox = self._arestas[n]
            if prox in pilha:
                return True
            if prox not in visto and dfs(prox):
                return True
            pilha.discard(n)
            return False

        return any(dfs(n) for n in self._nos if n not in visto)

    # -- execução -------------------------------------------------------
    def compilar(self, max_passos: int = 25) -> "GrafoCompilado":
        self.validar()
        return GrafoCompilado(self, max_passos)


class GrafoCompilado:
    def __init__(self, grafo: Grafo, max_passos: int) -> None:
        self._g = grafo
        self._max = max_passos

    def executar(self, estado: Estado) -> Estado:
        atual = self._g._entrada
        while atual != END:
            if estado.passos >= self._max:
                estado.pendencias.append(f"grafo interrompido: {self._max} passos (possível ciclo)")
                return estado
            funcao = self._g._nos[atual]
            estado.visitou(atual)
            estado = funcao(estado)
            if atual in self._g._condicionais:
                proximo = self._g._condicionais[atual](estado)
                if proximo != END and proximo not in self._g._nos:
                    raise GrafoInvalido(
                        f"roteador de '{atual}' devolveu nó inexistente: '{proximo}'"
                    )
                atual = proximo
            else:
                atual = self._g._arestas[atual]
        estado.caminho.append(END)
        return estado
