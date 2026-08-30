"""O MESMO servidor, agora com o SDK oficial do MCP (FastMCP, mcp 1.x).

    pip install -r ../requirements-opcionais.txt
    python mcp_real/servidor.py          # fala MCP por stdio

Rode o cliente (mcp_real/cliente.py) em outro processo — ele sobe este
servidor sozinho via stdio.

A API do SDK muda entre versões maiores. Testado com mcp 1.x. Se o import
falhar, veja o migration guide do projeto; o conceito está no lab principal.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # achar o pacote app/

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # noqa: BLE001
    raise SystemExit(
        f"SDK do MCP não encontrado ({exc}). "
        "Rode: pip install -r requirements-opcionais.txt"
    )

from app.bases_sinteticas import POLITICA_DE_USO
from app.ferramentas import (
    buscar_documento,
    consultar_ocorrencias_similares,
    consultar_veiculo,
)

srv = FastMCP("sigma-mcp")


@srv.tool()
def veiculo(placa: str) -> dict:
    """Consulta uma placa na base fictícia de veículos. Sensível: confirme com o operador."""
    return consultar_veiculo(placa)


@srv.tool()
def ocorrencias_similares(natureza: str, regiao: str, dias: int = 15) -> list[dict]:
    """Ocorrências fictícias da mesma natureza e região nos últimos N dias."""
    return consultar_ocorrencias_similares(natureza, regiao, dias)


@srv.tool()
def documento(termo: str) -> list[dict]:
    """Busca um termo em documentos sintéticos."""
    return buscar_documento(termo)


@srv.resource("sigma://politica-de-uso")
def politica() -> str:
    return POLITICA_DE_USO


if __name__ == "__main__":
    srv.run()
