"""Testes do núcleo A2A — rodam offline, só com pydantic."""

from __future__ import annotations

from app.agentes import AgenteAuditor, AgenteClassificador, AgenteExtrator
from app.mensagem import EnvelopeA2A, Performativa
from app.ocorrencias import OCORRENCIAS_BRUTAS, classificar, extrair
from app.transporte import BarramentoLocal, ServicoLocal, ServicoNaoEncontrado


def test_envelope_factory_preenche_metadados():
    env = EnvelopeA2A.informar("extrator", "ocorrencia.extraida", {"id": "X"})
    assert env.performativa is Performativa.INFORM
    assert env.conversa_id and env.enviado_em


def test_pubsub_extrator_nao_conhece_classificador():
    bus = BarramentoLocal()
    auditor = AgenteAuditor()
    classificador = AgenteClassificador(bus)
    classificadas: list[EnvelopeA2A] = []

    bus.assinar("#", auditor.ao_receber)
    bus.assinar("ocorrencia.extraida", classificador.ao_receber)
    bus.assinar("ocorrencia.classificada", classificadas.append)

    AgenteExtrator(OCORRENCIAS_BRUTAS).publicar_todas(bus)

    assert len(classificadas) == len(OCORRENCIAS_BRUTAS)
    # auditor viu extraidas + classificadas
    assert len(auditor.trilha) == 2 * len(OCORRENCIAS_BRUTAS)


def test_curinga_de_topico():
    bus = BarramentoLocal()
    vistos: list[str] = []
    bus.assinar("ocorrencia.*", lambda e: vistos.append(e.topico))
    bus.publicar(EnvelopeA2A.informar("a", "ocorrencia.extraida", {}))
    bus.publicar(EnvelopeA2A.informar("a", "ocorrencia.classificada", {}))
    bus.publicar(EnvelopeA2A.informar("a", "sistema.heartbeat", {}))
    assert vistos == ["ocorrencia.extraida", "ocorrencia.classificada"]


def test_roubo_vira_prioridade_alta_e_revisao():
    conteudo = {"id": "PCDF-SIM-0002", **extrair(OCORRENCIAS_BRUTAS[1]["texto"])}
    resultado = classificar(conteudo)
    assert resultado["prioridade"] == "alta"
    assert resultado["revisao_humana_obrigatoria"] is True


def test_request_response_confirma():
    servico = ServicoLocal()
    classificador = AgenteClassificador(BarramentoLocal())
    servico.registrar("classificador", classificador.responder)

    pedido = EnvelopeA2A.pedir("triagem", "classificar",
                               {"natureza": "Furto", "data_fato": "2026-08-15", "local": "Asa Norte"},
                               responder_a="r")
    resposta = servico.chamar("classificador", pedido)
    assert resposta.performativa is Performativa.CONFIRM
    assert resposta.conversa_id == pedido.conversa_id


def test_request_response_exige_servico_no_ar():
    servico = ServicoLocal()
    try:
        servico.chamar("classificador", EnvelopeA2A.pedir("t", "c", {}, responder_a="r"))
        assert False
    except ServicoNaoEncontrado:
        pass


def test_envelope_invalido_e_rejeitado_por_schema():
    import pydantic

    try:
        EnvelopeA2A(performativa="xpto", remetente="a", topico="t")
        assert False
    except pydantic.ValidationError:
        pass
