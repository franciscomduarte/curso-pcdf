"""Nível intermediário: os 4 padrões de fluxo, lado a lado, na mesma ocorrência.

    python main_comparar.py
    python main_comparar.py PCDF-SIM-0009     # a trivial: veja o supervisor economizar

Depois, o Debate isolado numa sub-decisão ambígua.
"""

from __future__ import annotations

import sys

from app import padroes
from app.barramento import Auditor, Barramento
from app.bases_sinteticas import AVISO_DADOS, OCORRENCIAS
from app.especialistas import Dossie
from app.llm import MockLLM


def _novo(oc_id: str) -> Dossie:
    return Dossie(id=oc_id, texto=OCORRENCIAS[oc_id])


def main() -> None:
    oc_id = sys.argv[1] if len(sys.argv) > 1 else "PCDF-SIM-0002"
    print(f"* {AVISO_DADOS}")
    print(f"\nOcorrência {oc_id}: {OCORRENCIAS[oc_id][:90]}...\n")

    llm = MockLLM()
    bus, auditor = Barramento(), Auditor()
    bus.assinar("orquestracao.concluida", auditor.ao_receber)

    resultados = [
        ("pipeline", *padroes.pipeline(_novo(oc_id))),
        ("supervisor", *padroes.supervisor(_novo(oc_id), llm)),
        ("broker", *padroes.broker(_novo(oc_id))),
        ("blackboard", *padroes.blackboard(_novo(oc_id))),
    ]

    print("PADRÃO       | métricas")
    print("-" * 78)
    for nome, d, m in resultados:
        print(m.linha())
        print(f"             -> natureza={d.classificacao and d.classificacao['natureza']}, "
              f"completo={d.completo}, pendências={len(d.pendencias)}")
        bus.publicar("orquestracao.concluida", "orquestrador",
                     {"padrao": nome, "custo": m.custo, "latencia_ms": m.latencia_ms})
    print(f"\n(o Auditor registrou {len(auditor.trilha)} execuções de orquestração)\n")

    # Debate: só a sub-decisão da natureza
    veredito, md = padroes.debate(
        "Esta ocorrência é Furto ou Roubo?", OCORRENCIAS[oc_id], llm)
    print("-" * 78)
    print(md.linha())
    papeis = ["promotor", "defensor"]
    for r, opinioes in enumerate(veredito["por_rodada"], 1):
        print(f"  rodada {r}:")
        for i, op in enumerate(opinioes):
            print(f"    {papeis[i]}: {op['resposta']} (conf {op['confianca']:.2f}) — {op['razao']}")
    v = veredito["veredito"]
    print(f"  VEREDITO: {v['resposta']}  ({v['justificativa']})")


if __name__ == "__main__":
    main()
