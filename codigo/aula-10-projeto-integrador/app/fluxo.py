"""O fluxo do SIGMA — investigar -> analisar -> jurídico -> [roteador decide]
-> (revisar) -> [BREAKPOINT] -> consolidar. A mesma espinha dorsal desde a
Aula 7, cada etapa uma chamada de Service (Aula 8/9), com uma diferença: a
etapa seguinte a `juridico` não vem mais só de um dicionário fixo — vem de
`ROTEADORES_CONDICIONAIS` (Aula 6) quando existir um roteador para a etapa
atual.
"""

from __future__ import annotations

from datetime import datetime, timezone

from .cluster import Cluster
from .memoria import Estado
from .roteador import ROTEADORES_CONDICIONAIS
from .store import Concluido, DecisaoHumana, Pausado, PausaParaHumano, StoreCompartilhado

SERVICO_DA_ETAPA = {
    "investigar": "investigador-svc",
    "analisar": "analista-svc",
    "juridico": "juridico-svc",
    "revisar": "revisor-svc",
    "consolidar": "consolidador-svc",
}
# Arestas ESTÁTICAS (Aula 6) — o padrão para quem não tem roteador registrado.
PROXIMA_ETAPA = {
    "investigar": "analisar",
    "analisar": "juridico",
    "revisar": "aguardando_aprovacao",
    "consolidar": "fim",
}


class Fluxo:
    def __init__(self, cluster: Cluster, store: StoreCompartilhado, max_ciclos_hitl: int = 3) -> None:
        self.cluster = cluster
        self.store = store
        self.max_ciclos_hitl = max_ciclos_hitl

    def _rodar(self, e: Estado):
        while e.etapa not in ("fim", "aguardando_aprovacao"):
            servico = SERVICO_DA_ETAPA[e.etapa]
            etapa_atual = e.etapa
            e, pod, duracao_ms = self.cluster.chamar(servico, e)   # comunicação entre pods, medida
            e.atendido_por.append({"etapa": etapa_atual, "pod": pod, "duracao_ms": duracao_ms})

            roteador = ROTEADORES_CONDICIONAIS.get(etapa_atual)    # <- aresta condicional (Aula 6)
            e.etapa = roteador(e) if roteador else PROXIMA_ETAPA[etapa_atual]

        if e.etapa == "aguardando_aprovacao":
            cid = self.store.salvar(e)                        # NÃO fica na memória do pod
            raise PausaParaHumano(
                cid, e.tipificacao_proposta,
                f"Aprovar a tipificação proposta para {e.id}? "
                "(aprovar / corrigir / rejeitar-com-nota)",
            )
        return Concluido(e)

    def iniciar(self, estado: Estado):
        try:
            return self._rodar(estado)
        except PausaParaHumano as p:
            return Pausado(p.checkpoint, p.proposta, p.pergunta)

    def retomar(self, checkpoint: str, decisao: DecisaoHumana):
        e = self.store.carregar(checkpoint)                   # pode ser OUTRO pod lendo
        e.aprovacoes.append({
            "quando": datetime.now(timezone.utc).isoformat(),
            "operador": decisao.operador,
            "aprovado": decisao.aprovado,
            "nota": decisao.nota,
            "corrigiu": decisao.tipificacao_corrigida is not None,
        })

        if decisao.aprovado:
            e.tipificacao_final = e.tipificacao_proposta
            e.etapa = "consolidar"
        elif decisao.tipificacao_corrigida:
            e.tipificacao_final = {**decisao.tipificacao_corrigida, "origem": "correção humana"}
            e.etapa = "consolidar"
        else:
            rejeicoes = sum(1 for a in e.aprovacoes if not a["aprovado"] and not a["corrigiu"])
            if rejeicoes >= self.max_ciclos_hitl:
                e.tipificacao_final = {"artigo": "PENDENTE", "natureza": "indefinida",
                                       "origem": f"{rejeicoes} rejeições — encaminhado ao humano"}
                e.etapa = "consolidar"
            else:
                e.etapa = "juridico"

        try:
            return self._rodar(e)
        except PausaParaHumano as p:
            return Pausado(p.checkpoint, p.proposta, p.pergunta)
