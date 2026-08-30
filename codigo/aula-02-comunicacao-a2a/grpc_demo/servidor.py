"""Servidor gRPC do Classificador.

    python grpc_demo/servidor.py      # escuta em localhost:50051

Rode ./gerar.sh (ou gerar.ps1) antes, para criar os _pb2.
"""

from __future__ import annotations

import sys
from concurrent import futures
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))          # para achar os _pb2
sys.path.insert(0, str(Path(__file__).parent.parent))   # para achar o pacote app/

try:
    import grpc
    import classificador_pb2 as pb
    import classificador_pb2_grpc as pb_grpc
except ImportError as exc:  # noqa: BLE001
    raise SystemExit(
        "Faltam dependências/stubs. Rode:\n"
        "  pip install -r requirements-opcionais.txt\n"
        "  ./grpc_demo/gerar.sh   (ou gerar.ps1)\n"
        f"({exc})"
    )

from app.ocorrencias import classificar  # noqa: E402


class ClassificadorServicer(pb_grpc.ClassificadorServicer):
    def Classificar(self, request, context):  # noqa: N802 (nome vem do proto)
        resultado = classificar({
            "natureza": request.natureza,
            "data_fato": request.data_fato,
            "local": request.local,
        })
        return pb.Classificacao(
            id=request.id,
            natureza=resultado["natureza"],
            prioridade=resultado["prioridade"],
            revisao_humana_obrigatoria=resultado["revisao_humana_obrigatoria"],
        )


def main() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    pb_grpc.add_ClassificadorServicer_to_server(ClassificadorServicer(), server)
    server.add_insecure_port("[::]:50051")  # aula: sem TLS. Produção: mTLS (Aula 9)
    server.start()
    print("Classificador gRPC ouvindo em localhost:50051 (Ctrl+C para sair)")
    server.wait_for_termination()


if __name__ == "__main__":
    main()
