"""Cliente gRPC — chama o Classificador e espera a resposta (síncrono).

    python grpc_demo/cliente.py        # com o servidor.py rodando em outro terminal
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import grpc
    import classificador_pb2 as pb
    import classificador_pb2_grpc as pb_grpc
except ImportError as exc:  # noqa: BLE001
    raise SystemExit(f"Rode ./grpc_demo/gerar.sh primeiro. ({exc})")


def main() -> None:
    with grpc.insecure_channel("localhost:50051") as canal:
        stub = pb_grpc.ClassificadorStub(canal)
        pedido = pb.OcorrenciaExtraida(
            id="PCDF-SIM-0002", natureza="Roubo",
            data_fato="2026-08-03", local="Taguatinga",
            resumo="assalto com simulacro de arma",
        )
        resposta = stub.Classificar(pedido, timeout=5)
        print(f"pedido : {pedido.id} / {pedido.natureza}")
        print(f"resposta: prioridade={resposta.prioridade} "
              f"revisar={resposta.revisao_humana_obrigatoria}")


if __name__ == "__main__":
    main()
