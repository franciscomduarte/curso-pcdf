"""O agente Jurídico, de verdade, como um servidor HTTP — para rodar num Pod.

Só biblioteca padrão (`http.server`) de propósito: o ponto não é o framework
web, é mostrar como o MESMO `app/agentes.py::juridico` da aula vira um
processo de rede que um Deployment real do Kubernetes consegue rodar.

Diferença para o motor mínimo (app/cluster.py): lá o "ConfigMap" era um
dicionário lido na hora da chamada (equivalente a um volume montado, que
atualiza sem reiniciar o pod). Aqui, seguindo o padrão mais comum em
produção, o ConfigMap chega como VARIÁVEL DE AMBIENTE — e variável de
ambiente só é lida quando o processo INICIA. Mudar o ConfigMap real, nesse
modelo, exige reiniciar o pod (um rollout) para valer — é uma escolha de
design do Deployment (env vs. volume), não uma regra fixa do Kubernetes.

    python k8s_real/servidor.py            # sobe em http://localhost:8080
    curl -X POST localhost:8080/juridico -H "Content-Type: application/json" \\
         -d '{"id":"PCDF-SIM-0002","hipotese":{"natureza_provavel":"Roubo"}}'
"""

from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agentes import juridico
from app.memoria import Estado

DETALHE = os.environ.get("DETALHE", "padrao")   # vem do ConfigMap, injetado como env var


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/saude":
            self._responder(200, {"status": "ok", "detalhe": DETALHE})
        else:
            self._responder(404, {"erro": "rota desconhecida"})

    def do_POST(self) -> None:
        if self.path != "/juridico":
            self._responder(404, {"erro": "rota desconhecida"})
            return
        tamanho = int(self.headers.get("Content-Length", 0))
        corpo = json.loads(self.rfile.read(tamanho) or b"{}")

        e = Estado(id=corpo.get("id", "desconhecida"), texto="")
        e.hipotese = corpo.get("hipotese", {})
        e.aprovacoes = corpo.get("aprovacoes", [])
        e = juridico(e, config={"detalhe": DETALHE})
        self._responder(200, e.tipificacao_proposta)

    def _responder(self, codigo: int, corpo: dict) -> None:
        dados = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(dados)))
        self.end_headers()
        self.wfile.write(dados)

    def log_message(self, formato: str, *args) -> None:   # silencia o log padrão do http.server
        pass


def main() -> None:
    porta = int(os.environ.get("PORTA", "8080"))
    print(f"servidor juridico ouvindo em :{porta} (DETALHE={DETALHE})")
    HTTPServer(("0.0.0.0", porta), Handler).serve_forever()


if __name__ == "__main__":
    main()
