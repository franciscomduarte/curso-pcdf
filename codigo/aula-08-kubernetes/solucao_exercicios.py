"""Gabarito dos laboratórios da Aula 8.

    python solucao_exercicios.py            # todos
    python solucao_exercicios.py basico
    python solucao_exercicios.py intermediario
    python solucao_exercicios.py desafio
"""

from __future__ import annotations

import sys

from app.agentes import analista, consolidador, investigador, juridico
from app.bases_sinteticas import OCORRENCIAS
from app.cluster import Cluster, ServicoIndisponivel
from app.fluxo import Fluxo
from app.memoria import Estado
from app.store import DecisaoHumana, Pausado, StoreCompartilhado


# ---------------------------------------------------------------------------
# LAB BÁSICO — escalar e observar o round-robin com 3 réplicas / 3 ocorrências
# ---------------------------------------------------------------------------
def lab_basico() -> None:
    print("== LAB BÁSICO: escalar o investigador para 3 réplicas ==")
    c = Cluster()
    c.criar_deployment("investigador-deploy", investigador, replicas=1)
    c.criar_service("investigador-svc", "investigador-deploy")

    c.escalar("investigador-deploy", 3)
    for oc_id in OCORRENCIAS:
        c.chamar("investigador-svc", Estado(id=oc_id, texto=OCORRENCIAS[oc_id]))

    print(f"  {len(OCORRENCIAS)} ocorrências, 3 réplicas:")
    for linha in c.status().splitlines()[1:]:
        print(f"    {linha}")
    print("  cada réplica atendeu 1 — é o que round-robin com N chamadas == N réplicas dá.")


# ---------------------------------------------------------------------------
# LAB INTERMEDIÁRIO — store compartilhado (outro "pod" retoma) + ConfigMap live
# ---------------------------------------------------------------------------
def _montar_cluster_sigma(detalhe: str = "padrao") -> Cluster:
    c = Cluster()
    c.criar_configmap("juridico-config", detalhe=detalhe)
    c.criar_deployment("investigador-deploy", investigador, replicas=1)
    c.criar_deployment("analista-deploy", analista, replicas=1)
    c.criar_deployment("juridico-deploy", juridico, replicas=1, config_map="juridico-config")
    c.criar_deployment("consolidador-deploy", consolidador, replicas=1)
    c.criar_service("investigador-svc", "investigador-deploy")
    c.criar_service("analista-svc", "analista-deploy")
    c.criar_service("juridico-svc", "juridico-deploy")
    c.criar_service("consolidador-svc", "consolidador-deploy")
    return c


def lab_intermediario() -> None:
    print("\n== LAB INTERMEDIÁRIO (1): store compartilhado — outro cluster retoma ==")
    store = StoreCompartilhado()   # o MESMO diretório em saida/ — é o "volume compartilhado"

    cluster_a = _montar_cluster_sigma()
    fluxo_a = Fluxo(cluster_a, store)
    r = fluxo_a.iniciar(Estado(id="PCDF-SIM-0002", texto=OCORRENCIAS["PCDF-SIM-0002"]))
    assert isinstance(r, Pausado)
    print(f"  cluster A pausou e salvou: {r.checkpoint}")

    # "outro pod" = um Cluster/Fluxo TOTALMENTE novo, sem nenhum estado do cluster_a —
    # só compartilha o StoreCompartilhado (o mesmo diretório em saida/).
    cluster_b = _montar_cluster_sigma()
    fluxo_b = Fluxo(cluster_b, store)
    r2 = fluxo_b.retomar(r.checkpoint, DecisaoHumana(aprovado=True, operador="delegado"))
    print(f"  cluster B (novo, nunca viu essa investigação) retomou e concluiu: "
          f"{r2.estado.dossie['tipificacao']['artigo']}")
    print("  funcionou porque o estado nunca esteve na memória de nenhum pod específico.")

    print("\n== LAB INTERMEDIÁRIO (2): ConfigMap muda o comportamento sem redeploy ==")
    c_padrao = _montar_cluster_sigma(detalhe="padrao")
    c_verboso = _montar_cluster_sigma(detalhe="verboso")
    for nome, c in (("padrao", c_padrao), ("verboso", c_verboso)):
        e = Estado(id="PCDF-SIM-0002", texto=OCORRENCIAS["PCDF-SIM-0002"])
        e, _ = c.chamar("investigador-svc", e)
        e, _ = c.chamar("analista-svc", e)
        e, _ = c.chamar("juridico-svc", e)
        print(f"  detalhe={nome}: fundamento_detalhado presente? "
              f"{'fundamento_detalhado' in e.tipificacao_proposta}")
    print("  mesma função juridico() nos dois; só o ConfigMap mudou.")


# ---------------------------------------------------------------------------
# DESAFIO — rolling update: trocar o Deployment por trás de um Service sem parar
# ---------------------------------------------------------------------------
def rolling_update(cluster: Cluster, servico: str, deployment_novo: str, nova_imagem,
                    novo_config_map: str | None = None, passos: int = 3) -> list[dict]:
    """Sobe um Deployment novo ao lado do antigo e desliza réplicas gradualmente.

    Em nenhum passo o Service fica sem pelo menos 1 pod Running — é a mesma
    ideia de um rolling update real (ReplicaSet novo sobe, o antigo desce,
    o Service aponta para o que estiver com pods prontos).
    """
    svc = cluster.services[servico]
    antigo = cluster.deployments[svc.deployment]
    total = antigo.replicas
    cluster.criar_deployment(deployment_novo, nova_imagem, replicas=0, config_map=novo_config_map)

    trilha = []
    for passo in range(1, passos + 1):
        novo_n = round(total * passo / passos)
        antigo_n = total - novo_n
        cluster.escalar(deployment_novo, novo_n)
        cluster.escalar(antigo.nome, antigo_n)
        trilha.append({"passo": passo, antigo.nome: antigo_n, deployment_novo: novo_n})

    svc.deployment = deployment_novo
    del cluster.deployments[antigo.nome]
    return trilha


def desafio() -> None:
    print("\n== DESAFIO: rolling update do juridico-deploy (padrao -> verboso) ==")
    c = _montar_cluster_sigma(detalhe="padrao")
    c.escalar("juridico-deploy", 2)
    c.criar_configmap("juridico-config-v2", detalhe="verboso")

    trilha = rolling_update(c, "juridico-svc", "juridico-deploy-v2", juridico,
                            novo_config_map="juridico-config-v2", passos=2)
    for passo in trilha:
        print(f"  {passo}")

    e = Estado(id="PCDF-SIM-0002", texto=OCORRENCIAS["PCDF-SIM-0002"])
    e, pod = c.chamar("juridico-svc", e)
    print(f"  service/juridico-svc agora responde via {pod} (deployment novo)")
    print(f"  'juridico-deploy' (antigo) ainda existe? {'juridico-deploy' in c.deployments}")


# ===========================================================================
# EXERCÍCIOS EXTRAS (se sobrar tempo) — referência
# ===========================================================================

# --- Extra 1: escalar um agente a zero e trazer de volta (intermediário) ----
def extra_escala_a_zero() -> None:
    print("== EXTRA 1: escalar um agente a zero e trazer de volta ==")
    c = _montar_cluster_sigma()
    texto = OCORRENCIAS["PCDF-SIM-0002"]

    c.escalar("investigador-deploy", 0)
    try:
        c.chamar("investigador-svc", Estado(id="X", texto=texto))
        print("  (não deveria chegar aqui)")
    except ServicoIndisponivel as exc:
        print(f"  com 0 réplicas -> {exc}")

    recriados = c.reconciliar()
    print(f"  reconciliar(): {recriados or 'não recriou nada — 0 É o número desejado'}")

    c.escalar("investigador-deploy", 1)
    _, pod = c.chamar("investigador-svc", Estado(id="X", texto=texto))
    print(f"  escalar(..., 1) -> atendido por {pod}")
    print("  quando faz sentido: um agente que só roda sob demanda (ex.: o Consolidador,")
    print("  que só age depois da aprovação humana) pode ficar a zero até haver trabalho.")


# --- Extra 2: round-robin se re-adapta quando um pod morre no meio ---------
def extra_balanceamento_sob_falha() -> None:
    print("\n== EXTRA 2: round-robin se re-adapta quando um pod morre no meio ==")
    c = Cluster()
    c.criar_deployment("investigador-deploy", investigador, replicas=3)
    c.criar_service("investigador-svc", "investigador-deploy")
    texto = OCORRENCIAS["PCDF-SIM-0002"]

    falhas = 0
    for i in range(9):
        if i == 3:
            morto = c.matar_pod("investigador-deploy", 0)
            print(f"  [chamada {i}] matei {morto} (sem reconciliar)")
        try:
            c.chamar("investigador-svc", Estado(id=f"X{i}", texto=texto))
        except ServicoIndisponivel:
            falhas += 1

    print(f"  9 chamadas, {falhas} falha(s) — o Service respondeu pelos pods vivos")
    for linha in c.status().splitlines()[1:]:
        print(f"    {linha}")
    print("  a réplica morta parou de receber; as vivas cobriram — distribuição fica desigual.")


def extras() -> None:
    extra_escala_a_zero()
    extra_balanceamento_sob_falha()


LABS = {
    "basico": lab_basico,
    "intermediario": lab_intermediario,
    "desafio": desafio,
    "extras": extras,
}

if __name__ == "__main__":
    alvo = sys.argv[1] if len(sys.argv) > 1 else None
    if alvo in LABS:
        LABS[alvo]()
    else:
        for fn in LABS.values():
            fn()
