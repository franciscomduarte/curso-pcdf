"""Testes do fluxo do SIGMA rodando no cluster — checkpoint no store compartilhado."""

from __future__ import annotations

from pathlib import Path

from app.agentes import analista, consolidador, investigador, juridico
from app.bases_sinteticas import OCORRENCIAS
from app.cluster import Cluster
from app.fluxo import Fluxo
from app.memoria import Estado
from app.store import Concluido, DecisaoHumana, Pausado, StoreCompartilhado

TEXTO = OCORRENCIAS["PCDF-SIM-0002"]


def _cluster_sigma() -> Cluster:
    c = Cluster()
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


def test_fluxo_para_no_breakpoint_antes_de_tipificar(tmp_path):
    fluxo = Fluxo(_cluster_sigma(), StoreCompartilhado(tmp_path))
    r = fluxo.iniciar(Estado(id="PCDF-SIM-0002", texto=TEXTO))
    assert isinstance(r, Pausado)
    assert r.proposta["requer_decisao_humana"] is True


def test_atendido_por_registra_um_pod_por_etapa(tmp_path):
    fluxo = Fluxo(_cluster_sigma(), StoreCompartilhado(tmp_path))
    r = fluxo.iniciar(Estado(id="PCDF-SIM-0002", texto=TEXTO))
    e = fluxo.store.carregar(r.checkpoint)
    etapas = [item.split(":")[0] for item in e.atendido_por]
    assert etapas == ["investigar", "analisar", "juridico"]


def test_aprovar_conclui_e_consolida(tmp_path):
    fluxo = Fluxo(_cluster_sigma(), StoreCompartilhado(tmp_path))
    r = fluxo.iniciar(Estado(id="PCDF-SIM-0002", texto=TEXTO))
    r2 = fluxo.retomar(r.checkpoint, DecisaoHumana(aprovado=True, operador="delegado"))
    assert isinstance(r2, Concluido)
    assert r2.estado.dossie["tipificacao"]["artigo"] == "Art. 157 do CP (roubo)"


def test_store_compartilhado_permite_outro_cluster_retomar(tmp_path):
    """O ponto central da aula: quem retoma não precisa ser o mesmo processo
    (aqui, nem o mesmo Cluster) que pausou — só precisa do mesmo store."""
    store = StoreCompartilhado(tmp_path)

    fluxo_a = Fluxo(_cluster_sigma(), store)
    r = fluxo_a.iniciar(Estado(id="PCDF-SIM-0002", texto=TEXTO))
    assert isinstance(r, Pausado)

    fluxo_b = Fluxo(_cluster_sigma(), store)          # cluster NOVO, nunca viu essa investigação
    r2 = fluxo_b.retomar(r.checkpoint, DecisaoHumana(aprovado=True, operador="delegado"))
    assert isinstance(r2, Concluido)
    assert r2.estado.id == "PCDF-SIM-0002"


def test_configmap_verboso_acrescenta_fundamentacao(tmp_path):
    c_padrao = _cluster_sigma()
    c_verboso = _cluster_sigma()
    c_verboso.configmaps["juridico-config"].dados["detalhe"] = "verboso"

    fluxo_padrao = Fluxo(c_padrao, StoreCompartilhado(tmp_path / "a"))
    fluxo_verboso = Fluxo(c_verboso, StoreCompartilhado(tmp_path / "b"))

    r1 = fluxo_padrao.iniciar(Estado(id="PCDF-SIM-0002", texto=TEXTO))
    r2 = fluxo_verboso.iniciar(Estado(id="PCDF-SIM-0002", texto=TEXTO))

    assert "fundamento_detalhado" not in r1.proposta
    assert "fundamento_detalhado" in r2.proposta


def test_rejeitar_sem_correcao_volta_ao_juridico_e_registra_a_nota(tmp_path):
    fluxo = Fluxo(_cluster_sigma(), StoreCompartilhado(tmp_path))
    r = fluxo.iniciar(Estado(id="PCDF-SIM-0002", texto=TEXTO))

    r2 = fluxo.retomar(r.checkpoint, DecisaoHumana(aprovado=False, nota="reavaliar evidências"))
    assert isinstance(r2, Pausado)
    assert r2.proposta["considerou_nota_do_operador"] == "reavaliar evidências"


def test_rolling_update_troca_deployment_sem_deixar_service_sem_pod(tmp_path):
    from solucao_exercicios import rolling_update

    c = _cluster_sigma()
    c.escalar("juridico-deploy", 2)

    def juridico_v2(e, config=None):
        return juridico(e, config)

    trilha = rolling_update(c, "juridico-svc", "juridico-deploy-v2", juridico_v2, passos=2)

    assert "juridico-deploy" not in c.deployments
    assert c.services["juridico-svc"].deployment == "juridico-deploy-v2"
    assert len(c.deployments["juridico-deploy-v2"].pods) == 2
    # em nenhum passo da trilha os dois deployments somaram menos que o total original
    for passo in trilha:
        soma = passo["juridico-deploy"] + passo["juridico-deploy-v2"]
        assert soma == 2
