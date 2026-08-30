"""Os três agentes da Aula 2.

  AgenteExtrator      publica 'ocorrencia.extraida'          (INFORM)
  AgenteClassificador assina  'ocorrencia.extraida'          -> publica 'ocorrencia.classificada'
                      e também responde a REQUEST síncrono   (Request/Response)
  AgenteAuditor       assina  tudo ('#')                     -> trilha imutável

Repare: o Extrator não sabe que o Classificador existe. O Auditor foi
acrescentado sem tocar em ninguém. Isso é o desacoplamento do pub/sub.
"""

from __future__ import annotations

import logging

from .mensagem import EnvelopeA2A, Performativa
from .ocorrencias import classificar, extrair
from .transporte import BarramentoLocal

logger = logging.getLogger("sigma.a2a")


class AgenteExtrator:
    nome = "extrator"

    def __init__(self, ocorrencias: list[dict[str, str]]) -> None:
        self._ocorrencias = ocorrencias

    def publicar_todas(self, barramento: BarramentoLocal) -> None:
        for item in self._ocorrencias:
            conteudo = {"id": item["id"], **extrair(item["texto"])}
            env = EnvelopeA2A.informar(
                remetente=self.nome, topico="ocorrencia.extraida", conteudo=conteudo
            )
            logger.info("publica %s (%s)", item["id"], conteudo["natureza"])
            barramento.publicar(env)


class AgenteClassificador:
    nome = "classificador"

    def __init__(self, barramento: BarramentoLocal) -> None:
        self._barramento = barramento

    # --- caminho assíncrono (pub/sub) ---
    def ao_receber(self, env: EnvelopeA2A) -> None:
        if env.performativa is not Performativa.INFORM:
            return
        resultado = classificar(env.conteudo)
        saida = EnvelopeA2A(
            performativa=Performativa.INFORM,
            remetente=self.nome,
            topico="ocorrencia.classificada",
            conversa_id=env.conversa_id,
            conteudo={"id": env.conteudo.get("id"), **resultado},
        )
        logger.info("classifica %s -> %s", env.conteudo.get("id"), resultado["prioridade"])
        self._barramento.publicar(saida)

    # --- caminho síncrono (request/response) ---
    def responder(self, env: EnvelopeA2A) -> EnvelopeA2A:
        if env.performativa is not Performativa.REQUEST:
            return env.resposta(self.nome, Performativa.NOT_UNDERSTOOD, {})
        resultado = classificar(env.conteudo)
        return env.resposta(self.nome, Performativa.CONFIRM, resultado)


class AgenteAuditor:
    nome = "auditor"

    def __init__(self) -> None:
        self.trilha: list[EnvelopeA2A] = []

    def ao_receber(self, env: EnvelopeA2A) -> None:
        # trilha imutável: só acrescenta, nunca altera (base para a Aula 9)
        self.trilha.append(env)

    def imprimir_trilha(self) -> str:
        linhas = [f"{i:>2}. {e.resumo()}  [{e.conteudo.get('id', '-')}]"
                  for i, e in enumerate(self.trilha, 1)]
        return "\n".join(linhas)
