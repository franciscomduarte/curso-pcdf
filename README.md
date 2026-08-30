# Curso PCDF — Unidade 8: Sistemas Multiagentes em Segurança Pública

Material da unidade **Sistemas Multiagentes em Segurança Pública** (50h, 70% prática),
para servidores da Polícia Civil do Distrito Federal. Aulas em HTML estático +
código Python de exemplo. Todos os dados são **sintéticos**.

**Prof. Francisco Molina Jr**

## Como ver

Abra `index.html` no navegador (ou publique via GitHub Pages).
As aulas ficam em `aulas/` e compartilham o mesmo tema (`assets/`).

## Estrutura

```
curso-pcdf/
├── index.html                       # índice das 10 aulas (4 blocos)
├── assets/
│   ├── estilo.css                   # sistema de design (navy / ouro / teal)
│   ├── aula.js                      # progresso de rolagem, reveal, realçador Python, Mermaid
│   └── logo-pcdf.png                # brasão oficial da PCDF
├── aulas/
│   ├── _modelo-aula.html            # esqueleto reutilizável (base das Aulas 3–10)
│   ├── aula-01-fundamentos.html     # ✅ pronta
│   ├── aula-02-comunicacao-a2a.html # ✅ pronta
│   ├── aula-03-mcp-integracao.html  # ✅ pronta
│   ├── aula-04-agent-loops.html     # ✅ pronta
│   ├── aula-05-orquestracao.html    # ✅ pronta
│   ├── aula-06-grafos-langgraph.html # ✅ pronta
│   └── aula-07-especializados-hitl.html # ✅ pronta
└── codigo/
    ├── aula-01-extrator-ocorrencias/ # código da Aula 1 (roda offline, sem chave)
    ├── aula-02-comunicacao-a2a/      # código da Aula 2 (pub/sub offline; MQTT/gRPC opcionais)
    ├── aula-03-mcp-integracao/       # código da Aula 3 (MCP mínimo offline; SDK oficial opcional)
    ├── aula-04-agent-loops/          # código da Aula 4 (loop ReAct offline)
    ├── aula-05-orquestracao/         # código da Aula 5 (os 5 padrões + comparação, offline)
    ├── aula-06-grafos-langgraph/      # código da Aula 6 (motor de grafo mínimo; LangGraph opcional)
    └── aula-07-especializados-hitl/   # código da Aula 7 (agentes com papel + HITL/checkpoint, offline)
```

## Ementa (10 aulas de 5h)

| # | Aula | Bloco |
|---|---|---|
| 1 | Fundamentos de Agentes e Engenharia Básica | A · Fundamentos e comunicação |
| 2 | Protocolos de Comunicação Agente-a-Agente (A2A) | A |
| 3 | Model Context Protocol (MCP) e Integração | A |
| 4 | Engenharia de Agent Loops (ReAct) | B · Coordenação e orquestração |
| 5 | Padrões de Orquestração Multiagente | B |
| 6 | Modelagem de Sistemas Baseados em Grafos (LangGraph) | B |
| 7 | Agentes Especializados e Human-in-the-Loop | C · Especialização e operação |
| 8 | Arquitetura Distribuída e Deploy com Kubernetes | C |
| 9 | Auto-scaling, Observabilidade e Segurança | C |
| 10 | Projeto Integrador e Estudo de Caso | D · Integração |

Fio condutor: o sistema fictício **SIGMA**, construído incrementalmente aula a aula.

## Stack

Python · OpenAI API · Pydantic · (aulas seguintes) MQTT, gRPC, MCP, LangGraph,
Docker, Kubernetes, OpenTelemetry, Prometheus, Grafana.

Os laboratórios rodam **sem chave de API**: quando `OPENAI_API_KEY` não está
definida, um LLM falso e determinístico (`MockExtrator`) assume.

## Rodar o código

Cada aula tem sua pasta em `codigo/`. Padrão:

```bash
cd codigo/aula-01-extrator-ocorrencias   # ou aula-02-comunicacao-a2a
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q                          # testes rodam sem chave/broker
```

- **Aula 1:** `python main.py` · `python main_lote.py`
- **Aula 2:** `python main_local.py` (offline). MQTT (`main_mqtt.py`) e gRPC
  (`grpc_demo/`) são opcionais — ver o README da pasta.
- **Aula 3:** `python main.py` · `python main_escopo.py` (offline). O MCP com o
  SDK oficial (`mcp_real/`) é opcional.
- **Aula 4:** `python main.py` · `python main_limites.py` (offline).
- **Aula 5:** `python main_comparar.py` · `python main.py <padrão>` (offline).
- **Aula 6:** `python main.py` · `python main_ciclo.py` (offline).
- **Aula 7:** `python main.py` · `python main_retomar.py iniciar` (offline).

## Publicar no GitHub Pages

Settings → Pages → Branch `main` / `/root`. Fica em
`https://franciscomduarte.github.io/curso-pcdf/`.

## Status

- [x] Aula 1 — Fundamentos de Agentes
- [x] Aula 2 — Comunicação Agente-a-Agente (A2A)
- [x] Aula 3 — Model Context Protocol (MCP) e Integração
- [x] Aula 4 — Engenharia de Agent Loops
- [x] Aula 5 — Padrões de Orquestração Multiagente
- [x] Aula 6 — Modelagem de Sistemas Baseados em Grafos
- [x] Aula 7 — Agentes Especializados e Human-in-the-Loop
- [ ] Aulas 8 a 10 — geradas uma por vez, a partir de `aulas/_modelo-aula.html`
