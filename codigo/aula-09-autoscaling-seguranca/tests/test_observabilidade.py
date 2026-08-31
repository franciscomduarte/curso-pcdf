"""Testes de Metricas e do traço — sem depender do Cluster."""

from __future__ import annotations

from app.observabilidade import Metricas, formatar_traco


def test_registrar_sucesso_conta_chamada_e_latencia():
    m = Metricas()
    m.registrar("svc-a", 10.0, ok=True)
    m.registrar("svc-a", 20.0, ok=True)
    assert m.chamadas["svc-a"] == 2
    assert m.falhas.get("svc-a", 0) == 0
    assert m.latencia_media_ms("svc-a") == 15.0


def test_registrar_falha_conta_chamada_mas_nao_latencia():
    m = Metricas()
    m.registrar("svc-a", 0.0, ok=False)
    assert m.chamadas["svc-a"] == 1
    assert m.falhas["svc-a"] == 1
    assert m.latencia_media_ms("svc-a") == 0.0   # sem amostra de latência


def test_taxa_de_erro():
    m = Metricas()
    m.registrar("svc-a", 5.0, ok=True)
    m.registrar("svc-a", 0.0, ok=False)
    m.registrar("svc-a", 0.0, ok=False)
    assert m.taxa_de_erro("svc-a") == 2 / 3


def test_taxa_de_erro_sem_chamadas_e_zero():
    m = Metricas()
    assert m.taxa_de_erro("nunca-chamado") == 0.0


def test_latencia_p95_com_dez_amostras():
    m = Metricas()
    for i in range(1, 11):        # 10, 20, ..., 100
        m.registrar("svc-a", float(i * 10), ok=True)
    assert m.latencia_p95_ms("svc-a") == 100.0   # a mais alta, com 10 amostras


def test_painel_lista_servicos_em_ordem_alfabetica():
    m = Metricas()
    m.registrar("z-svc", 1.0, ok=True)
    m.registrar("a-svc", 1.0, ok=True)
    painel = m.painel()
    assert painel.index("a-svc") < painel.index("z-svc")


def test_formatar_traco():
    atendido_por = [
        {"etapa": "investigar", "pod": "investigador-deploy-0001", "duracao_ms": 1.234},
        {"etapa": "analisar", "pod": "analista-deploy-0002", "duracao_ms": 0.5},
    ]
    texto = formatar_traco(atendido_por)
    assert "investigar" in texto and "investigador-deploy-0001" in texto
    assert "1.2ms" in texto
