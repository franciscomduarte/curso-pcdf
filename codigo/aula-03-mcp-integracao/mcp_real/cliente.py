"""Cliente MCP com o SDK oficial — sobe o servidor via stdio e o consulta.

    pip install -r ../requirements-opcionais.txt
    python mcp_real/cliente.py
"""

from __future__ import annotations

import asyncio
from pathlib import Path

try:
    from mcp.client.session import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client
except ImportError as exc:  # noqa: BLE001
    raise SystemExit(f"SDK do MCP não encontrado ({exc}). Instale requirements-opcionais.txt")

SERVIDOR = str(Path(__file__).with_name("servidor.py"))


async def main() -> None:
    params = StdioServerParameters(command="python", args=[SERVIDOR])
    async with stdio_client(params) as (leitura, escrita):
        async with ClientSession(leitura, escrita) as sessao:
            await sessao.initialize()

            ferramentas = await sessao.list_tools()
            print("ferramentas:", [t.name for t in ferramentas.tools])

            r = await sessao.call_tool("veiculo", {"placa": "ABC1D23"})
            print("veiculo(ABC1D23):", r.content[0].text)

            r = await sessao.call_tool(
                "ocorrencias_similares",
                {"natureza": "Furto", "regiao": "Asa Norte", "dias": 15},
            )
            print("similares:", r.content[0].text)

            pol = await sessao.read_resource("sigma://politica-de-uso")
            print("politica:", pol.contents[0].text[:60], "...")


if __name__ == "__main__":
    asyncio.run(main())
