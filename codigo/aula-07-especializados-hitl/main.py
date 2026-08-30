"""Nível básico: o fluxo roda, PARA para o humano aprovar a tipificação, e continua.

    python main.py                     # PCDF-SIM-0002 -> aprova
    python main.py PCDF-SIM-0009 rejeitar
"""

from __future__ import annotations

import sys

from app.bases_sinteticas import AVISO_DADOS, OCORRENCIAS
from app.hitl import Concluido, DecisaoHumana, Fluxo, Pausado
from app.memoria import Estado


def main() -> None:
    print(f"* {AVISO_DADOS}\n")
    oc_id = sys.argv[1] if len(sys.argv) > 1 else "PCDF-SIM-0002"
    acao = sys.argv[2] if len(sys.argv) > 2 else "aprovar"

    fluxo = Fluxo()
    r = fluxo.iniciar(Estado(id=oc_id, texto=OCORRENCIAS[oc_id]))

    assert isinstance(r, Pausado), "o fluxo deveria ter pausado no breakpoint"
    print("=== BREAKPOINT — o fluxo parou ===")
    print("pergunta.:", r.pergunta)
    print("proposta.:", r.proposta)
    print("checkpoint gravado:", r.checkpoint, "\n")

    if acao == "rejeitar":
        # 1ª rodada: rejeita com nota -> volta ao Jurídico
        r = fluxo.retomar(r.checkpoint, DecisaoHumana(
            aprovado=False, nota="reavaliar: a testemunha não viu arma, só ouviu 'assalto'"))
        print("=== após rejeição com nota — o fluxo voltou ao Jurídico e parou de novo ===")
        print("nova proposta:", r.proposta, "\n")
        # 2ª rodada: corrige a tipificação
        r = fluxo.retomar(r.checkpoint, DecisaoHumana(
            aprovado=False,
            tipificacao_corrigida={"artigo": "Art. 155 do CP (furto)", "natureza": "Furto"},
            nota="tipifico como furto por ora"))
    else:
        r = fluxo.retomar(r.checkpoint, DecisaoHumana(aprovado=True, operador="escrivão de plantão"))

    assert isinstance(r, Concluido)
    d = r.estado.dossie
    print("=== DOSSIÊ CONSOLIDADO ===")
    print("tipificação:", d["tipificacao"])
    print("decisões humanas:", d["decisoes_humanas"])
    print("aviso......:", d["aviso"])
    print("\nmemória do Jurídico:", r.estado.memorias["juridico"]["notas"])


if __name__ == "__main__":
    main()
