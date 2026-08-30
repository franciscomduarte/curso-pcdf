"""Testes do fluxo HITL — rodam offline, só com a stdlib.

Usam um diretório de checkpoints temporário para não sujar saida/.
"""

from __future__ import annotations

import pytest

from app import hitl
from app.bases_sinteticas import OCORRENCIAS
from app.hitl import Checkpoint, Concluido, DecisaoHumana, Fluxo, Pausado
from app.memoria import Estado, Memoria


@pytest.fixture(autouse=True)
def _saida_tmp(tmp_path, monkeypatch):
    monkeypatch.setattr(hitl, "SAIDA", tmp_path)


def novo(oc_id="PCDF-SIM-0002"):
    return Estado(id=oc_id, texto=OCORRENCIAS[oc_id])


def test_o_fluxo_para_no_breakpoint_antes_de_consolidar():
    r = Fluxo().iniciar(novo())
    assert isinstance(r, Pausado)
    assert r.proposta["requer_decisao_humana"] is True
    assert "aprovar" in r.pergunta.lower()


def test_aprovacao_conclui_e_registra_a_decisao():
    f = Fluxo()
    r = f.iniciar(novo())
    r = f.retomar(r.checkpoint, DecisaoHumana(aprovado=True, operador="escrivão"))
    assert isinstance(r, Concluido)
    d = r.estado.dossie
    assert d["tipificacao"]["natureza"] == "Roubo"
    assert d["decisoes_humanas"][0]["operador"] == "escrivão"
    assert d["decisoes_humanas"][0]["aprovado"] is True


def test_consolidador_nunca_roda_sem_aprovacao():
    # o Estado não chega em 'consolidar' sem passar pelo breakpoint
    r = Fluxo().iniciar(novo())
    assert isinstance(r, Pausado)               # parou antes
    assert r.__dict__.get("estado") is None      # não devolveu Estado consolidado


def test_rejeicao_com_nota_volta_ao_juridico_e_pausa_de_novo():
    f = Fluxo()
    r = f.iniciar(novo())
    r2 = f.retomar(r.checkpoint, DecisaoHumana(aprovado=False, nota="sem arma, revejam"))
    assert isinstance(r2, Pausado)
    # o Jurídico considerou a nota
    assert r2.proposta["considerou_nota_do_operador"] == "sem arma, revejam"


def test_correcao_humana_da_tipificacao_prevalece():
    f = Fluxo()
    r = f.iniciar(novo())
    r = f.retomar(r.checkpoint, DecisaoHumana(
        aprovado=False,
        tipificacao_corrigida={"artigo": "Art. 155 do CP (furto)", "natureza": "Furto"},
        nota="furto por ora"))
    assert isinstance(r, Concluido)
    assert r.estado.dossie["tipificacao"]["natureza"] == "Furto"
    assert r.estado.dossie["tipificacao"]["origem"] == "correção humana"


def test_rejeicoes_repetidas_esbarram_no_limite():
    f = Fluxo(max_ciclos_hitl=2)
    r = f.iniciar(novo())
    r = f.retomar(r.checkpoint, DecisaoHumana(aprovado=False, nota="1"))
    r = f.retomar(r.checkpoint, DecisaoHumana(aprovado=False, nota="2"))
    assert isinstance(r, Concluido)
    assert r.estado.dossie["tipificacao"]["artigo"] == "PENDENTE"


def test_checkpoint_sobrevive_carrega_de_novo_com_a_memoria():
    f = Fluxo()
    r = f.iniciar(novo())
    e = Checkpoint.carregar(r.checkpoint)
    assert e.etapa == "aguardando_aprovacao"
    assert e.fatos and e.hipotese and e.tipificacao_proposta
    assert e.memorias["investigador"]["notas"]      # a memória do agente foi junto
    # retomar a partir do que veio do disco
    r = f.retomar(r.checkpoint, DecisaoHumana(aprovado=True))
    assert isinstance(r, Concluido)


def test_separacao_de_responsabilidades_cada_agente_uma_chave():
    from app import agentes
    e = novo()
    e = agentes.investigador(e)
    assert e.fatos and e.hipotese is None and e.tipificacao_proposta is None
    e.etapa = "analisar"; e = agentes.analista(e)
    assert e.hipotese and e.tipificacao_proposta is None


def test_memoria_e_append_only():
    m = Memoria(dono="x")
    m.anotar("a"); m.anotar("b")
    assert len(m.notas) == 2 and m.notas[0].endswith("a")
