"""Nível intermediário: o checkpoint sobrevive ao processo.

    python main_retomar.py iniciar         # roda até o breakpoint, imprime o checkpoint, ENCERRA
    python main_retomar.py aprovar <cid>   # OUTRO processo carrega o checkpoint e conclui

Simula o mundo real: o agente para, o servidor só volta a olhar horas depois,
possivelmente de outra máquina. O estado (e a memória dos agentes) estava no disco.
"""

from __future__ import annotations

import sys

from app.bases_sinteticas import AVISO_DADOS, OCORRENCIAS
from app.hitl import Checkpoint, Concluido, DecisaoHumana, Fluxo, Pausado
from app.memoria import Estado


def iniciar(oc_id: str) -> None:
    r = Fluxo().iniciar(Estado(id=oc_id, texto=OCORRENCIAS[oc_id]))
    assert isinstance(r, Pausado)
    print(f"fluxo pausou. checkpoint = {r.checkpoint}")
    print(f"proposta aguardando aprovação: {r.proposta['artigo']}")
    print("\n(este processo vai encerrar agora — o estado está no disco em saida/)")
    print(f"para concluir:  python main_retomar.py aprovar {r.checkpoint}")


def aprovar(cid: str) -> None:
    # nada de estado em memória: só o id do checkpoint
    antes = Checkpoint.carregar(cid)
    print(f"processo NOVO. carregou o checkpoint {cid}")
    print(f"  ocorrência: {antes.id}  etapa: {antes.etapa}")
    print(f"  memória do Investigador (persistida): {antes.memorias.get('investigador', {}).get('notas')}")

    r = Fluxo().retomar(cid, DecisaoHumana(aprovado=True, operador="delegado"))
    assert isinstance(r, Concluido)
    print(f"\nconcluído. tipificação final: {r.estado.dossie['tipificacao']}")
    print(f"decisões humanas registradas: {len(r.estado.aprovacoes)}")


def main() -> None:
    print(f"* {AVISO_DADOS}\n")
    cmd = sys.argv[1] if len(sys.argv) > 1 else "iniciar"
    if cmd == "iniciar":
        iniciar(sys.argv[2] if len(sys.argv) > 2 else "PCDF-SIM-0002")
    elif cmd == "aprovar":
        aprovar(sys.argv[2])
    else:
        raise SystemExit("uso: python main_retomar.py [iniciar <oc_id> | aprovar <checkpoint>]")


if __name__ == "__main__":
    main()
