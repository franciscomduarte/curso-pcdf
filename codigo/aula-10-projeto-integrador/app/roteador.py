"""A peça que faltava integrar: uma ARESTA CONDICIONAL (Aula 6) decidindo,
dentro do cluster distribuído (Aula 8/9), qual o próximo serviço.

Nas Aulas 8-9, `PROXIMA_ETAPA` (em `fluxo.py`) era um dicionário fixo — toda
ocorrência passava exatamente pelas mesmas etapas, na mesma ordem. Isso é
uma ARESTA ESTÁTICA no vocabulário da Aula 6. Aqui, depois do Jurídico, o
caminho passa a depender do ESTADO da própria ocorrência: casos com
tipificação grave (roubo — presença de grave ameaça) são roteados para uma
etapa extra de revisão dupla antes do breakpoint humano; casos sem grave
ameaça (furto) vão direto, como sempre foi.

O roteador nunca decide SOZINHO se um caso é grave — ele só lê o que o
Jurídico já concluiu (`tipificacao_proposta`). É uma decisão de ROTEAMENTO
(quantos agentes revisam antes do humano decidir), nunca uma decisão sobre
a pessoa investigada.
"""

from __future__ import annotations

from .memoria import Estado

ETAPA_REVISAO = "revisar"
ETAPA_APROVACAO = "aguardando_aprovacao"


def decidir_apos_juridico(e: Estado) -> str:
    """A aresta condicional (Aula 6) que decide o que acontece depois de
    `juridico`. Critério: tipificação de ROUBO (grave ameaça confirmada
    pelo Jurídico) exige uma segunda leitura antes do breakpoint humano —
    o mesmo princípio de dupla conferência para casos de maior gravidade
    que já rege processos institucionais reais, aqui expresso como uma
    aresta do grafo em vez de uma etapa manual à parte."""
    proposta = e.tipificacao_proposta or {}
    if proposta.get("natureza") == "Roubo":
        return ETAPA_REVISAO
    return ETAPA_APROVACAO


# Registro de roteadores condicionais por etapa de origem — o análogo de
# `Grafo.aresta_condicional(origem, roteador)` da Aula 6, só que aqui a
# origem é um Service do cluster, não uma função Python direta.
ROTEADORES_CONDICIONAIS = {
    "juridico": decidir_apos_juridico,
}
