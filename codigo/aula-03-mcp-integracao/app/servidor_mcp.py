"""ServidorMCP — expõe ferramentas e recursos, com escopo e auditoria.

Versão mínima e didática. O SDK oficial acrescenta transporte (stdio/HTTP),
negociação de capacidades, prompts, notificações... mas o núcleo é este:

  - listar_ferramentas()  -> o cliente descobre o que existe
  - chamar_ferramenta()   -> o servidor valida escopo, executa, registra
  - listar_recursos() / ler_recurso(uri)

O cliente NUNCA acessa as bases direto. Todo acesso passa por aqui e é logado.
"""

from __future__ import annotations

from datetime import datetime, timezone

from .bases_sinteticas import POLITICA_DE_USO
from .esquema import ChamadaMCP, RecursoSpec, RegistroAuditoria, RespostaMCP
from .ferramentas import ESPECIFICACOES, IMPLEMENTACOES

RECURSOS: dict[str, tuple[RecursoSpec, str]] = {
    "sigma://politica-de-uso": (
        RecursoSpec(uri="sigma://politica-de-uso", descricao="Regras de uso do servidor."),
        POLITICA_DE_USO,
    ),
    "sigma://bases/disponiveis": (
        RecursoSpec(uri="sigma://bases/disponiveis", descricao="Bases fictícias expostas."),
        "veiculos (fictícia) · ocorrencias_historico (fictícia) · documentos (fictícios)",
    ),
}


class ServidorMCP:
    def __init__(self, nome: str = "sigma-mcp", escopo: set[str] | None = None,
                 barramento=None) -> None:
        self.nome = nome
        # escopo = conjunto de ferramentas permitidas; None = todas
        self.escopo = escopo if escopo is not None else set(ESPECIFICACOES)
        self.auditoria: list[RegistroAuditoria] = []
        # opcional: publica cada RegistroAuditoria no barramento (Aula 2/lab)
        self._barramento = barramento

    # -- API do protocolo ---------------------------------------------------
    def atender(self, chamada: ChamadaMCP) -> RespostaMCP:
        despacho = {
            "listar_ferramentas": self._listar_ferramentas,
            "chamar_ferramenta": self._chamar_ferramenta,
            "listar_recursos": self._listar_recursos,
            "ler_recurso": self._ler_recurso,
        }.get(chamada.metodo)
        if despacho is None:
            return RespostaMCP.falha(f"método desconhecido: {chamada.metodo}")
        return despacho(chamada)

    # -- handlers ---------------------------------------------------------
    def _listar_ferramentas(self, chamada: ChamadaMCP) -> RespostaMCP:
        visiveis = [ESPECIFICACOES[n].model_dump() for n in sorted(self.escopo) if n in ESPECIFICACOES]
        self._registrar(chamada, permitido=True, resumo=f"{len(visiveis)} ferramentas")
        return RespostaMCP.sucesso(visiveis)

    def _chamar_ferramenta(self, chamada: ChamadaMCP) -> RespostaMCP:
        nome = chamada.ferramenta or ""
        if nome not in ESPECIFICACOES:
            self._registrar(chamada, permitido=False, resumo="ferramenta inexistente")
            return RespostaMCP.falha(f"ferramenta inexistente: {nome}")
        if nome not in self.escopo:
            self._registrar(chamada, permitido=False, resumo="fora do escopo")
            return RespostaMCP.falha(f"acesso negado: '{nome}' fora do escopo autorizado")
        try:
            resultado = IMPLEMENTACOES[nome](**chamada.argumentos)
        except TypeError as exc:
            self._registrar(chamada, permitido=True, resumo=f"erro de argumentos: {exc}")
            return RespostaMCP.falha(f"argumentos inválidos para {nome}: {exc}")
        self._registrar(chamada, permitido=True, resumo=_resumir(resultado))
        return RespostaMCP.sucesso(resultado)

    def _listar_recursos(self, chamada: ChamadaMCP) -> RespostaMCP:
        self._registrar(chamada, permitido=True, resumo=f"{len(RECURSOS)} recursos")
        return RespostaMCP.sucesso([spec.model_dump() for spec, _ in RECURSOS.values()])

    def _ler_recurso(self, chamada: ChamadaMCP) -> RespostaMCP:
        item = RECURSOS.get(chamada.uri or "")
        if not item:
            self._registrar(chamada, permitido=False, resumo="uri desconhecida")
            return RespostaMCP.falha(f"recurso não encontrado: {chamada.uri}")
        self._registrar(chamada, permitido=True, resumo="lido")
        return RespostaMCP.sucesso(item[1])

    # -- auditoria ------------------------------------------------------
    def _registrar(self, chamada: ChamadaMCP, permitido: bool, resumo: str) -> None:
        registro = RegistroAuditoria(
            quando=datetime.now(timezone.utc).isoformat(),
            cliente=chamada.cliente, metodo=chamada.metodo, ferramenta=chamada.ferramenta,
            uri=chamada.uri, argumentos=chamada.argumentos,
            permitido=permitido, resumo_resultado=resumo,
        )
        self.auditoria.append(registro)
        if self._barramento is not None:
            # permitido OU negado — a tentativa é o sinal
            self._barramento.publicar("ferramenta.invocada", self.nome, registro.model_dump())

    def trilha(self) -> str:
        linhas = []
        for r in self.auditoria:
            marca = "ok " if r.permitido else "NEG"
            alvo = r.ferramenta or r.uri or "-"
            linhas.append(f"[{marca}] {r.cliente} {r.metodo} {alvo} :: {r.resumo_resultado}")
        return "\n".join(linhas)


def _resumir(resultado) -> str:
    if isinstance(resultado, list):
        return f"{len(resultado)} item(ns)"
    if isinstance(resultado, dict):
        return "encontrado" if resultado.get("encontrado", True) else "não encontrado"
    return str(resultado)[:60]
