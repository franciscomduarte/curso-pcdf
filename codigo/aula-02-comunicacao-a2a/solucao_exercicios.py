"""Gabarito dos laboratórios da Aula 2.

    python solucao_exercicios.py
"""

from __future__ import annotations

from app.agentes import AgenteAuditor, AgenteClassificador, AgenteExtrator
from app.mensagem import EnvelopeA2A, Performativa
from app.ocorrencias import OCORRENCIAS_BRUTAS
from app.transporte import BarramentoLocal, ServicoLocal, ServicoNaoEncontrado


# ---------------------------------------------------------------------------
# LAB BÁSICO — um segundo assinante sem tocar no produtor
# ---------------------------------------------------------------------------
class AgentePainel:
    """Novo consumidor: conta prioridades. O Extrator não fica sabendo."""

    nome = "painel"

    def __init__(self) -> None:
        self.contagem: dict[str, int] = {}

    def ao_receber(self, env: EnvelopeA2A) -> None:
        p = env.conteudo.get("prioridade")
        if p:
            self.contagem[p] = self.contagem.get(p, 0) + 1


def lab_basico() -> None:
    print("== LAB BÁSICO: acrescentar um assinante ==")
    bus = BarramentoLocal()
    auditor, painel = AgenteAuditor(), AgentePainel()
    classificador = AgenteClassificador(bus)

    bus.assinar("#", auditor.ao_receber)
    bus.assinar("ocorrencia.extraida", classificador.ao_receber)
    bus.assinar("ocorrencia.classificada", painel.ao_receber)

    AgenteExtrator(OCORRENCIAS_BRUTAS).publicar_todas(bus)
    print("  painel:", painel.contagem)
    print("  trilha:", len(auditor.trilha), "envelopes")


# ---------------------------------------------------------------------------
# LAB INTERMEDIÁRIO — REFUSE quando o serviço não entende a ontologia
# ---------------------------------------------------------------------------
def lab_intermediario() -> None:
    print("\n== LAB INTERMEDIÁRIO: performativas na request/response ==")
    servico = ServicoLocal()
    classificador = AgenteClassificador(BarramentoLocal())

    def handler(env: EnvelopeA2A) -> EnvelopeA2A:
        if env.ontologia != "sigma/ocorrencia/v1":
            return env.resposta(classificador.nome, Performativa.REFUSE,
                                {"motivo": f"ontologia não suportada: {env.ontologia}"})
        return classificador.responder(env)

    servico.registrar("classificador", handler)

    ok = EnvelopeA2A.pedir("triagem", "classificar",
                           {"natureza": "Furto", "data_fato": "2026-08-15", "local": "Asa Norte"},
                           responder_a="r")
    ruim = ok.model_copy(update={"ontologia": "outro/v9"})
    print("  ", servico.chamar("classificador", ok).performativa.value)
    print("  ", servico.chamar("classificador", ruim).performativa.value)


# ---------------------------------------------------------------------------
# DESAFIO — acoplamento: serviço fora do ar
# ---------------------------------------------------------------------------
def desafio() -> None:
    print("\n== DESAFIO: request/response depende do serviço estar no ar ==")
    servico = ServicoLocal()  # nada registrado
    pedido = EnvelopeA2A.pedir("triagem", "classificar", {}, responder_a="r")
    try:
        servico.chamar("classificador", pedido)
    except ServicoNaoEncontrado as exc:
        print(f"  falhou como esperado: ServicoNaoEncontrado({exc})")
    print("  no pub/sub, o Extrator publicaria mesmo sem ninguém ouvindo (0 entregas).")


if __name__ == "__main__":
    lab_basico()
    lab_intermediario()
    desafio()
