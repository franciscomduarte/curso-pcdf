"""Testes do HPA — herdado sem mudança da Aula 9 (mesma cobertura)."""

from __future__ import annotations

from app.autoscaler import HPA, avaliar
from app.cluster import Cluster


def eco(valor, config=None):
    return valor


def _cluster_com_deployment(replicas=1):
    c = Cluster()
    c.criar_deployment("d", eco, replicas=replicas)
    return c


def test_carga_dentro_do_alvo_nao_escala():
    c = _cluster_com_deployment(replicas=2)
    hpa = HPA(nome="h", deployment="d", alvo_por_pod=5.0, min_replicas=1, max_replicas=10)
    r = avaliar(c, hpa, carga_atual=5.0)   # média por réplica, não total
    assert r["replicas_depois"] == 2
    assert c.deployments["d"].replicas == 2


def test_carga_acima_do_alvo_escala_para_cima():
    c = _cluster_com_deployment(replicas=1)
    hpa = HPA(nome="h", deployment="d", alvo_por_pod=3.0, min_replicas=1, max_replicas=10)
    r = avaliar(c, hpa, carga_atual=9.0)   # ceil(1 * 9/3) = 3
    assert r["replicas_depois"] == 3


def test_carga_zero_vai_para_o_minimo():
    c = _cluster_com_deployment(replicas=5)
    hpa = HPA(nome="h", deployment="d", alvo_por_pod=3.0, min_replicas=2, max_replicas=10)
    r = avaliar(c, hpa, carga_atual=0.0)
    assert r["replicas_depois"] == 2


def test_nunca_ultrapassa_max_replicas():
    c = _cluster_com_deployment(replicas=1)
    hpa = HPA(nome="h", deployment="d", alvo_por_pod=1.0, min_replicas=1, max_replicas=4)
    r = avaliar(c, hpa, carga_atual=1000.0)
    assert r["replicas_depois"] == 4


def test_nunca_fica_abaixo_de_min_replicas():
    c = _cluster_com_deployment(replicas=3)
    hpa = HPA(nome="h", deployment="d", alvo_por_pod=100.0, min_replicas=2, max_replicas=10)
    r = avaliar(c, hpa, carga_atual=0.1)
    assert r["replicas_depois"] == 2


def test_avaliar_de_fato_chama_escalar_no_cluster():
    c = _cluster_com_deployment(replicas=1)
    hpa = HPA(nome="h", deployment="d", alvo_por_pod=2.0, min_replicas=1, max_replicas=10)
    avaliar(c, hpa, carga_atual=8.0)
    assert len(c.deployments["d"].pods) == c.deployments["d"].replicas
