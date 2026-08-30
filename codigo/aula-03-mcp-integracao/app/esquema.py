"""Contratos do protocolo MCP mínimo (inspirado em JSON-RPC 2.0).

O SDK oficial do MCP faz muito mais, mas a espinha é isto: um cliente pede
`listar_ferramentas` / `chamar_ferramenta` / `ler_recurso`, e o servidor
responde com `resultado` ou `erro`.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ParametroSpec(BaseModel):
    nome: str
    tipo: str = "string"
    descricao: str = ""
    obrigatorio: bool = True


class FerramentaSpec(BaseModel):
    """O que o cliente vê ao descobrir uma ferramenta (nome + contrato)."""

    nome: str
    descricao: str
    parametros: list[ParametroSpec] = Field(default_factory=list)
    sensivel: bool = Field(
        default=False,
        description="Se True, o cliente deve pedir confirmação humana antes de chamar.",
    )


class RecursoSpec(BaseModel):
    uri: str
    descricao: str


class ChamadaMCP(BaseModel):
    """Requisição do cliente para o servidor."""

    metodo: str  # "listar_ferramentas" | "chamar_ferramenta" | "listar_recursos" | "ler_recurso"
    ferramenta: str | None = None
    argumentos: dict[str, Any] = Field(default_factory=dict)
    uri: str | None = None
    cliente: str = "desconhecido"


class RespostaMCP(BaseModel):
    ok: bool
    resultado: Any = None
    erro: str | None = None

    @classmethod
    def sucesso(cls, resultado: Any) -> "RespostaMCP":
        return cls(ok=True, resultado=resultado)

    @classmethod
    def falha(cls, erro: str) -> "RespostaMCP":
        return cls(ok=False, erro=erro)


class RegistroAuditoria(BaseModel):
    quando: str
    cliente: str
    metodo: str
    ferramenta: str | None = None
    uri: str | None = None
    argumentos: dict[str, Any] = Field(default_factory=dict)
    permitido: bool = True
    resumo_resultado: str = ""
