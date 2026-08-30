"""Transportes: como o envelope viaja de um agente a outro.

    Transporte (Protocol)
      ├── BarramentoLocal   -> pub/sub em memória, síncrono, determinístico (aula)
      └── BarramentoMQTT    -> pub/sub sobre um broker MQTT (app/transporte_mqtt.py)

E, para o padrão Request/Response:

    ServicoLocal            -> registro de handlers; chamada síncrona com resposta

A ideia é a mesma da Aula 1: o agente conhece só a *interface*. Trocar o
barramento local pelo MQTT não muda uma linha dos agentes.
"""

from __future__ import annotations

import fnmatch
from collections import defaultdict
from typing import Callable, Protocol

from .mensagem import EnvelopeA2A, Performativa

Assinante = Callable[[EnvelopeA2A], None]


class Transporte(Protocol):
    def publicar(self, envelope: EnvelopeA2A) -> None: ...
    def assinar(self, filtro_topico: str, callback: Assinante) -> None: ...


# ---------------------------------------------------------------------------
# Pub/Sub em memória
# ---------------------------------------------------------------------------
class BarramentoLocal:
    """Entrega síncrona e ordenada. `filtro_topico` aceita curingas fnmatch:
    'ocorrencia.*' pega 'ocorrencia.extraida' e 'ocorrencia.classificada';
    '*' (ou '#') pega tudo."""

    def __init__(self) -> None:
        self._assinantes: list[tuple[str, Assinante]] = []
        self.entregues = 0

    def assinar(self, filtro_topico: str, callback: Assinante) -> None:
        if filtro_topico == "#":
            filtro_topico = "*"
        self._assinantes.append((filtro_topico, callback))

    def publicar(self, envelope: EnvelopeA2A) -> None:
        for filtro, callback in list(self._assinantes):
            if fnmatch.fnmatch(envelope.topico, filtro):
                self.entregues += 1
                callback(envelope)


# ---------------------------------------------------------------------------
# Request/Response
# ---------------------------------------------------------------------------
class ServicoNaoEncontrado(Exception):
    pass


class ServicoLocal:
    """Registro simples de serviços síncronos. Cada handler recebe um
    EnvelopeA2A (REQUEST) e devolve um EnvelopeA2A (a resposta)."""

    def __init__(self) -> None:
        self._handlers: dict[str, Callable[[EnvelopeA2A], EnvelopeA2A]] = {}

    def registrar(self, nome: str, handler: Callable[[EnvelopeA2A], EnvelopeA2A]) -> None:
        self._handlers[nome] = handler

    def chamar(self, nome: str, envelope: EnvelopeA2A) -> EnvelopeA2A:
        handler = self._handlers.get(nome)
        if handler is None:
            # acoplamento: o chamador precisa que o serviço exista e esteja no ar
            raise ServicoNaoEncontrado(nome)
        try:
            return handler(envelope)
        except Exception as exc:  # noqa: BLE001 — vira uma resposta FAILURE
            return envelope.resposta(
                remetente=nome,
                performativa=Performativa.FAILURE,
                conteudo={"erro": str(exc)},
            )
