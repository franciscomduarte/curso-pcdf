"""Testes do cluster — igual à Aula 8, revalidando a mudança de `chamar()`
(agora devolve 3 valores: resultado, pod, duração) e o registro em Metricas."""

from __future__ import annotations

import pytest

from app.cluster import Cluster, ServicoIndisponivel
from app.observabilidade import Metricas


def eco(valor, config=None):
    return {"valor": valor, "config": config or {}}


def test_chamar_devolve_resultado_pod_e_duracao():
    c = Cluster()
    c.criar_deployment("d", eco, replicas=1)
    c.criar_service("svc", "d")
    resultado, pod, duracao_ms = c.chamar("svc", "x")
    assert resultado["valor"] == "x"
    assert pod.startswith("d-")
    assert duracao_ms >= 0.0


def test_round_robin_ainda_funciona():
    c = Cluster()
    c.criar_deployment("d", eco, replicas=2)
    c.criar_service("svc", "d")
    _, pod1, _ = c.chamar("svc", "a")
    _, pod2, _ = c.chamar("svc", "b")
    assert pod1 != pod2


def test_self_healing_ainda_funciona():
    c = Cluster()
    c.criar_deployment("d", eco, replicas=2)
    c.matar_pod("d", 0)
    c.matar_pod("d", 0)
    recriados = c.reconciliar()
    assert len(recriados) == 2
    assert all(p.status == "Running" for p in c.deployments["d"].pods)


def test_chamada_registra_sucesso_em_metricas():
    m = Metricas()
    c = Cluster(metricas=m)
    c.criar_deployment("d", eco, replicas=1)
    c.criar_service("svc", "d")
    c.chamar("svc", "x")
    assert m.chamadas["svc"] == 1
    assert m.falhas.get("svc", 0) == 0
    assert m.latencia_media_ms("svc") >= 0.0


def test_servico_indisponivel_registra_falha_em_metricas():
    m = Metricas()
    c = Cluster(metricas=m)
    c.criar_deployment("d", eco, replicas=1)
    c.criar_service("svc", "d")
    c.matar_pod("d", 0)

    with pytest.raises(ServicoIndisponivel):
        c.chamar("svc", "x")
    assert m.chamadas["svc"] == 1
    assert m.falhas["svc"] == 1
    assert m.taxa_de_erro("svc") == 1.0


def test_cluster_sem_metricas_explicitas_cria_uma_propria():
    c = Cluster()
    assert isinstance(c.metricas, Metricas)
