"""Testes dos exercícios extras da Aula 8."""

from __future__ import annotations

import pytest

from app.cluster import Cluster, ServicoIndisponivel
from app.memoria import Estado


def eco(valor, config=None):
    return valor


def test_escalar_a_zero_deixa_service_indisponivel_e_reconciliar_nao_recria():
    c = Cluster()
    c.criar_deployment("d", eco, replicas=2)
    c.criar_service("svc", "d")

    c.escalar("d", 0)
    with pytest.raises(ServicoIndisponivel):
        c.chamar("svc", Estado(id="X", texto="t"))

    assert c.reconciliar() == []                 # 0 É o número desejado — nada a recriar
    assert c.deployments["d"].pods == []

    c.escalar("d", 1)
    _, pod = c.chamar("svc", Estado(id="X", texto="t"))
    assert pod.startswith("d-")


def test_round_robin_se_readapta_quando_um_pod_morre_sem_reconciliar():
    c = Cluster()
    c.criar_deployment("d", eco, replicas=3)
    c.criar_service("svc", "d")

    falhas = 0
    for i in range(9):
        if i == 3:
            c.matar_pod("d", 0)
        try:
            c.chamar("svc", Estado(id=f"X{i}", texto="t"))
        except ServicoIndisponivel:
            falhas += 1

    assert falhas == 0                           # nunca ficou sem pod vivo
    vivos = [p for p in c.deployments["d"].pods if p.status == "Running"]
    assert len(vivos) == 2
    assert sum(p.chamadas_atendidas for p in vivos) + \
           sum(p.chamadas_atendidas for p in c.deployments["d"].pods if p.status != "Running") == 9
