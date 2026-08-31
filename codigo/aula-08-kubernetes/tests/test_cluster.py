"""Testes do cluster mínimo — rodam offline, só com a biblioteca padrão."""

from __future__ import annotations

import pytest

from app.cluster import Cluster, ServicoIndisponivel


def eco(valor, config=None):
    return {"valor": valor, "config": config or {}}


def test_deployment_cria_o_numero_certo_de_pods():
    c = Cluster()
    c.criar_deployment("d", eco, replicas=3)
    assert len(c.deployments["d"].pods) == 3
    assert all(p.status == "Running" for p in c.deployments["d"].pods)


def test_service_roteia_em_round_robin():
    c = Cluster()
    c.criar_deployment("d", eco, replicas=2)
    c.criar_service("svc", "d")

    _, pod1 = c.chamar("svc", "a")
    _, pod2 = c.chamar("svc", "b")
    _, pod3 = c.chamar("svc", "c")

    assert pod1 != pod2          # alterna entre as 2 réplicas
    assert pod1 == pod3          # e volta pra primeira na 3ª chamada


def test_configmap_chega_na_imagem():
    c = Cluster()
    c.criar_configmap("cm", nivel="alto")
    c.criar_deployment("d", eco, replicas=1, config_map="cm")
    c.criar_service("svc", "d")

    resultado, _ = c.chamar("svc", "x")
    assert resultado["config"] == {"nivel": "alto"}


def test_deployment_sem_configmap_recebe_config_vazio():
    c = Cluster()
    c.criar_deployment("d", eco, replicas=1)
    c.criar_service("svc", "d")
    resultado, _ = c.chamar("svc", "x")
    assert resultado["config"] == {}


def test_matar_pod_marca_crashloopbackoff_mas_nao_remove():
    c = Cluster()
    c.criar_deployment("d", eco, replicas=2)
    morto = c.matar_pod("d", 0)
    status = {p.nome: p.status for p in c.deployments["d"].pods}
    assert status[morto] == "CrashLoopBackOff"
    assert sum(1 for s in status.values() if s == "Running") == 1


def test_service_ainda_atende_se_sobra_pelo_menos_1_pod_running():
    c = Cluster()
    c.criar_deployment("d", eco, replicas=2)
    c.criar_service("svc", "d")
    c.matar_pod("d", 0)

    resultado, pod = c.chamar("svc", "x")   # não levanta ServicoIndisponivel
    assert resultado["valor"] == "x"


def test_service_indisponivel_sem_nenhum_pod_running():
    c = Cluster()
    c.criar_deployment("d", eco, replicas=1)
    c.criar_service("svc", "d")
    c.matar_pod("d", 0)

    with pytest.raises(ServicoIndisponivel):
        c.chamar("svc", "x")


def test_reconciliar_recria_pods_mortos_ate_bater_replicas():
    c = Cluster()
    c.criar_deployment("d", eco, replicas=2)
    c.matar_pod("d", 0)
    c.matar_pod("d", 0)   # mata a última Running restante também

    assert all(p.status == "CrashLoopBackOff" for p in c.deployments["d"].pods)
    recriados = c.reconciliar()
    assert len(recriados) == 2
    assert len(c.deployments["d"].pods) == 2
    assert all(p.status == "Running" for p in c.deployments["d"].pods)


def test_escalar_aumenta_e_diminui_replicas():
    c = Cluster()
    c.criar_deployment("d", eco, replicas=1)
    c.escalar("d", 4)
    assert len(c.deployments["d"].pods) == 4
    c.escalar("d", 2)
    assert len(c.deployments["d"].pods) == 2


def test_eventos_registram_o_ciclo_de_vida():
    c = Cluster()
    c.criar_deployment("d", eco, replicas=1)
    c.criar_service("svc", "d")
    c.chamar("svc", "x")
    assert any("criado" in ev for ev in c.eventos)
    assert any("roteou" in ev for ev in c.eventos)
