"""Testes do fluxo do SIGMA + Gateway — checkpoint no store, guardrail na entrada."""

from __future__ import annotations

import pytest

from app.agentes import analista, consolidador, investigador, juridico
from app.bases_sinteticas import BOLETIM_SUSPEITO, OCORRENCIAS
from app.cluster import Cluster
from app.fluxo import Fluxo
from app.gateway import Gateway
from app.guardrail import EntradaRejeitada, Guardrail, TaxaExcedida
from app.memoria import Estado
from app.observabilidade import Metricas
from app.store import Concluido, DecisaoHumana, Pausado, StoreCompartilhado

TEXTO = OCORRENCIAS["PCDF-SIM-0002"]


def _cluster_sigma(metricas: Metricas | None = None) -> Cluster:
    c = Cluster(metricas=metricas or Metricas())
    c.criar_configmap("juridico-config", detalhe="padrao")
    c.criar_deployment("investigador-deploy", investigador, replicas=1)
    c.criar_deployment("analista-deploy", analista, replicas=1)
    c.criar_deployment("juridico-deploy", juridico, replicas=1, config_map="juridico-config")
    c.criar_deployment("consolidador-deploy", consolidador, replicas=1)
    c.criar_service("investigador-svc", "investigador-deploy")
    c.criar_service("analista-svc", "analista-deploy")
    c.criar_service("juridico-svc", "juridico-deploy")
    c.criar_service("consolidador-svc", "consolidador-deploy")
    return c


def test_fluxo_para_no_breakpoint(tmp_path):
    fluxo = Fluxo(_cluster_sigma(), StoreCompartilhado(tmp_path))
    r = fluxo.iniciar(Estado(id="PCDF-SIM-0002", texto=TEXTO))
    assert isinstance(r, Pausado)


def test_atendido_por_agora_e_lista_de_dicts_com_duracao(tmp_path):
    fluxo = Fluxo(_cluster_sigma(), StoreCompartilhado(tmp_path))
    r = fluxo.iniciar(Estado(id="PCDF-SIM-0002", texto=TEXTO))
    e = fluxo.store.carregar(r.checkpoint)
    assert [p["etapa"] for p in e.atendido_por] == ["investigar", "analisar", "juridico"]
    assert all("pod" in p and "duracao_ms" in p for p in e.atendido_por)
    assert all(p["duracao_ms"] >= 0.0 for p in e.atendido_por)


def test_aprovar_conclui(tmp_path):
    fluxo = Fluxo(_cluster_sigma(), StoreCompartilhado(tmp_path))
    r = fluxo.iniciar(Estado(id="PCDF-SIM-0002", texto=TEXTO))
    r2 = fluxo.retomar(r.checkpoint, DecisaoHumana(aprovado=True, operador="delegado"))
    assert isinstance(r2, Concluido)


def test_metricas_recebem_uma_chamada_por_servico(tmp_path):
    metricas = Metricas()
    fluxo = Fluxo(_cluster_sigma(metricas), StoreCompartilhado(tmp_path))
    fluxo.iniciar(Estado(id="PCDF-SIM-0002", texto=TEXTO))
    assert metricas.chamadas["investigador-svc"] == 1
    assert metricas.chamadas["analista-svc"] == 1
    assert metricas.chamadas["juridico-svc"] == 1
    assert "consolidador-svc" not in metricas.chamadas   # ainda não passou pelo breakpoint


# -- Gateway (guardrail + fluxo) -----------------------------------------

def test_gateway_processa_boletim_limpo(tmp_path):
    gw = Gateway(Fluxo(_cluster_sigma(), StoreCompartilhado(tmp_path)),
                Guardrail(limite_por_janela=10))
    r = gw.processar("PCDF-SIM-0002", TEXTO, origem="delegacia-01")
    assert isinstance(r, Pausado)


def test_gateway_barra_boletim_com_injecao(tmp_path):
    gw = Gateway(Fluxo(_cluster_sigma(), StoreCompartilhado(tmp_path)),
                Guardrail(limite_por_janela=10))
    with pytest.raises(EntradaRejeitada):
        gw.processar("PCDF-SIM-9999", BOLETIM_SUSPEITO, origem="delegacia-02")


def test_gateway_barra_apos_estourar_taxa(tmp_path):
    gw = Gateway(Fluxo(_cluster_sigma(), StoreCompartilhado(tmp_path)),
                Guardrail(limite_por_janela=1, janela_s=60.0))
    gw.processar("PCDF-SIM-0002", TEXTO, origem="delegacia-03")
    with pytest.raises(TaxaExcedida):
        gw.processar("PCDF-SIM-0009", OCORRENCIAS["PCDF-SIM-0009"], origem="delegacia-03")


def test_gateway_entrada_rejeitada_nao_consome_nenhuma_cota_de_processamento(tmp_path):
    """Uma entrada barrada pelo guardrail nem chega a criar checkpoint."""
    store = StoreCompartilhado(tmp_path)
    gw = Gateway(Fluxo(_cluster_sigma(), store), Guardrail(limite_por_janela=10))
    with pytest.raises(EntradaRejeitada):
        gw.processar("PCDF-SIM-9999", BOLETIM_SUSPEITO, origem="delegacia-02")
    assert list(tmp_path.glob("*.json")) == []
