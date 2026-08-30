# MCP de verdade (SDK oficial)

O mesmo servidor da Aula 3, agora com o pacote `mcp` (FastMCP). Serve para ver
que o lab principal (`app/servidor_mcp.py`) tem a mesma forma do protocolo real.

```bash
pip install -r ../requirements-opcionais.txt
python mcp_real/cliente.py      # sobe servidor.py via stdio e o consulta
```

> A API do SDK muda entre versões maiores (1.x usa `FastMCP`; 2.x renomeou para
> `MCPServer`). O `requirements-opcionais.txt` está pinado em `mcp>=1.2,<2`.
> Se o import falhar, o conceito continua no lab principal — este diretório é só
> a "prova real".

O que muda em relação ao lab mínimo:

| Lab mínimo (`app/`) | SDK oficial (`mcp_real/`) |
|---|---|
| chamada de método Python direta | JSON-RPC 2.0 sobre **stdio** (processos separados) |
| `ServidorMCP.atender()` | `initialize` + `list_tools` + `call_tool` + `read_resource` |
| escopo/auditoria embutidos | você acrescenta (o SDK dá os ganchos) |
| `FerramentaSpec` (nosso) | schema derivado da assinatura + docstring |
