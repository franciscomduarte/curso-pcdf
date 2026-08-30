"""AgenteConsultor — o loop que usa o MCP.

Dada uma ocorrência nova (texto), o agente:
  1. conecta ao servidor MCP e descobre as ferramentas;
  2. pergunta ao LLM o próximo passo;
  3. se for uma chamada de ferramenta, executa via ClienteMCP e guarda a observação;
  4. repete até o LLM encerrar ou bater o limite de passos (trava anti-loop da Aula 1).

O agente não conhece as bases; conhece só o cliente MCP.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from .cliente_mcp import ClienteMCP
from .llm import LLMConsultor

logger = logging.getLogger("sigma.mcp")


@dataclass
class ResultadoConsulta:
    enriquecimento: str
    observacoes: list[str] = field(default_factory=list)
    passos: int = 0


@dataclass
class AgenteConsultor:
    cliente: ClienteMCP
    llm: LLMConsultor
    max_passos: int = 5

    def enriquecer(self, ocorrencia_texto: str) -> ResultadoConsulta:
        specs = self.cliente.conectar()
        logger.info("ferramentas disponíveis: %s", [s.nome for s in specs])
        observacoes: list[str] = []

        for passo in range(1, self.max_passos + 1):
            decisao = self.llm.proximo_passo(ocorrencia_texto, specs, observacoes)
            if "resposta_final" in decisao:
                return ResultadoConsulta(decisao["resposta_final"], observacoes, passo - 1)

            nome = decisao["ferramenta"]
            args = decisao.get("argumentos", {})
            logger.info("passo %d: chamar %s(%s)", passo, nome, args)
            resp = self.cliente.chamar(nome, **args)
            if resp.ok:
                observacoes.append(f"{nome}({args}) -> {resp.resultado}")
            else:
                observacoes.append(f"{nome} FALHOU: {resp.erro}")

        return ResultadoConsulta(
            "Limite de passos atingido — entregar o que há para revisão humana.",
            observacoes, self.max_passos,
        )
