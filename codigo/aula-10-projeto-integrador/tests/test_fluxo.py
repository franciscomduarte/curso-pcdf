"""Testes do fluxo do SIGMA completo — roteamento condicional + Gateway."""

from __future__ import annotations

import pytest

from app.agentes import analista, consolidador, investigador, juridico, revisor_dupla
from app.bases_sinteticas import BOLETIM_SUSPEITO, OCORRENCIAS
from app.cluster import Cluster
from app.fluxo import Fluxo
from app.gateway import Gateway
from app.guardrail import EntradaRejeitada, Guardrail, TaxaExcedida
from app.memoria import Estado
from app.observabilidade import Metricas
from app.store import Concluido, DecisaoHumana, Pausado, StoreCompartilhado

ROUBO = OCORRENCIAS["PCDF-SIM-0002"]     # grave ameaça -> roteado para revisão dupla
FURTO = OCORRENCIAS["PCDF-SIM-0009"]     # sem grave ameaça -> direto ao breakpoint


def _cluster_sigma(metricas: Metricas | None = None) -> Cluster:
    c = Cluster(metricas=metricas or Metricas())
    c.criar_configmap("juridico-config", detalhe="padrao")
    c.criar_deployment("investigador-deploy", investigador, replicas=1)
    c.criar_deployment("analista-deploy", analista, replicas=1)
    c.criar_deployment("juridico-deploy", juridico, replicas=1, config_map="juridico-config")
    c.criar_deployment("revisor-deploy", revisor_dupla, replicas=1)
    c.criar_deployment("consolidador-deploy", consolidador, replicas=1)
    for base in ("investigador", "analista", "juridico", "revisor", "consolidador"):
        c.criar_service(f"{base}-svc", f"{base}-deploy")
    return c


def test_roubo_passa_pela_revisao_dupla(tmp_path):
    fluxo = Fluxo(_cluster_sigma(), StoreCompartilhado(tmp_path))
    r = fluxo.iniciar(Estado(id="PCDF-SIM-0002", texto=ROUBO))
    e = fluxo.store.carregar(r.checkpoint)
    assert [p["etapa"] for p in e.atendido_por] == ["investigar", "analisar", "juridico", "revisar"]
    assert e.revisao is not None
    assert e.revisao["concorda"] is True


def test_furto_vai_direto_sem_revisao(tmp_path):
    fluxo = Fluxo(_cluster_sigma(), StoreCompartilhado(tmp_path))
    r = fluxo.iniciar(Estado(id="PCDF-SIM-0009", texto=FURTO))
    e = fluxo.store.carregar(r.checkpoint)
    assert [p["etapa"] for p in e.atendido_por] == ["investigar", "analisar", "juridico"]
    assert e.revisao is None


def test_aprovar_conclui_e_dossie_carrega_a_revisao(tmp_path):
    fluxo = Fluxo(_cluster_sigma(), StoreCompartilhado(tmp_path))
    r = fluxo.iniciar(Estado(id="PCDF-SIM-0002", texto=ROUBO))
    r2 = fluxo.retomar(r.checkpoint, DecisaoHumana(aprovado=True, operador="delegado"))
    assert isinstance(r2, Concluido)
    assert r2.estado.dossie["revisao_dupla"] is not None


def test_metricas_registram_chamada_ao_revisor_so_para_roubo(tmp_path):
    metricas = Metricas()
    fluxo = Fluxo(_cluster_sigma(metricas), StoreCompartilhado(tmp_path))
    fluxo.iniciar(Estado(id="PCDF-SIM-0002", texto=ROUBO))
    assert metricas.chamadas.get("revisor-svc", 0) == 1

    metricas2 = Metricas()
    fluxo2 = Fluxo(_cluster_sigma(metricas2), StoreCompartilhado(tmp_path))
    fluxo2.iniciar(Estado(id="PCDF-SIM-0009", texto=FURTO))
    assert "revisor-svc" not in metricas2.chamadas


# -- Gateway (guardrail + fluxo) -----------------------------------------

def test_gateway_processa_boletim_limpo(tmp_path):
    gw = Gateway(Fluxo(_cluster_sigma(), StoreCompartilhado(tmp_path)),
                Guardrail(limite_por_janela=10))
    r = gw.processar("PCDF-SIM-0002", ROUBO, origem="delegacia-01")
    assert isinstance(r, Pausado)


def test_gateway_barra_boletim_com_injecao(tmp_path):
    gw = Gateway(Fluxo(_cluster_sigma(), StoreCompartilhado(tmp_path)),
                Guardrail(limite_por_janela=10))
    with pytest.raises(EntradaRejeitada):
        gw.processar("PCDF-SIM-9999", BOLETIM_SUSPEITO, origem="delegacia-02")


def test_gateway_barra_apos_estourar_taxa(tmp_path):
    gw = Gateway(Fluxo(_cluster_sigma(), StoreCompartilhado(tmp_path)),
                Guardrail(limite_por_janela=1, janela_s=60.0))
    gw.processar("PCDF-SIM-0002", ROUBO, origem="delegacia-03")
    with pytest.raises(TaxaExcedida):
        gw.processar("PCDF-SIM-0009", FURTO, origem="delegacia-03")


def test_gateway_entrada_rejeitada_nao_consome_nenhuma_cota_de_processamento(tmp_path):
    store = StoreCompartilhado(tmp_path)
    gw = Gateway(Fluxo(_cluster_sigma(), store), Guardrail(limite_por_janela=10))
    with pytest.raises(EntradaRejeitada):
        gw.processar("PCDF-SIM-9999", BOLETIM_SUSPEITO, origem="delegacia-02")
    assert list(tmp_path.glob("*.json")) == []
