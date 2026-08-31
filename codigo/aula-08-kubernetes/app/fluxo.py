"""O fluxo do SIGMA rodando NO CLUSTER — investigar → analisar → jurídico →
[BREAKPOINT] → consolidar, igual à Aula 7, mas cada etapa é uma chamada de
Service (não uma chamada de função direta), e o checkpoint vai para o
`StoreCompartilhado` (não para o disco de um processo só).
"""

from __future__ import annotations

from datetime import datetime, timezone

from .cluster import Cluster
from .memoria import Estado
from .store import Concluido, DecisaoHumana, Pausado, PausaParaHumano, StoreCompartilhado

SERVICO_DA_ETAPA = {
    "investigar": "investigador-svc",
    "analisar": "analista-svc",
    "juridico": "juridico-svc",
    "consolidar": "consolidador-svc",
}
PROXIMA_ETAPA = {
    "investigar": "analisar",
    "analisar": "juridico",
    "juridico": "aguardando_aprovacao",
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
            e, pod = self.cluster.chamar(servico, e)          # comunicação entre pods
            e.atendido_por.append(f"{e.etapa}:{pod}")
            e.etapa = PROXIMA_ETAPA[e.etapa]

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
