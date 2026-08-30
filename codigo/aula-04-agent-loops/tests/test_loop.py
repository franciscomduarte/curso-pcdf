"""Testes do loop ReAct — rodam offline, só com pydantic."""

from __future__ import annotations

from app.ferramentas import REGISTRO
from app.llm import MockReAct
from app.loop import Autonomia, LoopReAct
from app.orcamento import MotivoParada, Orcamento

TAREFA = "Furto da motocicleta Honda CG placa ABC1D23 em Taguatinga."


def rodar(**kw):
    kw.setdefault("llm", MockReAct())
    kw.setdefault("autonomia", Autonomia.AUTONOMO)
    kw.setdefault("orcamento", Orcamento())
    return LoopReAct(**kw).executar(TAREFA)


def test_encerra_com_resposta_final_e_linha_do_tempo():
    t = rodar()
    assert t.motivo_parada is MotivoParada.RESPOSTA_FINAL
    assert "linha_do_tempo" in t.resposta_final


def test_reage_a_observacao_busca_documento_so_se_consta_alerta():
    # ABC1D23 consta alerta -> o passo buscar_documento aparece
    ferramentas_usadas = [p.ferramenta for p in rodar().passos if p.ferramenta]
    assert "buscar_documento" in ferramentas_usadas

    # XYZ9Z87 sem apontamentos -> não busca documento
    t2 = LoopReAct(llm=MockReAct(), autonomia=Autonomia.AUTONOMO, orcamento=Orcamento()) \
        .executar("Furto da moto placa XYZ9Z87 em Taguatinga.")
    assert "buscar_documento" not in [p.ferramenta for p in t2.passos if p.ferramenta]


class _NuncaEncerra:
    """Sempre pede ferramenta; varia os args para não cair na trava de repetição."""

    def __init__(self, ferramenta="buscar_documento"):
        self.ferramenta = ferramenta

    def pensar(self, tarefa, ferramentas, historico):
        return {"pensamento": "...", "acao": {"ferramenta": self.ferramenta,
                                              "args": {"assunto": f"tema-{len(historico)}"}}}


def test_limite_de_passos():
    t = rodar(llm=_NuncaEncerra(), orcamento=Orcamento(max_passos=3, max_chamadas=99, custo_max=999))
    assert t.motivo_parada is MotivoParada.LIMITE_PASSOS
    assert t.orcamento.passos == 3


def test_limite_de_custo():
    t = rodar(llm=_NuncaEncerra(), orcamento=Orcamento(max_passos=99, max_chamadas=99, custo_max=3))
    assert t.motivo_parada is MotivoParada.LIMITE_CUSTO


def test_acao_repetida_aborta():
    class Repete:
        def pensar(self, *a):
            return {"pensamento": "...", "acao": {"ferramenta": "consultar_veiculo", "args": {"placa": "ABC1D23"}}}

    t = rodar(llm=Repete(), orcamento=Orcamento(max_passos=99))
    assert t.motivo_parada is MotivoParada.ACAO_REPETIDA


def test_retry_recupera_servico_instavel():
    REGISTRO["servico_externo"].funcao.tentativas = 0  # reseta o contador do _Instavel

    class UsaExterno:
        def pensar(self, tarefa, ferramentas, historico):
            if not historico:
                return {"pensamento": "...", "acao": {"ferramenta": "servico_externo", "args": {"recurso": "R"}}}
            return {"pensamento": "ok", "resposta_final": str(historico[-1]["observacao"])}

    t = rodar(llm=UsaExterno())
    passo = next(p for p in t.passos if p.ferramenta == "servico_externo")
    assert passo.tentativas == 3 and "ok após retry" in passo.observacao


def test_autonomia_supervisionado_confirma_toda_acao():
    vistos = []
    LoopReAct(llm=MockReAct(), autonomia=Autonomia.SUPERVISIONADO,
              confirmar=lambda f, a: vistos.append(f) or True,
              orcamento=Orcamento()).executar(TAREFA)
    assert len(vistos) >= 2 and "consultar_ocorrencias_similares" in vistos


def test_autonomia_limitado_confirma_so_sensivel():
    vistos = []
    LoopReAct(llm=MockReAct(), autonomia=Autonomia.LIMITADO,
              confirmar=lambda f, a: vistos.append(f) or True,
              orcamento=Orcamento()).executar(TAREFA)
    assert vistos == ["consultar_veiculo"]   # a única sensível


def test_nao_confirmado_encerra():
    t = rodar(autonomia=Autonomia.SUPERVISIONADO, confirmar=lambda f, a: False)
    assert t.motivo_parada is MotivoParada.NAO_CONFIRMADO


def test_evento_de_encerramento_chega_ao_auditor():
    from app.barramento import Auditor, Barramento
    from solucao_exercicios import executar_e_publicar, orcamento_para

    assert orcamento_para("triagem rápida").max_passos == 3
    assert orcamento_para("investigação a fundo").max_passos == 8

    bus, aud = Barramento(), Auditor()
    bus.assinar("#", aud.ao_receber)
    executar_e_publicar("triagem rápida do furto placa ABC1D23 em Taguatinga", bus)
    assert len(aud.trilha) == 1
    assert aud.trilha[0].topico == "agente.encerrou"
    assert "motivo_parada" in aud.trilha[0].dados
