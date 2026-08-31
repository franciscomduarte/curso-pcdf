# Aula 4 — Engenharia de Agent Loops (SIGMA)

> **Todos os dados são fictícios e destinados exclusivamente ao treinamento.**

O loop que decide, a cada passo, se o agente consulta mais, se já tem o
suficiente, ou se desiste. Ciclo **Percepção → Planejamento → Decisão → Ação →
Observação**, padrão **ReAct**, e todos os critérios de parada num lugar só.

## Laboratório (offline, só a stdlib + python-dotenv)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

python main.py                     # o loop monta uma linha do tempo, reagindo às observações
python main_limites.py             # cada critério de parada, disparado de propósito
python solucao_exercicios.py       # todos os labs (ou: basico | sem-progresso | intermediario | desafio)
pytest -q                          # 11 testes, offline
```

Sem `OPENAI_API_KEY`, usa o `MockReAct` (roteiro reativo, determinístico).

## Estrutura

```
app/
├── barramento.py       # Barramento + Auditor (versão enxuta da Aula 2, p/ o evento de encerramento)
├── orcamento.py        # Orcamento + MotivoParada: passos, chamadas, custo, tempo, repetição
├── ferramentas.py      # REGISTRO de ferramentas (com custo e flag sensivel) + uma instável
├── llm.py              # LLMReAct (Protocol) · MockReAct (reativo) · OpenAIReAct
├── loop.py             # LoopReAct: o ciclo P-P-D-A-O; Autonomia; retry com backoff
└── bases_sinteticas.py # dados fictícios
main.py · main_limites.py · solucao_exercicios.py · tests/
```

## O que cada peça demonstra

| Arquivo | Conceito da Aula 4 |
|---|---|
| `loop.py` | as 5 fases explícitas; a decisão "agir ou encerrar" a cada volta |
| `orcamento.py` | por que um agente sem trava é perigoso — 5 formas de terminar |
| `llm.py` (`MockReAct`) | REAGIR à observação: só busca o documento se o veículo consta alerta |
| `Autonomia` (loop.py) | supervisionado / limitado / autônomo — quanto o agente decide sozinho |
| `_executar_com_retry` | falha transitória ≠ erro de argumento; backoff; limite de tentativas |

## Riscos em produção (discussão)

- **Loop infinito / custo descontrolado**: sem `custo_max`, `max_chamadas` e
  timeout, um agente confuso gasta até o orçamento acabar. Todos são obrigatórios.
- **Parsing frágil do ReAct em texto**: aqui o passo é um dict; um traço ReAct
  em texto livre quebra quando o modelo foge do formato (dor da Aula 1).
- **Autonomia alta sem necessidade**: rodar `AUTONOMO` quando `LIMITADO`
  resolveria remove a chance de o humano barrar uma ação ruim.
- **Retry cego**: repetir uma chamada com argumento inválido não adianta —
  distinga erro transitório de erro determinístico.
