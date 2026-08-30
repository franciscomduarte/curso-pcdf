# Aula 5 — Padrões de Orquestração (SIGMA)

> **Todos os dados são fictícios e destinados exclusivamente ao treinamento.**

Cinco padrões coordenando os **mesmos** especialistas (extrator, classificador,
consultor, revisor) na **mesma** ocorrência — para comparar custo, latência e
complexidade de verdade, não no quadro.

## Laboratório (offline, só a stdlib + python-dotenv)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

python main.py supervisor           # roda 1 padrão e mostra o dossiê + métricas
python main.py pipeline PCDF-SIM-0009
python main_comparar.py             # os 4 padrões de fluxo + debate, lado a lado
python main_comparar.py PCDF-SIM-0009   # ocorrência trivial: veja o supervisor economizar
python solucao_exercicios.py
pytest -q                           # 13 testes, offline
```

Sem `OPENAI_API_KEY`, o Supervisor e o Debate usam o `MockLLM` (determinístico).

## Estrutura

```
app/
├── especialistas.py    # Dossie + os 4 especialistas + SpecEspecialista (precisa/produz)
├── barramento.py       # Barramento + Auditor (versão enxuta da Aula 2)
├── metricas.py         # contadores: especialistas, llm, ferramentas, custo, rodadas, latência
├── llm.py              # MockLLM (decidir p/ supervisor; opinar/julgar p/ debate) + OpenAILLM
└── padroes/
    ├── pipeline.py     # ordem fixa
    ├── supervisor.py   # um LLM decide o próximo especialista (loop da Aula 4)
    ├── broker.py       # despacha PEDIDOS por capacidade; resolve dependências
    ├── blackboard.py   # quadro compartilhado; cada um contribui quando pode
    └── debate.py       # N debatedores + rodadas + juiz, para uma sub-decisão ambígua
main.py · main_comparar.py · solucao_exercicios.py · tests/
```

## O que a comparação mostra

| | pipeline | supervisor | broker | blackboard | debate |
|---|---|---|---|---|---|
| decide o fluxo | você (fixo) | um LLM | ninguém (roteia pedidos) | emergente (pré-condições) | — (sub-decisão) |
| chamadas de LLM extra | 0 | +1 por decisão | 0 | 0 | N × rodadas + 1 |
| adapta ao caso | não | sim | parcial | sim | — |
| fácil de depurar | muito | médio (1 ponto de decisão) | médio | difícil | médio |
| acrescentar especialista | mexe na ordem | mexe no prompt | registra capacidade | só declara `precisa`/`produz` | — |
| ponto único de falha | não | **sim (o supervisor)** | sim (o broker) | não | o juiz |

Na ocorrência **complexa** os quatro dão o mesmo resultado; o supervisor gasta
mais LLM à toa. Na **trivial**, o supervisor pula o consultor (esp=3, tools=0) —
a adaptação passa a compensar quando as ferramentas puladas são caras.

## Riscos em produção (discussão)

- **Supervisor/Broker = ponto único de falha e de decisão**: se ele erra ou cai,
  o sistema inteiro para. Precisa de observabilidade e fallback.
- **Blackboard sem controlador**: dois especialistas podem escrever no mesmo
  campo; ordem não determinística dificulta auditoria. Aqui a ordem é estável de
  propósito.
- **Debate**: custo cresce rápido (N debatedores × R rodadas); só onde a
  ambiguidade justifica. Debatedores podem convergir para o erro (viés de grupo).
- **Nenhum padrão decide o caso** — todos produzem rascunho para revisão humana.
