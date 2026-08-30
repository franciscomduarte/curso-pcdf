"""ClienteMCP — o lado do agente.

Traduz chamadas de alto nível em ChamadaMCP e conversa com um ServidorMCP.
Poderia falar por stdio/HTTP com um servidor remoto — aqui é uma referência
direta ao objeto, para o laboratório rodar offline e determinístico.

Regras que o cliente aplica localmente:
  - ferramentas marcadas `sensivel` exigem um callback de confirmação humana;
  - o cliente só conhece as ferramentas que o servidor listou (descoberta).
"""

from __future__ import annotations

from typing import Callable

from .esquema import ChamadaMCP, FerramentaSpec, RespostaMCP
from .servidor_mcp import ServidorMCP

# callback de confirmação: recebe (nome, argumentos) e devolve True/False
Confirmador = Callable[[str, dict], bool]


def _auto_sim(_nome: str, _args: dict) -> bool:
    return True


class ClienteMCP:
    def __init__(self, servidor: ServidorMCP, nome: str = "agente-consultor",
                 confirmar: Confirmador = _auto_sim) -> None:
        self._servidor = servidor
        self.nome = nome
        self._confirmar = confirmar
        self._catalogo: dict[str, FerramentaSpec] = {}

    def conectar(self, redescobrir: bool = False) -> list[FerramentaSpec]:
        """Descobre as ferramentas disponíveis (handshake mínimo). Idempotente:
        se já conectou, devolve o catálogo em cache — chamar de novo não gera
        outra entrada na auditoria. Passe `redescobrir=True` para forçar."""
        if self._catalogo and not redescobrir:
            return list(self._catalogo.values())
        resp = self._servidor.atender(ChamadaMCP(metodo="listar_ferramentas", cliente=self.nome))
        self._catalogo = {
            e["nome"]: FerramentaSpec.model_validate(e) for e in (resp.resultado or [])
        }
        return list(self._catalogo.values())

    def ferramentas(self) -> list[str]:
        return sorted(self._catalogo)

    def chamar(self, nome: str, **argumentos) -> RespostaMCP:
        spec = self._catalogo.get(nome)
        if spec is None:
            return RespostaMCP.falha(
                f"'{nome}' não está no catálogo do servidor (rodou conectar()?)"
            )
        if spec.sensivel and not self._confirmar(nome, argumentos):
            return RespostaMCP.falha(f"chamada a '{nome}' não confirmada pelo operador")
        return self._servidor.atender(ChamadaMCP(
            metodo="chamar_ferramenta", ferramenta=nome,
            argumentos=argumentos, cliente=self.nome,
        ))

    def ler_recurso(self, uri: str) -> RespostaMCP:
        return self._servidor.atender(ChamadaMCP(metodo="ler_recurso", uri=uri, cliente=self.nome))
