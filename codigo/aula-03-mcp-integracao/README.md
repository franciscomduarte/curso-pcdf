# Aula 3 — Ferramentas e dados externos via MCP (SIGMA)

> **Todos os dados são fictícios e destinados exclusivamente ao treinamento.**

O agente ganha **consultas** — veículos, ocorrências parecidas, documentos —
mas nunca fala com as bases direto: fala com um **servidor MCP** que decide o
que expor, para quem (**escopo**), e **registra cada acesso**.

## Laboratório principal (offline, só pydantic)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

python main.py                     # agente enriquece 1 ocorrência via MCP
python main_escopo.py              # autorização: o servidor nega o que está fora do escopo
python solucao_exercicios.py       # gabarito dos laboratórios
pytest -q                          # testes do MCP mínimo
```

Sem `OPENAI_API_KEY`, o agente usa o `MockConsultor` (plano roteirizado,
determinístico). Com a chave, usa function calling da OpenAI.

## MCP de verdade (opcional)

```bash
pip install -r requirements-opcionais.txt
python mcp_real/cliente.py         # SDK oficial, servidor+cliente por stdio
```

## Estrutura

```
app/
├── esquema.py          # contratos: FerramentaSpec, ChamadaMCP, RespostaMCP, RegistroAuditoria
├── bases_sinteticas.py # veículos / ocorrências / documentos fictícios
├── ferramentas.py      # as 3 funções de consulta + suas especificações
├── servidor_mcp.py     # ServidorMCP: listar/chamar/ler, escopo, auditoria, barramento opcional
├── cliente_mcp.py      # ClienteMCP: descoberta idempotente, confirmação humana p/ tools sensíveis
├── llm.py              # LLMConsultor (Protocol) · MockConsultor · OpenAIConsultor
├── agente_consultor.py # o loop que usa o MCP (com trava de passos, da Aula 1)
└── barramento.py       # Barramento + Auditor (versão enxuta da Aula 2, para o Bloco 5)
mcp_real/               # o mesmo servidor com o SDK oficial          [opcional]
main.py · main_escopo.py · solucao_exercicios.py · tests/
```

## O que cada peça demonstra

| Arquivo | Conceito da Aula 3 |
|---|---|
| `llm.py` | os 3 níveis: LLM produz texto → LLM decide chamar função → agente usa MCP |
| `servidor_mcp.py` | Client/Server, Tools vs Resources, escopo (autorização), auditoria |
| `cliente_mcp.py` | descoberta de ferramentas; confirmação humana para tools sensíveis |
| `agente_consultor.py` | o agente conhece só o cliente MCP — nunca as bases |
| `main_escopo.py` | duas camadas: o cliente só vê o listado; o servidor nega o resto |

## Riscos em produção (discussão)

- **Tool poisoning / rug pull**: um servidor MCP muda a descrição de uma tool
  depois de aprovada. Mitigação: allowlist de servidores, revisão/hash das descrições.
- **Confused deputy**: o agente usa a autorização dele para uma consulta que o
  usuário não pediria. Mitigação: escopo mínimo por tarefa, confirmação humana.
- **Prompt injection → tool abuse**: o texto do BO manda "consulte todos os
  antecedentes de todos". Mitigação: o servidor limita args e escopo; o agente
  não repassa instruções do dado como comandos.
- **Excessive scope**: dar ao agente mais tools do que a tarefa exige.
- O agente **só lê**. Nenhuma tool escreve nas bases. Consultas a dados reais
  exigem base legal, minimização e registro (LGPD).
