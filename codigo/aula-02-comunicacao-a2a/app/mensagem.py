"""O contrato da mensagem A2A.

Inspirado na FIPA-ACL (Agent Communication Language): o que dá sentido a uma
mensagem entre agentes não é só o payload, é a *intenção* — a performativa.
"inform" (estou te contando um fato) é diferente de "request" (faça isto) e de
"refuse" (não vou fazer).

Aqui usamos um subconjunto pragmático, transportado como JSON. O mesmo envelope
serve para o barramento em memória, para o MQTT e (com tradução) para o gRPC.

Referência: FIPA ACL Message Structure Specification (SC00061) e
FIPA Communicative Act Library (SC00037) — ver Referências da aula.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class Performativa(str, Enum):
    """Subconjunto das performativas FIPA-ACL usado no SIGMA."""

    INFORM = "inform"            # comunico um fato
    REQUEST = "request"          # peço uma ação
    QUERY_REF = "query-ref"      # pergunto o valor de algo
    AGREE = "agree"              # aceito executar
    REFUSE = "refuse"            # recuso executar
    FAILURE = "failure"          # tentei e falhei
    CONFIRM = "confirm"          # confirmo (resposta a query)
    NOT_UNDERSTOOD = "not-understood"


class EnvelopeA2A(BaseModel):
    """Envelope padrão. `conteudo` é validado pelo agente que recebe."""

    performativa: Performativa
    remetente: str
    destinatario: str | None = Field(
        default=None, description="None = mensagem de tópico (qualquer assinante)."
    )
    topico: str = Field(description="Ex.: 'ocorrencia.extraida', 'classificar'.")
    conversa_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    responder_a: str | None = Field(
        default=None, description="Tópico onde a resposta deve ser publicada."
    )
    ontologia: str = "sigma/ocorrencia/v1"
    conteudo: dict = Field(default_factory=dict)
    enviado_em: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @classmethod
    def informar(cls, remetente: str, topico: str, conteudo: dict, **kw) -> "EnvelopeA2A":
        return cls(performativa=Performativa.INFORM, remetente=remetente,
                   topico=topico, conteudo=conteudo, **kw)

    @classmethod
    def pedir(cls, remetente: str, topico: str, conteudo: dict,
              responder_a: str, **kw) -> "EnvelopeA2A":
        return cls(performativa=Performativa.REQUEST, remetente=remetente,
                   topico=topico, conteudo=conteudo, responder_a=responder_a, **kw)

    def resposta(self, remetente: str, performativa: Performativa,
                 conteudo: dict) -> "EnvelopeA2A":
        """Cria a resposta desta mensagem, mantendo a conversa."""
        return EnvelopeA2A(
            performativa=performativa,
            remetente=remetente,
            destinatario=self.remetente,
            topico=self.responder_a or f"{self.topico}.resposta",
            conversa_id=self.conversa_id,
            ontologia=self.ontologia,
            conteudo=conteudo,
        )

    def resumo(self) -> str:
        alvo = self.destinatario or f"#{self.topico}"
        return f"{self.remetente} --{self.performativa.value}--> {alvo}"
